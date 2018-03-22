import sys
import os
import datetime
import traceback
import yaml
import time
import docker
from rrc import __version__ as version
from . import *
import json
import requests
from .authority import Authority
import shutil
import psutil

class Node(object):
    """docstring for ."""
    def __init__(self, id="localhost", network=True, contract=None):
        super(Node, self).__init__()
        xprint("RRC Network >> Launching the node...")
        self.id = id
        self.network = network
        self.client = docker.from_env()
        self.client.ping()
        self.queu = {}
        self.base_path = "/tmp/rrc"
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        if self.network:
            # Fetch an id from the network to update self.id
            # auth = Authority()
            # if not auth.hand_chake():
            #     xprint("RRC Node >> Error: Network unreachable :-()")
            # else:
            self.fetch_id()
            self.join_net()
            xprint("RRC Network >> Node is on the network :-)")
            xprint("RRC Network >> Synching with the network...")
            self.sync_net()
            xprint("RRC Network >> Node is up to date with the network :-)")
        else:
            self.configure_local(contract)

    def fetch_id(self):
        # Perform security checks here to retrieve an id.
        # Clean all local files.
        # Request node's username and password on the RRC node (A CoRR account).
        # Generate RSA keys.
        # Fetch Network authority public key.
        # Encrypt with the Network authority public key.
        # First autenticate by sending username and hashed password with node's public key.
        # Network authority decrypt with RSA private key, verifies the credentials and
        # if good, generates a node id and renewable session key.
        self.net_pub = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        self.id = "xxxxxxxxx"
        self.session = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

        # ToRelease.
        # owner = {"username":"uname_sha256xxxxxx", "password":"pass_sha256xxxxxx"}
        # auth = Authority()
        # credentials = auth.fetch_id(owner)
        #
        # self.net_pub = credentials['net-pub']
        # self.id = credentials['id']
        # self.session = credentials['session']

        time.sleep(3)
        xprint("RRC Network >> Node <{0}> is starting up...".format(self.id()))

    def join_net(self):
        # The node tries to join the network with the session_key
        # If it works it means it was granted access.
        xprint("RRC Network >> Node <{0}> is joining the network...".format(self.id()))
        time.sleep(3)

    def sync_net(self):
        time.sleep(3)

    def configure_local(self, contract=None):
        xprint("RRC Network >> Node configured for localhost :-)")
        if contract:
            # time.sleep(3)
            xprint("RRC Network >> Node is running :-)")
            xprint("RRC Node >> Loading the contract...")
            try:
                stream = open(contract, 'r')
                content = yaml.load(stream)
                logs = self.process(content)
                if len(logs) != 0:
                    return False
                for key in sorted(self.queu.keys()):
                    xprint("RRC Node >> Fetching a request to run...")
                    job = self.fetch_request(key)
                    # xprint("\n"+json.dumps(job, sort_keys=True, indent=4))
                    job = self.pre_run(job)
                    # xprint("\n"+json.dumps(job, sort_keys=True, indent=4))
                    job = self.run(job)
                    # xprint("\n"+json.dumps(job, sort_keys=True, indent=4))
                    job = self.post_run(job)

                    persist_job(job)
                    # xprint("\n"+json.dumps(job, sort_keys=True, indent=4))
                return True
            except Exception as e:
                xprint("RRC Node >> Error: Node <{0}> could not load {1}.".format(self.id, contract))
                xprint("RRC Node >> Exception: {0}".format(str(e)))
                return False
        else:
            # time.sleep(3)
            xprint("RRC Node >> Node <{0}> failed to run :-(".format(self.id))
            xprint("RRC Node >> Error: Provide a contract to process on localhost.")
            xprint("RRC Node >> Error: Node <{0}> cannot be run in local without a contract specified to process.".format(self.id))
            xprint("RRC Node >> Tip: Please provide a contract file with --cnt.")
            return False

    def process(self, content):
        request = {'version': content['version']}
        logs = []
        if float(request['version']) > float(version):
            self.push_logs(logs, "RRC Network >> Error: Node <{0}> version '{1}' cannot load a contract with version '{2}'.".format(self.id, version, request['version']))
            self.push_logs(logs, "RRC Network >> Required: Node <{0}> encontered a contract with a higher version.".format(self.id))
            self.push_logs(logs, "RRC Network >> Required: This suggests that node <{0}> software must be upgraded.".format(self.id))
            self.push_logs(logs, "RRC Network >> Tip: To get node <{0}> to join the network again,".format(self.id))
            self.push_logs(logs, "RRC Network >> Tip: you must upgrade it to the latest version.")
            return logs
        else:
            self.build_request(content, request)
            self.schedule(request)
            # xprint("\n"+json.dumps(self.queu["{0}".format(request['reward'])][-1], sort_keys=True, indent=4))
            return logs

    def build_request(self, content, request):
        if request['version'] == 0.1:

            request['container'] = content['container']
            request['user'] = content.get('user', 'rrc-admin')
            request['inputs'] = content.get('inputs', {})
            request['outputs'] = content.get('outputs', {})
            request['assess'] = content['assess']
            request['gpu'] = content.get('gpu', False)
            request['bounds'] = content.get('bounds', None)
            request['reward'] = float(content.get('reward', 0)/content.get('pool', 1))
            # status: unknown, preparing, ready, running, confirmed, rejected, failed, cancel.
            request['id'] = content['id']
            request['node'] = self.id
            request['status'] = 'unknown'

            request['digests'] = {}
            request['digests']['container'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            request['digests']['inputs'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            request['digests']['outputs'] = {}

            request['timestamps'] = {}
            request['timestamps']['added'] = 'xxxx-xx-xx xx:xx:xx'
            request['timestamps']['ready'] = 'xxxx-xx-xx xx:xx:xx'
            request['timestamps']['failure'] = 'xxxx-xx-xx xx:xx:xx'
            request['timestamps']['running'] = 'xxxx-xx-xx xx:xx:xx'
            request['timestamps']['processed'] = 'xxxx-xx-xx xx:xx:xx'
            request['timestamps']['canceled'] = 'xxxx-xx-xx xx:xx:xx'
            return request

    def push_logs(self, logs, message):
        ts = time.gmtime()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        logs.append("{0} {1}".format(timestamp, message))
        print(logs[-1])
        return logs

    def schedule(self, request):
        ts = time.gmtime()
        request['status'] = 'preparing'
        request['timestamps']['added'] = time.strftime("%Y-%m-%d %H:%M:%S", ts)

        key = "{0}".format(request['reward'])
        if key in self.queu.keys():
            self.queu[key].append(request)
        else:
            self.queu[key] = [request]
        xprint("RRC Node >> Contract {0} is scheduled for processing :-)".format(request['id']))

    def fetch_request(self, key):
       xprint("RRC Node >> Next request reward amount: {0} RRC".format(key))
       job = self.queu[key][-1]
       if len(self.queu[key]) == 1:
           del self.queu[key]
       else:
           del self.queu[key][-1]
       job['reward'] = key
       job['logs'] = []
       return job

    def pre_run(self, job):
        xprint("RRC Node >> Contract {0} is assessing if computation {1} is {2} with the submitted requirements.".format(job['id'], job['container']['repository'], job['assess']['scope']))
        # Do it for the inputs content.
        # Same for outputs.
        # Download them and check their checksum.
        if not os.path.exists("{0}/{1}".format(self.base_path, job["id"])):
           os.makedirs("{0}/{1}".format(self.base_path, job["id"]))
        else:
           xprint("RRC Node >> Cleaning up previous files from job[{0}] execution. There shouldn't be any.".format(job["id"]))
           shutil.rmtree("{0}/{1}".format(self.base_path, job["id"]))
           os.makedirs("{0}/{1}".format(self.base_path, job["id"]))

        if len(job['inputs']) != 0:
            try:
               filename, tmp_destination = get_file(job['inputs']['location'], job["id"])
               tmp_location = "{0}/{1}".format(tmp_destination, filename)
               digest = sha256_digest(tmp_location)
               if unpack(filename, tmp_destination):
                   os.remove(tmp_location)
               job['digests']['inputs'] = digest
               xprint(digest)
               if job['inputs']['digest'] == job['digests']['inputs']:
                   xprint("RRC Node >> Fetched inputs matches with the expectations.")
                   job['inputs']['origin'] = "{0}/{1}".format(tmp_destination, filename.split(".")[0])
               else:
                   job['status'] = 'failed'
                   ts = time.gmtime()
                   timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                   job['timestamps']['failure'] = timestamp
                   job['logs'] = self.push_logs(job['logs'], "RRC Node >> Error: Fetched inputs {0} does not comply with hard expectations.".format(job['inputs']['location']))
                   return job
            except Exception as e:
                job['status'] = 'failed'
                ts = time.gmtime()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                job['timestamps']['failure'] = timestamp
                job['logs'] = self.push_logs(job['logs'], "RRC Node >> Error: Unable to fetch specified inputs: {0}.".format(job['inputs']['location']))
                job['logs'] = self.push_logs(job['logs'], "RRC Node >> Exception: {0}".format(str(e)))
                if self.network:
                    # Inform the moderator that the selected not cannot perform the requested computation.
                    # http request of a failure. Including the job post.
                    pass
                return job

        if len(job['outputs']) != 0:
            xprint("RRC Node >> Job expected output has been registered.")
            job['outputs']['origin'] = "{0}/{1}/{2}".format(self.base_path, job["id"], job['outputs']['volume'].split("/")[-1])
        else:
            job['status'] = 'failed'
            ts = time.gmtime()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            job['timestamps']['failure'] = timestamp
            job['logs'] = self.push_logs(job['logs'], "RRC Node >> Error: A job should have an expected output.")
            return job

        # if 'outputs' in job['assess'].keys():
        #    try:
        #        filename, tmp_destination = get_file(job['assess']['outputs']['location'], job["id"])
        #        tmp_location = "{0}/{1}".format(tmp_destination, filename)
        #        digest = sha256_digest(tmp_location)
        #        if unpack(filename, tmp_destination):
        #            os.remove(tmp_location)
        #        job['digests']['outputs'] = digest
        #        xprint(digest)
        #        if job['assess']['outputs']['digest'] == job['digests']['outputs']:
        #             job['outputs'] = digest
        #            xprint("RRC Node >> Fetched outputs matches with the expectations.")
        #        else:
        #            job['status'] = 'failed'
        #            ts = time.gmtime()
        #            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        #            job['timestamps']['failure'] = timestamp
        #            self.push_logs(job['logs'], "RRC Node >> Error: Fetched outputs {0} does not comply with hard expectations.".format(job['assess']['outputs']['location']))
        #            return False
        #    except Exception as e:
        #        job['status'] = 'failed'
        #        ts = time.gmtime()
        #        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        #        job['timestamps']['failure'] = timestamp
        #        self.push_logs(job['logs'], "RRC Node >> Error: Unable to fetch specified outputs: {0}.".format(job['assess']['outputs']))
        #        self.push_logs(job['logs'], "RRC Node >> Exception: {0}".format(str(e)))
        #        if self.network:
        #            # Inform the moderator that the selected not cannot perform the requested computation.
        #            # http request of a failure. Including the job post.
        #            pass
        #        return False

        try:
           # Docker pull the container
           client = docker.from_env()
           image_tag = "{0}:latest".format(job['container']['repository'])
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

           job['digests']['container'] = image.id.split(":")[1]
           xprint(job['digests']['container'])
           if self.network:
               # If on net, fill in the digests and send it to the moderating network.
               # If as expected, the node will be allowed in the ready state.
               # http request POST json job to network.
               allowed = True
               if allowed:
                   job['status'] = 'ready'
                   ts = time.gmtime()
                   timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                   job['timestamps']['ready'] = timestamp
                   # xprint("\n"+json.dumps(job, sort_keys=True, indent=4))
                   return job
               else:
                   return job
           else:
               # If localhost just check that the digest is the specified one.
               # If as expected, the node will be allowed in the ready state.
               if job['container']['digest'] == job['digests']['container']:
                   xprint("RRC Node >> Pull container matches with the expectations.")
                   job['status'] = 'ready'
                   ts = time.gmtime()
                   timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                   job['timestamps']['ready'] = timestamp
                   # xprint("\n"+json.dumps(job, sort_keys=True, indent=4))
                   return job
               else:
                   job['status'] = 'failed'
                   ts = time.gmtime()
                   timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                   job['timestamps']['failure'] = timestamp
                   job['logs'] = self.push_logs(job['logs'], "RRC Node >> Error: Pulled container {0} does not comply with hard expectations.".format(job['container']['repository']))
                   return job
        except Exception as e:
           job['status'] = 'failed'
           ts = time.gmtime()
           timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
           job['timestamps']['failure'] = timestamp
           job['logs'] = self.push_logs(job['logs'], "RRC Node >> Error: Unable to fetch the container: {0}".format(job['container']['repository']))
           job['logs'] = self.push_logs(job['logs'], "RRC Node >> Exception: {0}".format(str(e)))
           return job

    def cache_outputs(self, job, scope): #scope original or compared
        filename =  job['outputs']['origin'].split("/")[-1]
        destination = job['outputs']['origin'].split("/{0}".format(filename))[0]
        folder_path = "{0}/{1}".format(destination, filename)
        base_dir = os.path.abspath(folder_path)
        base_path = os.path.normpath("{0}".format(destination))
        if job['assess']['scope'] == 'reproducible':
            for dirpath, dirnames, filenames in os.walk(base_dir):
                for name in filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    if os.path.isfile(path):
                        if scope == "original":
                            job['assess']['outputs'][os.path.relpath(path, base_path)] = sha256_digest(path)
                        elif scope == "compared":
                            job['digests']['outputs'][os.path.relpath(path, base_path)] = sha256_digest(path)
        return job

    def launch_job(self, job):
        client = docker.from_env()
        image_tag = "{0}:latest".format(job['container']['repository'])

        volumes = {}
        volumes[job['inputs']['origin']] = {'bind':job['inputs']['volume'], 'mode': 'ro'}
        volumes[job['outputs']['origin']] = {'bind':job['outputs']['volume'], 'mode': 'rw'}

        container = client.containers.run(image_tag, volumes=volumes, detach=True)
        status = container.status
        xprint("Docker container [{0}]".format(status))

        while container.status != "exited":
            container.reload()
            if status != container.status:
                status = container.status
                if status:
                    xprint("Docker container [{0}]".format(status))

        for log in container.logs():
            xprint("RRC Node >> Container Logs: {0}".format(log))
            if "ERROR" in log.upper() or "EXCEPTION" in log.upper():
                job['status'] = 'failed'
                ts = time.gmtime()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                job['timestamps']['failure'] = timestamp

        container.reload()
        container.remove()
        os.makedirs("{0}/Tested".format(job['outputs']['origin']))
        with open("{0}/Tested/another".format(job['outputs']['origin']), "w") as an_f:
            an_f.write("see!")
        return job

    def run(self, job):
        job['status'] = 'running'
        ts = time.gmtime()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        job['timestamps']['running'] = timestamp

        if job['assess']['scope'] == "repeatable":
            job = self.launch_job(job)
            self.cache_outputs(job, "original")
            job = self.launch_job(job)
            ts = time.gmtime()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            job['timestamps']['processed'] = timestamp
            return self.cache_outputs(job, "compared")
        elif job['assess']['scope'] == "reproducible":
            job = self.launch_job(job)
            ts = time.gmtime()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            job['timestamps']['processed'] = timestamp
            return self.cache_outputs(job, "compared")
        elif job['assess']['scope'] == "replicable":

            ts = time.gmtime()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            job['timestamps']['processed'] = timestamp
            return job
        else:
            ts = time.gmtime()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            job['timestamps']['processed'] = timestamp
            return job


    def post_run(self, job):
        # Check the assessment here.
        confirmed = True
        for key in job['assess']['outputs'].keys():
            if job['assess']['outputs'][key] != job['digests']['outputs'][key]:
                confirmed = False
                job['logs'] = self.push_logs(job['logs'], "RRC Node >> Decision: The assessment is rejected due to a difference found for {0}".format(key))
                break
        ts = time.gmtime()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        if not confirmed:
            job['timestamps']['rejected'] = timestamp
        else:
            job['logs'] = self.push_logs(job['logs'], "RRC Node >> Decision: The submitted assessment has been successfully confirmed! :-)")
            job['logs'] = self.push_logs(job['logs'], "RRC Node >> Decision: You will soon be awarded {0} RRC for your effort! :-)".format(job['reward']))
            job['timestamps']['confirmed'] = timestamp
        return job
