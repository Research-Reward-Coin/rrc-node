# The storage utility.
# Manipulates the database.
# SQlite/Mongodb.
import os
import sys
import json
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
import rsa
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto import Random
from Crypto.Hash import SHA256
import time
from random import random


from rrc import __version__ as version
from . import *

Base = declarative_base()

class Block(Base):
    __tablename__ = 'block'
    id = Column(Integer, primary_key=True)
    previous = Column(String(100), nullable=True)
    signature = Column(String(100), nullable=True)
    contract_id = Column(Integer, ForeignKey("contract.id"))
    contract = relationship("Contract")
    contract_global_id = Column(String(100), nullable=True)
    container = Column(String(), nullable=False) # digest of the container
    inputs = Column(String(), nullable=False) # digest of the inputs
    outputs = Column(String(), nullable=False) # digest of the outputs
    scope = Column(String(25), nullable=False) # reproducible, repeatable, replicable
    nodes = Column(String(), nullable=True)
    decisions = Column(String(), nullable=True) # per node position.
    reward = Column(Float(), nullable=True) # Total amount.
    genesis = Column(Boolean(), nullable=True) # is it the genesis block?
    last = Column(Boolean(), nullable=False) # is it the last block? Speeds up the chaining.
    status = Column(String(50), nullable=False) # created, validated, hooked, chained.
    created = Column(String(100), nullable=True) # created when the decision is being asked.
    validated = Column(String(100), nullable=True) # when the network accepeted the signature of the previous last on.
    hooked = Column(String(100), nullable=True) # when the last signature is accepted and the new one also
    chained = Column(String(100), nullable=True) # when a new block is added making this not the last one anymore.

    def dict(self):
        content = {}
        content['previous'] = self.previous
        content['hash'] = self.signature
        content['status'] = self.status
        content['last'] = self.last
        content['genesis'] = self.genesis
        content['reward'] = self.reward
        content['nodes'] = {}
        idx = 0
        dcs = self.decisions.split(",")
        for nd in self.nodes.split(","):
            content['nodes'][nd] = dcs[idx]
            idx += 1

        content['timestamps'] = {}
        content['timestamps']['created'] = self.created
        content['timestamps']['validated'] = self.validated
        content['timestamps']['hooked'] = self.hooked
        content['timestamps']['chained'] = self.chained
        content['contract'] = {}
        content['contract']['id'] = self.contract.identifier
        content['contract']['container'] = self.container
        content['contract']['inputs'] = self.inputs
        content['contract']['outputs'] = json.loads(self.outputs.replace("\'", "\""))
        content['contract']['scope'] = self.scope
        return content

    def __repr__(self):
        return json.dumps(self.dict(), sort_keys=True, indent=4)

class Owner(Base):
    __tablename__ = 'owner'
    id = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=False)
    fname = Column(String(100), nullable=True)
    lname = Column(String(100), nullable=True)
    rewards = Column(Float(), nullable=False)

    def dict(self):
        content = {}
        content['email'] = self.email
        content['fname'] = self.fname
        content['lname'] = self.lname
        content['rewards'] = self.rewards
        return content

    def __repr__(self):
        return json.dumps(self.dict(), sort_keys=True, indent=4)

