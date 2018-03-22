# The networking deamon/thread
from daemon import runner
from threading import Thread
import time
from . import *
from rrc.main.storing import *
import requests
import json

def online(func):
   def func_wrapper(self, *args, **kwargs):
       if self.connected():
           return func(self, *args, **kwargs)
       else:
           xprint('Networking', 'warn', 'Warning: Node running in localhost.')
           xprint('Networking', 'warn', 'Beware: Limited access to the RRC network.')
           return None
   return func_wrapper

class Networking(Thread):
    """docstring for ."""
    def __init__(self):
        super(Networking, self).__init__()
        self.setName('RRC-Networking')
        self.daemon = False
        self.remote = "https://corr-root.org/rrc/0.1"
        self.session = None
        self.localhost = True
        self.storing = None

    def connect(self):
        self.localhost = False

    def connected(self):
        return not self.localhost

    def network_pub(self):
        xprint('Networking', 'deb', 'Fetching the RRC network public key...')
        try:
            r = requests.get("{0}/network/pub".format(self.remote))
            if r.status_code == 200:
                return r.text
            else:
                xprint('Networking', 'err', 'Error: Server return code [{0}]'.format(r.status_code))
                xprint('Networking', 'inf', 'Tip: Try again later.')
                return None
        except Exception as e:
            xprint('Networking', 'err', 'Error: Communication with the RRC network failed.')
            xprint('Networking', 'inf', 'Tip: Please check internet connexion.')
            return None

    @online
    def node_configure(self, owner=None):
        xprint('Networking', 'deb', 'Sending a request to configure the node...')
        # Package the request with
        # the node public key.
        # the node id requested: Hash256(publickey)
        # the owner username
        # The network: signature Hash network_pub.
        # encrypt with the network public key.
        # {'signature': sign_network, 'content': encrypted_content}
        # Check for seeing if we can have our node id allowed on the network.
        # Return {'signature':sign_node, 'content': encrypted_content}
        try:
            data = {'signature': self.storing.signature_network()}

            payload = {"node":self.storing.signature_node()}
            payload['pub'] = self.storing.rsa_pub.exportKey(format='PEM').encode("utf-8")

            data['payload'] = self.storing.encrypt(json.dumps(payload))
            r = requests.post("{0}/node/configure".format(self.remote), data=data)
            if r.status_code == 200:
                response = json.loads(r.json())
                if response['signature'] != self.storing.signature_node():
                    xprint('Networking', 'err', 'Error: Wrong signature from the network')
                    xprint('Networking', 'inf', 'Tip: Try again later.')
                    return None
                else:
                    return self.storing.decrypt(response['payload'])
            else:
                xprint('Networking', 'err', 'Error: Server return code [{0}]'.format(r.status_code))
                xprint('Networking', 'inf', 'Tip: Try again later.')
                return None
        except Exception as e:
            xprint('Networking', 'err', 'Error: Communication with the RRC network failed.')
            xprint('Networking', 'inf', 'Tip: Please check internet connexion.')
            return None

    def network_summary(self):
        xprint('Networking', 'deb', 'Sending a request for a summary of the RRC network...')
        try:
            data = {'signature': self.storing.signature_network()}
            payload = self.storing.encrypt(json.dumps(data))
            r = requests.post("{0}/network/summary".format(self.remote), data=payload)
            if r.status_code == 200:
                response = json.loads(r.json())
                if response['signature'] != self.storing.signature_node():
                    xprint('Networking', 'err', 'Error: Wrong signature from the network')
                    xprint('Networking', 'inf', 'Tip: Try again later.')
                    return None
                else:
                    return self.storing.decrypt(response['payload'])
            else:
                xprint('Networking', 'err', 'Error: Server return code [{0}]'.format(r.status_code))
                xprint('Networking', 'inf', 'Tip: Try again later.')
                return None
        except Exception as e:
            xprint('Networking', 'err', 'Error: Communication with the RRC network failed.')
            xprint('Networking', 'inf', 'Tip: Please check internet connexion.')
            return None

    def network_price(self):
        xprint('Networking', 'deb', 'Sending a request for the current price of 1 RRC in USD...')
        try:
            data = {'signature': self.storing.signature_network()}
            payload = self.storing.encrypt(json.dumps(data))

            r = requests.post("{0}/network/price".format(self.remote), data=payload)
            if r.status_code == 200:
                response = json.loads(r.json())
                if response['signature'] != self.storing.signature_node():
                    xprint('Networking', 'err', 'Error: Wrong signature from the network')
                    xprint('Networking', 'inf', 'Tip: Try again later.')
                    return None
                else:
                    return self.storing.decrypt(response['payload'])
            else:
                xprint('Networking', 'err', 'Error: Server return code [{0}]'.format(r.status_code))
                xprint('Networking', 'inf', 'Tip: Try again later.')
                return None
        except Exception as e:
            xprint('Networking', 'err', 'Error: Communication with the RRC network failed.')
            xprint('Networking', 'inf', 'Tip: Please check internet connexion.')
            return None

    @online
    def node_network(self, owner=None, password=None):
        xprint('Networking', 'deb', 'Sending handshake request to the RRC Network...')
        # Check to request a session key for the node and owner info to store here.
        # node id.
        # owner password.
        # {'signature':sign_network, 'content':encrypt_content}
        # Return {'signature':sign_node, 'content': encrypted_content}
        try:
            data = {'signature': self.storing.signature_network()}

            payload = {"node":self.storing.signature_node()}
            payload['owner'] = {'email': owner, 'password': password}

            data['payload'] = self.storing.encrypt(json.dumps(payload))

            r = requests.post("{0}/node/network".format(self.remote), data=data)

            if r.status_code == 200:
                response = json.loads(r.json())
                if response['signature'] != self.storing.signature_node():
                    xprint('Networking', 'err', 'Error: Wrong signature from the network')
                    xprint('Networking', 'inf', 'Tip: Try again later.')
                    return None
                else:
                    return self.storing.decrypt(response['payload'])
            else:
                xprint('Networking', 'err', 'Error: Server return code [{0}]'.format(r.status_code))
                xprint('Networking', 'inf', 'Tip: Try again later.')
                return None
        except Exception as e:
            xprint('Networking', 'err', 'Error: Communication with the RRC network failed.')
            xprint('Networking', 'inf', 'Tip: Please check internet connexion.')
            return None

    def node_fetchid(self, owner):
        try:
            r = requests.post("{0}/node/fetchid/{1}".format(self.remote, self.session), data = owner)
            return json.loads(r.json())
        except:
            return False

    @online
    def sync_network(self):
        # Look for new contracts to run.
        # Finalize push of executed contracts.
        # Fetch for updates on contracts: cancelations or edits.
        # Pick the last block to chain by sending the signature of the last one.
        xprint("Networking", "deb", "Synching with the RRC network...")
        return {}

    def link_storage(self, storing=None):
        self.storing = storing

    @online
    def process(self, request):
        xprint("Networking", "deb", "Processing the request...")

    def run(self):
        xprint('Networking', 'inf', 'running...')
        stop = False
        while True:
            session = self.storing.hook("Networking")
            current_node = session.query(Instance).first()
            if current_node.status == "stopped":
                stop = True
            self.storing.release("Networking")
            if stop:
                xprint('Networking', 'inf', 'stopping...')
                break
            request = self.sync_network()
            self.process(request)
            session = self.storing.hook("Networking")
            com = session.query(Communication).filter(Communication.receiver == "networking").first()
            if com:
                request = com.dict()
                self.storing.release("Networking")
                self.process(request)
            else:
                self.storing.release("Networking")
            time.sleep(3)
        xprint('Networking', 'inf', 'stopped.')
