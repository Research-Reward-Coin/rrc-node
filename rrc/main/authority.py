import requests
import json

class Authority(object):
    """docstring for ."""
    def __init__(self, session=None):
        super(Authority, self).__init__()
        self.remote = "https://corr-root.org/rrc/0.1"
        self.session = session

    def hand_chake(self):
        try:
            r = requests.get("{0}/hand".format(self.remote))
            if r.text == "shake":
                return True
            else:
                return False
        except:
            return False

    def node_fetchid(self, owner):
        try:
            r = requests.post("{0}/node/fetchid/{1}".format(self.remote, self.session), data = owner)
            return json.loads(r.json())
        except:
            return False

    def node_joinnet(self, owner):
        # Tell you how far you are behind the blockchain.
        # You can share your last block number.
        try:
            r = requests.post("{0}/node/joinnet/{1}".format(self.remote, self.session), data = owner)
            return json.loads(r.json())
        except:
            return False

    def node_syncnet(self, owner):
        # Fetch N=100 blocks from the chain for updating the current one. from the last block number sent.
        # When syched it gives the jobs the node has been selected to run.
        # Or when a job is been updated (canceled), the nodes have to cancel it locally too.
        # This will have a penalty to the sender in terms of rewards.
        try:
            r = requests.post("{0}/node/syncnet/{1}".format(self.remote, self.session), data = owner)
            return json.loads(r.json())
        except:
            return False

    def job_prerun(self, job):
        # Check if the node qualifies for moving to the run state.
        try:
            r = requests.post("{0}/job/pre_run/{1}".format(self.remote, self.session), data = job)
            return json.loads(r.json())
        except:
            return False

    def job_failed(self, job):
        try:
            r = requests.post("{0}/job/failed/{1}".format(self.remote, self.session), data = job)
            return json.loads(r.json())
        except:
            return False

    def job_run(self, job):
        try:
            r = requests.post("{0}/job/run/{1}".format(self.remote, self.session), data = job)
            return json.loads(r.json())
        except:
            return False

    def job_postrun(self, job):
        try:
            r = requests.post("{0}/job/postrun/{1}".format(self.remote, self.session), data = job)
            return json.loads(r.json())
        except:
            return False

    def job_confirm(self, job):
        try:
            r = requests.post("{0}/job/confirm/{1}".format(self.remote, self.session), data = job)
            return json.loads(r.json())
        except:
            return False

    def job_reject(self, job):
        try:
            r = requests.post("{0}/job/reject/{1}".format(self.remote, self.session), data = job)
            return json.loads(r.json())
        except:
            return False

    def job_cancel(self, job):
        try:
            r = requests.post("{0}/job/cancel/{1}".format(self.remote, self.session), data = job)
            return json.loads(r.json())
        except:
            return False