class Instance(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    version = Column(String(25), nullable=False)
    identifier = Column(String(64), nullable=False)
    session = Column(String(64), nullable=False)
    localhost = Column(Boolean(), nullable=False)
    status = Column(String(25), nullable=False)
    rewards = Column(Float(), nullable=True)
    component_networking = Column(String(), nullable=True)
    component_computing = Column(String(), nullable=True)

    def dict(self):
        content = {}
        content['version'] = self.version
        content['id'] = self.identifier
        content['session'] = self.session
        content['localhost'] = self.localhost
        content['status'] = self.status
        content['rewards'] = self.rewards
        content['components'] = {'networking': self.component_networking, 'computing': self.component_computing}
        return content

    def __repr__(self):
        return json.dumps(self.dict(), sort_keys=True, indent=4)

class Contract(Base):
    __tablename__ = 'contract'
    id = Column(Integer, primary_key=True)
    identifier = Column(String(100), nullable=False)
    user = Column(String(100), nullable=False)
    status = Column(String(25), nullable=False) # unknown, preparing, ready, running, confirmed, rejected, failed, cancel
    reward = Column(Float(), nullable=True)

    inputs = Column(String(), nullable=True)
    outputs = Column(String(), nullable=True)

    digests_container = Column(String(), nullable=True)
    digests_inputs = Column(String(), nullable=True)
    digests_outputs = Column(String(), nullable=True)

    gpu = Column(Boolean(), nullable=True)

    bounds_cpu = Column(Boolean(), nullable=True)
    bounds_gpu = Column(Boolean(), nullable=True)
    bounds_mem = Column(Boolean(), nullable=True)
    bounds_bdw = Column(Boolean(), nullable=True) # bandwith

    added = Column(String(50), nullable=True)
    ready = Column(String(50), nullable=True)
    failure = Column(String(50), nullable=True)
    running = Column(String(50), nullable=True)
    processed = Column(String(50), nullable=True)
    canceled = Column(String(50), nullable=True)

    assess_scope = Column(String(25), nullable=True) # reproducible, repeatable, replicable
    assess_outputs = Column(String(), nullable=True)

    container_digest = Column(String(), nullable=True)
    container_repo = Column(String(), nullable=True)
    container_id = Column(String(), nullable=True)

    logs = Column(String(), nullable=True)

    def dict(self):
        content = {}
        content['container'] = {'id':self.container_id, 'digest':self.container_digest, 'repository':self.container_repo}
        content['user'] = "current"
        content['inputs'] = json.loads(self.inputs.replace("\'", "\""))
        content['outputs'] = json.loads(self.outputs.replace("\'", "\""))
        content['assess'] = {'scope':self.assess_scope, 'outputs':json.loads(self.assess_outputs.replace("\'", "\""))}
        content['gpu'] = self.gpu
        content['bounds'] = {'cpu':self.bounds_cpu, 'gpu':self.bounds_gpu, 'memory':self.bounds_mem, 'bandwith': self.bounds_bdw}
        content['reward'] = self.reward
        # status: added, preparing, ready, running, confirmed, rejected, failed, cancel.
        content['id'] = self.identifier
        content['node'] = "current"
        content['status'] = self.status

        content['digests'] = {}
        content['digests']['container'] = self.digests_container
        content['digests']['inputs'] = self.digests_inputs
        content['digests']['outputs'] = json.loads(self.digests_outputs.replace("\'", "\""))

        content['timestamps'] = {}
        content['timestamps']['added'] = self.added
        content['timestamps']['ready'] = self.ready
        content['timestamps']['failure'] = self.failure
        content['timestamps']['running'] = self.running
        content['timestamps']['processed'] = self.processed
        content['timestamps']['canceled'] = self.canceled

        content['logs'] = json.loads(self.logs.replace("\'", "\""))

        return content

    def __repr__(self):
        return json.dumps(self.dict(), sort_keys=True, indent=4)

class Queu(Base):
    __tablename__ = 'queu'
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("contract.id"))
    contract = relationship("Contract")
    container = Column(String(100), nullable=True)
    scheduled = Column(String(50), nullable=False) # Time scheduled.
    processed = Column(String(50), nullable=False) # Time processed.
    status = Column(String(25), nullable=False) # fetching, scheduled, preparing, running, 1/2, 2/2, processed, decision, failed, canceled,

    def dict(self):
        content = {}
        content['id'] = self.id
        content['contract'] = self.contract.dict()
        content['container'] = self.container
        content['scheduled'] = self.scheduled
        content['processed'] = self.processed
        content['status'] = self.status
        return content

    def __repr__(self):
        return json.dumps(self.dict(), sort_keys=True, indent=4)

