# The computing Thread/Deamon
from daemon import runner
from threading import Thread
from . import *
from rrc.main.storing import *
import time
import yaml
import json
from sqlalchemy_pagination import paginate
import docker
import os
import shutil

## ToDo: Improve code reduction by writing a contract synchronizer from dict to sqlachemy.

class Computing(Thread):
    """docstring for ."""
    def __init__(self):
        super(Computing, self).__init__()
        self.setName('RRC-Networking')
        self.daemon = False
        self.localhost = True
        self.base_path = "/tmp/rrc"
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def connect(self):
        self.localhost = False

    def connected(self):
        return not self.localhost

    def queu(self): #maximum of 10 contract at a time.
        xprint('Computing', 'deb', 'Fetching all the queued contracts')
        session = self.storing.hook("Computing")
        queus = {'list':[], 'size':0}
        ## Access in between
        for qu in session.query(Queu).all():
            queus['list'].append(qu.dict())
        queus['size'] = len(queus['list'])
        self.storing.release("Computing")
        xprint('Computing', 'inf', '\n{0}.'.format(json.dumps(queus, sort_keys=True, indent=4)))

    def contracts(self, page):
        xprint('Computing', 'deb', 'Fetching all contracts list on page [{0}].'.format(page))
        session = self.storing.hook("Computing")
        ## Access in between
        cntrs = {'list':[], 'size':0, 'pages': 0}
        cnts = session.query(Contract).all()
        pagination = paginate(session.query(Contract), 1, 10)
        pages = pagination.pages
        if pages > 0:
            if page > pages:
                cnts = paginate(session.query(Contract), pages, 10).items
            elif page < 1:
                cnts = pagination.items
            else:
                cnts = paginate(session.query(Contract), page, 10).items

            for cntr in cnts:
                cntrs['list'].append(cntr.dict())

            cntrs['size'] = pagination.total
            cntrs['pages'] = pages
        self.storing.release("Computing")
        xprint('Computing', 'inf', '\n{0}.'.format(json.dumps(cntrs, sort_keys=True, indent=4)))

    def submit(self, cntr_path):
        # Load contract from path.
        xprint('Computing', 'deb', 'Requesting the computation of contract file [{0}].'.format(cntr_path))
        ts = time.gmtime()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        session = self.storing.hook("Computing")
        contract = {}
        try:
            stream = open(cntr_path, 'r')
            contract = yaml.load(stream)
        except Exception as e:
            # pass
            xprint('Computing', 'err', 'Error: {0}.'.format(e))

        if len(contract) == 0:
            xprint('Computing', 'err', 'Error: Unable to find a contract at path: [{0}].'.format(cntr_path))
            return

        # To avoid global_id collisions in localhost.
        # We auto-generate the sha-256 ids here.
        if self.connected():
            global_id = contract['id']
            user = contract['user']
        else:
            global_id = self.storing.gen_id()
            user = self.storing.gen_id()

        xprint('Computing', 'inf', 'Requesting the computation of contract [{0}].'.format(global_id))

        status = 'added'
        reward = float(contract.get('reward', 0))

        inputs = json.dumps(contract.get('inputs', {})).replace("\"","'")
        outputs = json.dumps(contract.get('outputs', {})).replace("\"","'")

        digests_container = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        digests_inputs = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        digests_outputs = json.dumps({}).replace("\"","'")

        gpu = contract.get('gpu', False)

        bounds = contract.get('bounds', None)
        if bounds:
            bounds_cpu = bounds['cpu']
            bounds_gpu = bounds['gpu']
            bounds_mem = bounds['memory']
            bounds_bdw = bounds['bandwith']

        added = timestamp
        ready = 'xxxx-xx-xx xx:xx:xx'
        failure = 'xxxx-xx-xx xx:xx:xx'
        running = 'xxxx-xx-xx xx:xx:xx'
        processed = 'xxxx-xx-xx xx:xx:xx'
        canceled = 'xxxx-xx-xx xx:xx:xx'

        assess = contract.get('assess', None)
        if assess:
            assess_scope = assess['scope'] # reproducible, repeatable, replicable
            assess_outputs = json.dumps(assess['outputs']).replace("\"","'")

        container = contract.get('container', None)
        if container:
            container_digest = container['digest']
            container_repo = container['repository']

        logs = json.dumps([]).replace("\"","'")
        current_contract = Contract(identifier=global_id,user=user,status=status,reward=reward,inputs=inputs,outputs=outputs,gpu=gpu,logs=logs,added=added,ready=ready,failure=failure,running=running,processed=processed,canceled=canceled)
        current_contract.digests_container = digests_container
        current_contract.digests_inputs = digests_inputs
        current_contract.digests_outputs = digests_outputs
        current_contract.bounds_cpu = bounds_cpu
        current_contract.bounds_gpu = bounds_gpu
        current_contract.bounds_mem = bounds_mem
        current_contract.bounds_bdw = bounds_bdw
        current_contract.assess_scope = assess_scope
        current_contract.assess_outputs = assess_outputs
        current_contract.container_digest = container_digest
        current_contract.container_repo = container_repo
        current_contract.logs = logs
        session.add(current_contract)
        session.commit()
        self.storing.release("Computing")

    def cancel(self, contract):
        xprint('Computing', 'inf', 'Requesting the cancelation of contract [{0}].'.format(contract))
        session = self.storing.hook("Computing")

        current_contract = session.query(Contract).filter(Contract.global_id == contract).first()
        if current_contract:
            current_queu = session.query(Queu).filter(Queu.contract_id == current_contract.id).first()
            if current_queu:
                session.delete(current_queu)
            session.delete(current_contract)
            session.commit()
            xprint('Computing', 'inf', 'Contract [{0}] cancelled.'.format(contract))
        else:
            xprint('Computing', 'err', 'Unable to find contract [{0}].'.format(contract))
        # Cancel only work in localhost.
        self.storing.release("Computing")

    def show(self, contract):
        xprint('Computing', 'inf', 'Requesting details on contract [{0}].'.format(contract))
        session = self.storing.hook("Computing")
        ## Access in between
        current_contract = session.query(Contract).filter(Contract.global_id == contract).first()
        if current_contract:
            xprint('Computing', 'inf', '\n{0}'.format(contract))
        else:
            xprint('Computing', 'err', 'Unable to find contract [{0}].'.format(contract))
        self.storing.release("Computing")

    def link_storage(self, storing=None):
        self.storing = storing

    def process(self, request):
        xprint('Computing', 'deb', 'Processing request...')
        if request['type'] == "jobs":
            # See which job is done.
            # If done remove it from the list and update the db accordingly.
            request['jobs'] = self.post_exec(request['jobs'])
            queu_size = len(request['jobs'])
            available = 10 - queu_size
            if available > 0:
                # Later update.
                # Order here by most rewarding first.
                idx = 0
                for cntr in request['contracts']:
                    ts = time.gmtime()
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)

                    session = self.storing.hook("Computing")
                    cntr_object = session.query(Contract).filter(Contract.identifier == cntr["id"]).first()
                    queu = Queu(contract=cntr_object, scheduled=timestamp, processed="xxxx-xx-xx xx:xx:xx", status="fetching")
                    session.add(queu)
                    session.commit()
                    cntr["queu"] = queu.id
                    self.storing.release("Computing")

                    job = self.pre_exec(cntr)
                    if not self. connected():
                        self._exec(job)

                    idx += 1
                    if idx > available:
                        break
            else:
                xprint('Computing', 'deb', 'Queu is full. Moving on...')
        elif request['type'] == "received":
            xprint('Computing', 'deb', 'Checking received comm: {0}'.format(request['comm']))
        elif request['type'] == "sent":
            xprint('Computing', 'deb', 'Checking sent comm: {0}'.format(request['comm']))

    def pre_exec(self, contract):
        xprint('Computing', 'inf', 'Prexecuting contract [{0}]'.format(contract['id']))
        # Load the image and all the files and prepare
        # Update queu state.
        # Move contract to queu
        session = self.storing.hook("Computing")
        queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
        cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
        cntr_object.status = "preparing"
        queu.status = "scheduled"
        session.commit()
        self.storing.release("Computing")

        if not os.path.exists("{0}/{1}".format(self.base_path, contract["id"])):
           os.makedirs("{0}/{1}".format(self.base_path, contract["id"]))
        else:
           xprint("Computing", "deb", "Cleaning up previous files from job[{0}] execution. There shouldn't be any.".format(contract["id"]))
           shutil.rmtree("{0}/{1}".format(self.base_path, contract["id"]))
           os.makedirs("{0}/{1}".format(self.base_path, contract["id"]))

        session = self.storing.hook("Computing")
        queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
        queu.status = "preparing"
        session.commit()
        self.storing.release("Computing")

        # Fetch the contract and update the assess outputs.
        if contract['assess']['scope'] == "replicable":
            # xprint("Computing", "warn", "Replicable.")
            session = self.storing.hook("Computing")
            # try:
            blk = session.query(Block).filter(Block.contract_global_id == contract["assess"]["outputs"]).first()
            if blk:
                contract['assess']['outputs'] = json.loads(blk.contract.assess_outputs.replace("\'", "\""))
                # xprint("Computing", "warn", "Replicate assess output: {0}".format(json.dumps(blk.contract.assess_outputs)))
                cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
                cntr_object.assess_outputs = json.dumps(contract['assess']['outputs']).replace("\"", "\'")
                session.commit()
            else:
                contract['status'] = 'failed'
                ts = time.gmtime()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                contract['timestamps']['failure'] = timestamp
                contract['logs'].append("RRC Computing >> Error: Unable to find the replicated contract [{0}].".format(contract["assess"]["outputs"]))
                queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
                cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
                cntr_object.status = "failed"
                cntr_object.failure = timestamp
                cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
                queu.status = "failed"
                queu.processed = timestamp
                session.commit()
            # except:
            #     contract['status'] = 'failed'
            #     ts = time.gmtime()
            #     timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            #     contract['timestamps']['failure'] = timestamp
            #     contract['logs'].append("RRC Computing >> Error: An issue occured with the replicable contract referenced.")
            #     queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
            #     cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
            #     cntr_object.status = "failed"
            #     cntr_object.failure = timestamp
            #     cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
            #     queu.status = "failed"
            #     queu.processed = timestamp
            #     session.commit()
            self.storing.release("Computing")

        if len(contract['inputs']) != 0:
            try:
               filename, tmp_destination = get_file(contract['inputs']['location'], contract["id"])
               tmp_location = "{0}/{1}".format(tmp_destination, filename)
               digest = sha256_digest(tmp_location)
               if unpack(filename, tmp_destination):
                   os.remove(tmp_location)
               contract['digests']['inputs'] = digest
               xprint("Computing", "warn", "Inputs Digest: {0}".format(digest))

               session = self.storing.hook("Computing")
               cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
               cntr_object.digests_inputs = digest
               session.commit()
               self.storing.release("Computing")

               if contract['inputs']['digest'] == contract['digests']['inputs']:
                   xprint("Computing", "deb", "Fetched inputs matches with the expectations.")
                   contract['inputs']['origin'] = "{0}/{1}".format(tmp_destination, filename.split(".")[0])

                   session = self.storing.hook("Computing")
                   cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
                   cntr_object.inputs = json.dumps(contract['inputs']).replace("\"", "\'")
                   cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
                   session.commit()
                   self.storing.release("Computing")
               else:
                   contract['status'] = 'failed'
                   ts = time.gmtime()
                   timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                   contract['timestamps']['failure'] = timestamp
                   contract['logs'].append("RRC Computing >> Error: Fetched inputs {0} does not comply with hard expectations.".format(contract['inputs']['location']))

                   session = self.storing.hook("Computing")
                   queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
                   cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
                   cntr_object.status = "failed"
                   cntr_object.failure = timestamp
                   cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
                   queu.status = "failed"
                   queu.processed = timestamp
                   session.commit()
                   self.storing.release("Computing")
                   ## Communicate with networking to inform that the node cannot run the contract.

                   return contract
            except Exception as e:
                contract['status'] = 'failed'
                ts = time.gmtime()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                contract['timestamps']['failure'] = timestamp
                contract['logs'].append("RRC Computing >> Error: Unable to fetch specified inputs: {0}.".format(contract['inputs']['location']))
                contract['logs'].append( "RRC Computing >> Exception: {0}".format(str(e)))

                session = self.storing.hook("Computing")
                queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
                cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
                cntr_object.status = "failed"
                cntr_object.failure = timestamp
                cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
                queu.status = "failed"
                queu.processed = timestamp
                session.commit()
                self.storing.release("Computing")
                ## Communicate with networking to inform that the node cannot run the contract.

                return contract

        if len(contract['outputs']) != 0:
            xprint("Computing", "deb", "Job expected output has been registered.")
            contract['outputs']['origin'] = "{0}/{1}/{2}".format(self.base_path, contract["id"], contract['outputs']['volume'].split("/")[-1])

            session = self.storing.hook("Computing")
            cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
            cntr_object.outputs = json.dumps(contract['outputs']).replace("\"", "\'")
            cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
            session.commit()
            self.storing.release("Computing")
        else:
            contract['status'] = 'failed'
            ts = time.gmtime()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            contract['timestamps']['failure'] = timestamp
            contract['logs'].append("RRC Computing >> Error: A job should have an expected output.")

            session = self.storing.hook("Computing")
            queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
            cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
            cntr_object.status = "failed"
            cntr_object.failure = timestamp
            cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
            queu.status = "failed"
            queu.processed = timestamp
            session.commit()
            self.storing.release("Computing")
            ## Communicate with networking to inform that the node cannot run the contract.

        try:
           # Docker pull the container
           client = docker.from_env()
           image_tag = "{0}:latest".format(contract['container']['repository'])
           exists = False
           for container in client.containers.list():
               if image_tag in container.image.tags:
                   if container.status == "exited":
                       exists = True
                       container.remove()

           for image in client.images.list():
               if image_tag in image.tags:
                   exists = True
                   # client.images.remove(image_tag)
           if not exists:
               image = client.images.pull(image_tag)
           else:
               image = client.images.get(image_tag)

           contract['digests']['container'] = image.id.split(":")[1]

           session = self.storing.hook("Computing")
           cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
           cntr_object.digests_container = contract['digests']['container']
           cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
           session.commit()
           self.storing.release("Computing")

           xprint("Computing", "deb", contract['digests']['container'])
           if self.connected():
               session = self.storing.hook("Computing")
               comm = Communication(sender="computing", receiver="networking", function="contract:ready", request=json.dumps(contract).replace("\"","\'"))
               session.add(comm)
               session.commit()
               self.storing.release("Computing")

               return contract
           else:
               # If localhost just check that the digest is the specified one.
               # If as expected, the node will be allowed in the ready state.
               if contract['container']['digest'] == contract['digests']['container']:
                   xprint("Computing","db", "Pulled container digest matches.")
                   contract['status'] = 'ready'
                   ts = time.gmtime()
                   timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                   contract['timestamps']['ready'] = timestamp

                   session = self.storing.hook("Computing")
                   cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
                   cntr_object.status = "ready"
                   cntr_object.ready = timestamp
                   cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
                   session.commit()
                   self.storing.release("Computing")
                   return contract
               else:
                   contract['status'] = 'failed'
                   ts = time.gmtime()
                   timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                   contract['timestamps']['failure'] = timestamp
                   contract['logs'].append("RRC Computing >> Error: Pulled container {0} does not comply with hard expectations.".format(job['container']['repository']))

                   session = self.storing.hook("Computing")
                   queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
                   cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
                   cntr_object.status = "failed"
                   cntr_object.failure = timestamp
                   cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
                   queu.status = "failed"
                   queu.processed = timestamp
                   session.commit()
                   self.storing.release("Computing")

                   return contract
        except Exception as e:
           contract['status'] = 'failed'
           ts = time.gmtime()
           timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
           contract['timestamps']['failure'] = timestamp
           contract['logs'].append("RRC Computing >> Error: Unable to fetch the container: {0}".format(contract['container']['repository']))
           contract['logs'].append("RRC Computing >> Exception: {0}".format(str(e)))

           session = self.storing.hook("Computing")
           queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
           cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
           cntr_object.status = "failed"
           cntr_object.failure = timestamp
           cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
           queu.status = "failed"
           queu.processed = timestamp
           session.commit()
           self.storing.release("Computing")

           return contract

    def launch_job(self, contract):
        client = docker.from_env()
        image_tag = "{0}:latest".format(contract['container']['repository'])

        volumes = {}
        volumes[contract['inputs']['origin']] = {'bind':contract['inputs']['volume'], 'mode': 'ro'}
        volumes[contract['outputs']['origin']] = {'bind':contract['outputs']['volume'], 'mode': 'rw'}

        container = client.containers.run(image_tag, volumes=volumes, detach=True)

        session = self.storing.hook("Computing")
        queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
        cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
        cntr_object.container_id = container.id
        queu.container = container.id
        session.commit()
        self.storing.release("Computing")

        contract['job'] = container.id
        return contract

    def cache_outputs(self, job, scope): #scope original or compared
        filename =  job['outputs']['origin'].split("/")[-1]
        destination = job['outputs']['origin'].split("/{0}".format(filename))[0]
        folder_path = "{0}/{1}".format(destination, filename)
        base_dir = os.path.abspath(folder_path)
        base_path = os.path.normpath("{0}".format(destination))
        if job['assess']['scope'] in ['reproducible', 'repeatable', 'replicable']:
            for dirpath, dirnames, filenames in os.walk(base_dir):
                for name in filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    if os.path.isfile(path):
                        if scope == "original":
                            job['assess']['outputs'][os.path.relpath(path, base_path)] = sha256_digest(path)
                            # xprint("Computing", "warn", "Assess outputs: {0}".format(json.dumps(job, sort_keys=True, indent=4)))
                        elif scope == "compared":
                            job['digests']['outputs'][os.path.relpath(path, base_path)] = sha256_digest(path)
                            # xprint("Computing", "warn", "Digests outputs: {0}".format(json.dumps(job, sort_keys=True, indent=4)))
        return job

    def _exec(self, contract):
        xprint('Computing', 'info', 'Executing contract [{0}].'.format(contract["id"]))
        # Launch the new container in the queu.
        # Update with the container id.

        ts = time.gmtime()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        contract['timestamps']['running'] = timestamp

        session = self.storing.hook("Computing")
        queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
        cntr_object = session.query(Contract).filter(Contract.identifier == contract["id"]).first()
        cntr_object.status = "running"
        cntr_object.running = timestamp
        cntr_object.logs = json.dumps(contract['logs']).replace("\"", "\'")
        queu.status = "running"
        session.commit()
        self.storing.release("Computing")

        if contract['assess']['scope'] == "repeatable":
            contract = self.launch_job(contract)

            session = self.storing.hook("Computing")
            queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
            queu.status = "1/2"
            session.commit()
            self.storing.release("Computing")

            return contract
        elif contract['assess']['scope'] == "reproducible":
            contract = self.launch_job(contract)

            session = self.storing.hook("Computing")
            queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
            queu.status = "2/2"
            session.commit()
            self.storing.release("Computing")

            return contract
        elif contract['assess']['scope'] == "replicable":
            contract = self.launch_job(contract)

            session = self.storing.hook("Computing")
            queu = session.query(Queu).filter(Queu.id == contract["queu"]).first()
            queu.status = "2/2"
            session.commit()
            self.storing.release("Computing")

            return contract
        else:
            ts = time.gmtime()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            contract['timestamps']['processed'] = timestamp
            return contract

    def post_exec(self, jobs):
        to_remove = []
        idx = 0
        client = docker.from_env()
        idx = 0
        for job in jobs:
            xprint('Computing', 'inf', 'Postexecuting contract [{0}].'.format(job['contract']['id']))
            if job['contract']['status'] == "failed":
                # Cleanup the execution and report to the network if connected.
                container = client.containers.get(job['container'])
                if container:
                    container.reload()
                    if container.status != 'exited':
                        container.stop()
                        container.remove()

                session = self.storing.hook("Computing")
                queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                ## ToDo: Move to history.
                session.delete(queu)
                session.commit()
                self.storing.release("Computing")
                to_remove.append(idx)
            elif job['contract']['status'] == "preparing":
                # This is a connected one.
                # Wait for the response to ready function put back the status to ready.
                xprint("Computing", "inf", "Node waiting for network ready response to resume.")
            elif job['contract']['status'] == "ready":
                ## The network responded to say that the node can go on and run it.
                ## Do an _exec here.
                self._exec(job['contract'])
            elif job['contract']['status'] == "cancel":
                ## The network issued a request to terminate the contract.
                container = client.containers.get(job['container'])
                if container:
                    container.reload()
                    if container.status != 'exited':
                        container.stop()
                        container.remove()

                session = self.storing.hook("Computing")
                queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                ## ToDo: Move to history.
                session.delete(queu)
                session.commit()
                self.storing.release("Computing")
                to_remove.append(idx)
            elif job['contract']['status'] == "processed":
                if not self.connected():
                    confirmed = True
                    # xprint("Computing", "warn", job['contract']['assess'])
                    for key in job['contract']['assess']['outputs'].keys():
                        if job['contract']['assess']['outputs'][key] != job['contract']['digests']['outputs'][key]:
                            confirmed = False
                            job['contract']['logs'].append("RRC Computing >> Decision: The assessment is rejected due to a difference found for {0}".format(key))
                            break
                    ts = time.gmtime()
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)

                    container = job['contract']['digests']['container']
                    inputs = job['contract']['digests']['inputs']
                    outputs = json.dumps(job['contract']['digests']['outputs']).replace("\"","\'")
                    scope = job['contract']['assess']['scope']
                    last = True
                    status = "created"
                    created = timestamp
                    validated = "xxxx-xx-xx xx:xx:xx"
                    hooked = "xxxx-xx-xx xx:xx:xx"
                    chained = "xxxx-xx-xx xx:xx:xx"

                    if not confirmed:
                        job['contract']['timestamps']['rejected'] = timestamp
                        session = self.storing.hook("Computing")
                        queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                        current_instance = session.query(Instance).first()
                        nodes = current_instance.identifier
                        cntr_object = session.query(Contract).filter(Contract.identifier == job['contract']["id"]).first()
                        cntr_object.status = "rejected"
                        cntr_object.logs = json.dumps(job['contract']['logs']).replace("\"", "\'")
                        decisions = cntr_object.status
                        reward = cntr_object.reward
                        queu.status = "decision"
                        session.delete(queu)
                        ## ToDo: Move to history.

                        last_blk = session.query(Block).filter(Block.last == True).first()
                        if last_blk:
                            last_blk.last = False
                            last_blk.status = "chained"
                            last_blk.chained = timestamp
                            genesis = False
                            current_block = Block(previous=last_blk.signature, contract_global_id=cntr_object.identifier, contract=cntr_object, container=container, inputs=inputs, outputs=outputs, scope=scope, nodes=nodes, decisions=decisions, reward=reward, last=last, status=status, created=created, validated=validated, hooked=hooked, chained=chained, genesis=genesis)
                        else:
                            genesis = True
                            current_block = Block(contract_global_id=cntr_object.identifier, contract=cntr_object, container=container, inputs=inputs, outputs=outputs, scope=scope, nodes=nodes, decisions=decisions, reward=reward, last=last, status=status, created=created, validated=validated, hooked=hooked, chained=chained, genesis=genesis)

                        session.add(current_block)
                        session.commit()
                        self.storing.release("Computing")
                    else:
                        job['contract']['logs'].append("RRC Computing >> Decision: The submitted assessment has been successfully confirmed! :-)")
                        job['contract']['logs'].append("RRC Computing >> Decision: You will soon be awarded {0} RRC for your effort! :-)".format(job['contract']['reward']))
                        job['contract']['timestamps']['confirmed'] = timestamp
                        session = self.storing.hook("Computing")
                        queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                        current_instance = session.query(Instance).first()
                        nodes = current_instance.identifier
                        cntr_object = session.query(Contract).filter(Contract.identifier == job['contract']["id"]).first()
                        current_instance.rewards +=  job['contract']['reward']
                        cntr_object.status = "confirmed"
                        cntr_object.logs = json.dumps(job['contract']['logs']).replace("\"", "\'")
                        decisions = cntr_object.status
                        reward = cntr_object.reward
                        queu.status = "decision"
                        ## ToDo: Move to history.
                        session.delete(queu)

                        last_blk = session.query(Block).filter(Block.last == True).first()
                        if last_blk:
                            last_blk.last = False
                            last_blk.status = "chained"
                            last_blk.chained = timestamp
                            genesis = False
                            current_block = Block(previous=last_blk.signature, contract_global_id=cntr_object.identifier, contract=cntr_object, container=container, inputs=inputs, outputs=outputs, scope=scope, nodes=nodes, decisions=decisions, reward=reward, last=last, status=status, created=created, validated=validated, hooked=hooked, chained=chained, genesis=genesis)
                        else:
                            genesis = True
                            current_block = Block(contract_global_id=cntr_object.identifier, contract=cntr_object, container=container, inputs=inputs, outputs=outputs, scope=scope, nodes=nodes, decisions=decisions, reward=reward, last=last, status=status, created=created, validated=validated, hooked=hooked, chained=chained, genesis=genesis)

                        session.add(current_block)
                        session.commit()
                        self.storing.release("Computing")

                    session = self.storing.hook("Computing")
                    ts = time.gmtime()
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                    last_blk = session.query(Block).filter(Block.last == True).first()
                    if last_blk:
                        content = last_blk.dict()
                        del content['hash']
                        del content['timestamps']
                        del content['last']
                        del content['status']
                        last_blk.signature = self.storing.digest(json.dumps(content).replace("\"", "\'").encode("utf-8"))
                        last_blk.status = "validated"
                        last_blk.validated = timestamp
                        session.commit()
                    self.storing.release("Computing")

                    session = self.storing.hook("Computing")
                    ts = time.gmtime()
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                    last_blk = session.query(Block).filter(Block.last == True).first()
                    if last_blk:
                        last_blk.status = "hooked"
                        last_blk.hooked = timestamp
                        session.commit()
                    self.storing.release("Computing")

            elif job['contract']['status'] == "confirmed":
                container = client.containers.get(job['container'])
                if container:
                    container.reload()
                    container.remove()

                session = self.storing.hook("Computing")
                queu = session.query(Queu).filter(Queu.id == job["queu"]).first()
                current_instance = session.query(Instance).first()
                # User reward updated online.
                # Should be display next time call owner --summary.
                current_instance.reward +=  job['contract']['reward']
                ## ToDo: Move to history.
                session.delete(queu)
                session.commit()
                self.storing.release("Computing")
                to_remove.append(idx)
            elif job['contract']['status'] == "rejected":
                container = client.containers.get(job['container'])
                if container:
                    container.reload()
                    container.remove()

                session = self.storing.hook("Computing")
                queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                ## ToDo: Move to history.
                session.delete(queu)
                session.commit()
                self.storing.release("Computing")
                to_remove.append(idx)
            elif job['contract']['status'] == "running":
                # Update the execution.
                container = client.containers.get(job['container'])
                if container:
                    xprint('Computing', 'deb', 'Container loaded!')
                    container.reload()
                    if container.status == 'exited':
                        if job['contract']['assess']['scope'] == "repeatable":
                            if job['status'] == "1/2":
                                job['contract'] = self.cache_outputs(job['contract'], "original")
                                job['contract']['queu'] = job['id']
                                job['contract'] = self.launch_job(job['contract'])

                                ts = time.gmtime()
                                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                                job['contract']['timestamps']['processed'] = timestamp

                                session = self.storing.hook("Computing")
                                queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                                cntr_object = session.query(Contract).filter(Contract.identifier == job['contract']["id"]).first()
                                cntr_object.assess_outputs = json.dumps(job['contract']['assess']['outputs']).replace("\"", "\'")
                                cntr_object.logs = json.dumps(job['contract']['logs']).replace("\"", "\'")
                                queu.status = "2/2"
                                session.commit()
                                self.storing.release("Computing")
                            elif job['status'] == "2/2":
                                job['contract'] = self.cache_outputs(job['contract'], "compared")

                                ts = time.gmtime()
                                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                                job['contract']['timestamps']['processed'] = timestamp

                                session = self.storing.hook("Computing")
                                queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                                cntr_object = session.query(Contract).filter(Contract.identifier == job['contract']["id"]).first()
                                cntr_object.status = "processed"
                                cntr_object.processed = timestamp
                                cntr_object.digests_outputs = json.dumps(job['contract']['digests']['outputs']).replace("\"", "\'")
                                cntr_object.logs = json.dumps(job['contract']['logs']).replace("\"", "\'")
                                queu.status = "processed"
                                queu.processed = timestamp
                                session.commit()
                                self.storing.release("Computing")

                                if self.connected():
                                    ## Ask the RRC network to decide based on the current contract content.
                                    session = self.storing.hook("Computing")
                                    comm = Communication(sender="computing", receiver="networking", function="contract:decision", request=json.dumps(contract).replace("\"","\'"))
                                    session.add(comm)
                                    session.commit()
                                    self.storing.release("Computing")
                        elif job['contract']['assess']['scope'] == "reproducible":
                            if job['status'] == "2/2":
                                job['contract'] = self.cache_outputs(job['contract'], "compared")

                                ts = time.gmtime()
                                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                                job['contract']['timestamps']['processed'] = timestamp

                                session = self.storing.hook("Computing")
                                queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                                cntr_object = session.query(Contract).filter(Contract.identifier == job['contract']["id"]).first()
                                cntr_object.status = "processed"
                                cntr_object.processed = timestamp
                                cntr_object.digests_outputs = json.dumps(job['contract']['digests']['outputs']).replace("\"", "\'")
                                cntr_object.logs = json.dumps(job['contract']['logs']).replace("\"", "\'")
                                queu.status = "processed"
                                queu.processed = timestamp
                                session.commit()
                                self.storing.release("Computing")

                                if self.connected():
                                    ## Ask the RRC network to decide based on the current contract content.
                                    session = self.storing.hook("Computing")
                                    comm = Communication(sender="computing", receiver="networking", function="contract:decision", request=json.dumps(contract).replace("\"","\'"))
                                    session.add(comm)
                                    session.commit()
                                    self.storing.release("Computing")
                        elif job['contract']['assess']['scope'] == "replicable":
                            if job['status'] == "2/2":
                                job['contract'] = self.cache_outputs(job['contract'], "compared")

                                ts = time.gmtime()
                                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                                job['contract']['timestamps']['processed'] = timestamp

                                session = self.storing.hook("Computing")
                                queu = session.query(Queu).filter(Queu.id == job["id"]).first()
                                cntr_object = session.query(Contract).filter(Contract.identifier == job['contract']["id"]).first()
                                cntr_object.status = "processed"
                                cntr_object.processed = timestamp
                                cntr_object.digests_outputs = json.dumps(job['contract']['digests']['outputs']).replace("\"", "\'")
                                cntr_object.logs = json.dumps(job['contract']['logs']).replace("\"", "\'")
                                queu.status = "processed"
                                queu.processed = timestamp
                                session.commit()
                                self.storing.release("Computing")

                                if self.connected():
                                    ## Ask the RRC network to decide based on the current contract content.
                                    session = self.storing.hook("Computing")
                                    comm = Communication(sender="computing", receiver="networking", function="contract:decision", request=json.dumps(contract).replace("\"","\'"))
                                    session.add(comm)
                                    session.commit()
                                    self.storing.release("Computing")
            idx += 1
        for index in sorted(to_remove, reverse=True):
            del jobs[index]
        return jobs

    def run(self):
        xprint('Computing', 'inf', 'running...')
        # Recover her if already.
        # ToDo.
        stop = False
        while True:
            # Look for requests
            session = self.storing.hook("Computing")
            current_node = session.query(Instance).first()
            if current_node.status == "stopped":
                stop = True
            self.storing.release("Computing")
            if stop:
                xprint('Computing', 'inf', 'stopping...')
                break
            session = self.storing.hook("Computing")
            coms = session.query(Communication).filter(Communication.receiver == "computing").all()
            for com in coms:
                if com:

                    request = {'type':'received', 'comm':com.dict()}
                    self.storing.release("Computing")
                    self.process(request)
                else:
                    self.storing.release("Computing")

            # Look for responses
            session = self.storing.hook("Computing")
            coms = session.query(Communication).filter(Communication.sender == "computing").all()
            for com in coms:
                if com:
                    request = {'type':'sent', 'comm': com.dict()}
                    self.storing.release("Computing")
                    self.process(request)
                else:
                    self.storing.release("Computing")

            # Look for queu and new contracts to add
            # next request contains a check for the running containers.
            # and the addition in the queu of new contracts.
            session = self.storing.hook("Computing")
            jobs = session.query(Queu).all()
            ## Check if the containers are done.
            request = {'type':'jobs', 'jobs':[j.dict() for j in jobs]}
            self.storing.release("Computing")
            ## Look for the next 10 contracts
            session = self.storing.hook("Computing")
            pagination = paginate(session.query(Contract).filter(Contract.status == "added").order_by(Contract.reward), 1, 10)
            cntrs = pagination.items
            # xprint("Computing", "deb", "Paginate: {0}".format(len(cntrs)))
            # break
            ## Check if the containers are done.
            request['contracts'] = [c.dict() for c in cntrs]
            self.storing.release("Computing")
            self.process(request)
            time.sleep(10)
        xprint('Computing', 'inf', 'stopped.')