class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    timestamp = Column(String(50), nullable=False)
    message = Column(String(250), nullable=False)

    def dict(self):
        content = {}
        content['id'] = self.id
        content['timestamp'] = self.timestamp
        content['message'] = self.message
        return content

    def __repr__(self):
        return json.dumps(self.dict(), sort_keys=True, indent=4)

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    scope = Column(String(25), nullable=False) # contract, communication.
    backup = Column(String(50), nullable=False) # Backup time.
    content = Column(String(), nullable=False)

    def dict(self):
        content = {}
        content['id'] = self.id
        content['scope'] = self.scope
        content['backup'] = self.backup
        content['content'] = self.content
        return content

    def __repr__(self):
        return json.dumps(self.dict(), sort_keys=True, indent=4)

class Communication(Base):
    __tablename__ = 'communication'
    id = Column(Integer, primary_key=True)
    sender = Column(String(25), nullable=False) # node, netw, comp
    receiver = Column(String(25), nullable=False) # node, net, comp
    sent = Column(String(50), nullable=True)
    received = Column(String(50), nullable=True)
    function = Column(String(100), nullable=False)
    request = Column(String(), nullable=False)
    response = Column(String(), nullable=True)
    status = Column(String(25), nullable=False) # sent, pulled, done.

    def dict(self):
        content = {}
        content['id'] = self.id
        content['sender'] = self.sender
        content['receiver'] = self.receiver
        content['sent'] = self.sent
        content['received'] = self.received
        content['function'] = self.function
        content['request'] = self.request
        content['response'] = self.response
        content['status'] = self.status
        return content

    def __repr__(self):
        return json.dumps(self.dict(), sort_keys=True, indent=4)

class Storing(object):
    """docstring for ."""
    def __init__(self, node=None, networking=None, computing=None):
        super(Storing, self).__init__()
        self.conf_dir = os.path.join(os.path.expanduser("~"), '.rrc')
        self.node = node
        self.networking = networking
        self.computing = computing
        self.session = None
        self.net_pub = None
        self.rsa_pub = None
        self.rsa_prv = None
        self.node_sign = None
        self.net_sign = None
        self.localhost = True

        if not os.path.exists(self.conf_dir):
            os.makedirs(self.conf_dir)
            self.engine = create_engine('sqlite:///{0}/rrc.db'.format(self.conf_dir))
            Base.metadata.create_all(self.engine)
        else:
            self.engine = create_engine('sqlite:///{0}/rrc.db'.format(self.conf_dir))

    def connect(self):
        self.localhost = False

    def connected(self):
        return self.localhost

    def generate_rsa(self):
        xprint('Storing', 'deb', 'Generating a new RSA key pair...')
        random_generator = Random.new().read
        privkey = RSA.generate(4096, random_generator)
        pubkey = privkey.publickey()
        xprint('Storing', 'deb', 'Storing the key pair...')
        with open("{0}/rrc.pub".format(self.conf_dir), 'wb') as pub_file:
            pub_file.write(pubkey.exportKey(format='PEM'))
        with open("{0}/rrc.prv".format(self.conf_dir), 'wb') as prv_file:
            prv_file.write(privkey.exportKey(format='PEM'))
        xprint('Storing', 'deb', 'done.')

    def rsa_private(self):
        if self.rsa_prv:
            return self.rsa_prv
        else:
            with open("{0}/rrc.prv".format(self.conf_dir), mode='rb') as prv_file:
                self.rsa_prv = RSA.importKey(prv_file.read())
            return self.rsa_prv

    def rsa_public(self):
        if self.rsa_pub:
            return self.rsa_pub
        else:
            with open("{0}/rrc.pub".format(self.conf_dir), mode='rb') as pub_file:
                self.rsa_pub = RSA.importKey(pub_file.read())
            return self.rsa_pub

    def hook(self, whom):
        xprint('Storing', 'deb', '{0} accessing database...'.format(whom))

        locker = "node"
        if whom == "Networking":
            locker = "networking"
        elif whom == "Computing":
            locker = "computing"
        elif whom == "Storing":
            locker = "storing"

        locks = ["storing", "computing", "networking", "node"]
        locks.remove(locker)

        self.session = None
        while self.session == None:
            busy = False
            for lck in locks:
                if os.path.isfile("{0}/.{1}".format(self.conf_dir, lck)):
                    busy = True
                    break

            if busy:
                pass
            else:
                with open("{0}/.{1}".format(self.conf_dir, locker), "w") as lock_file:
                    lock_file.write("{0}".format(whom))
                Base.metadata.bind = self.engine
                DBSession = sessionmaker(bind=self.engine)
                self.session = DBSession()
                break
        return self.session

    def encrypt(self, content): # Encrypt with the network public key. (For the RRC network decrypt with private key.)
        key = self.net_pub
        if key:
            cipher = PKCS1_v1_5.new(key)
            return cipher.encrypt(content.encode('utf-8'))
        else:
            return None

    def decrypt(self, content): # Decrypt with the node private key. (From the RRC network encrypt node public key.)
        key = self.rsa_private()
        if key:
            cipher = PKCS1_v1_5.new(key)
            return cipher.decrypt(content, None)
        else:
            return None

    def network_pub(self, key=None):
        self.net_pub = RSA.importKey(key)

    def signature_node(self):
        if self.rsa_pub:
            if self.node_sign:
                return self.node_sign
            else:
                self.node_sign = self.digest(self.rsa_pub.exportKey(format='PEM'))
                return self.node_sign
        else:
            xprint('Storing', 'err', 'Error: Unable to fetch the node public key.')
            xprint('Storing', 'inf', 'Tip: Possible internet access issues.')

    def signature_network(self):
        if self.net_pub:
            if self.net_sign:
                return self.net_sign
            else:
                self.net_sign = self.digest(self.net_pub.exportKey(format='PEM'))
                return self.net_sign
        else:
            xprint('Storing', 'err', 'Error: Unable to fetch the RRC network public key.')
            xprint('Storing', 'inf', 'Tip: Possible internet access issues.')

    def digest(self, content):
        dig = SHA256.new(content).hexdigest()
        return dig

    def gen_id(self):
        ts = time.gmtime()
        prefix = time.strftime("%Y-%m-%d %H:%M:%S:%f", ts)
        suffix = random()
        return SHA256.new("{0}{1}".format(prefix, suffix).encode("utf-8")).hexdigest()

    def release(self, whom):
        xprint('Storing', 'deb', '{0} releasing database...'.format(whom))
        locker = "node"
        if whom == "Networking":
            locker = "networking"
        elif whom == "Computing":
            locker = "computing"
        elif whom == "Storing":
            locker = "storing"
        current = False
        if os.path.isfile("{0}/.{1}".format(self.conf_dir, locker)):
            if self.session:
                self.session.close()
                os.remove("{0}/.{1}".format(self.conf_dir, locker))
        else:
            xprint('Storing', 'err', 'Error: Another component [{0}] is hooked to the database.'.format(locker))

    def unlock(self):
        locks = ["storing", "computing", "networking", "node"]
        found = False
        for lck in locks:
            if os.path.isfile("{0}/.{1}".format(self.conf_dir, lck)):
                try:
                    found = True
                    os.remove("{0}/.{1}".format(self.conf_dir, lck))
                    xprint('Storing', 'info', 'Deadlock found [{0}] and successfully removed.'.format(lck))
                except:
                    xprint('Storing', 'err', 'Deadlock found [{0}] but currently in use.'.format(lck))
                    xprint('Storing', 'info', 'Tip: Try unlock it later.')
        if not found:
            xprint('Storing', 'info', 'No deadlock found.')

    def setup(self):
        if self.node:
            self.node.link_storage(self)

        if self.networking:
            self.networking.link_storage(self)

        if self.computing:
            self.computing.link_storage(self)
