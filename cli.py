import click
from rrc.main.node import Node
from rrc.main.networking import Networking
from rrc.main.computing import Computing
from rrc.main.storing import *
import getpass
import docker
from . import *
from rrc import __version__ as version
from rrc import _debug as _debug

@click.group()
def cmd():
    pass

@cmd.command()
@click.option('--debug/--no-debug', default=None, help="Show debug logs.")
@click.option('--clean/--no-clean', default=None, help="Delete all the blocks.")
def block(debug, clean): # show the lask block in the blockchain for now.
    if debug:
        _debug = True

    storing = Storing()
    networking = Networking()
    computing = Computing()
    networking.link_storage(storing)
    computing.link_storage(storing)
    net_pub = networking.network_pub()

    session = storing.hook("Node")
    current_node = session.query(Instance).first()
    if current_node and not current_node.localhost:
        networking.connect()
        storing.connect()
    storing.release("Node")

    # To hide for production.
    # Never allow this even in localhost dev test.
    if clean:
        sure = input("Do you really want to proceed: (y)es | (n)o ?  ")
        if sure.lower() == "y":
            session = storing.hook("Node")
            blks = session.query(Block).all()
            for blk in blks:
                session.delete(blk)
            session.commit()
            storing.release("Node")
            xprint("Node", "warn", "All Blocks removed.")
        elif sure.lower() == "n":
            xprint('Node', 'warn', 'Well understood. Cheers!')
        else:
            xprint('Node', 'warn', 'Warning: Unknown answer. (y)es/(n)o.')
    else:
        storing = Storing()
        networking = Networking()
        computing = Computing()
        networking.link_storage(storing)
        computing.link_storage(storing)
        net_pub = networking.network_pub()

        session = storing.hook("Node")
        current_node = session.query(Instance).first()
        if current_node and not current_node.localhost:
            networking.connect()
            storing.connect()
        storing.release("Node")

        if networking.connected():
            xprint("Node", "warn", "Warning: We do not support showing the last block from the network for now.")
        else:
            session = storing.hook("Node")
            last_blk = session.query(Block).filter(Block.last == True).first()
            if last_blk:
                xprint("Node", "inf", "Last Block: \n{0}".format(last_blk))
            else:
                xprint("Node", "inf", "The blockchain is currently empty.")
            storing.release("Node")

# add a clean up command to wipe the .lock just in case something is messed up.
# Also in exceptions try to always release the lock.
# Finally for forced terminations, make sure to place a callback to cleanup the lock.
@cmd.command()
@click.option('--debug/--no-debug', default=None, help="Show debug logs.")
def unlock(debug):
    if debug:
        _debug = True
    xprint('Node', 'deb', 'Entering the cli unlock command...')
    xprint('Node', 'tip', 'Only do this when one component did not release the storing lock properly.')
    xprint('Node', 'tip', 'The current deadlock is preventing the whole node to run properly.')
    xprint('Node', 'warn', 'Warning: This will force the removal of the current lock on storing.')
    xprint('Node', 'warn', 'Warning: Doing this can cause non-reversible arm to your storage integrity.')
    xprint('Node', 'warn', 'Warning: Ensure that no component is actively using the current lock.')
    sure = input("Do you really want to proceed: (y)es | (n)o ?  ")
    if sure.lower() == "y":
        storing = Storing()
        storing.unlock()
    elif sure.lower() == "n":
        xprint('Node', 'warn', 'Well understood. Cheers!')
    else:
        xprint('Node', 'warn', 'Warning: Unknown answer. (y)es/(n)o.')


@cmd.command()
# Summary of the network:
# - Check that we can connect to it.
# - Show a map of the network nodes. Total, By continent, by country.
# - Show the number of computations ran so far.
# - Show the amount of rewards generated so far.
# - Show the price of a reward.
# - Says if the current node is connected or disconnected from the network.
# - Says what is the state of current node: Behind the network, synching or up to date.
@click.option('--summary/--no-summary', default=None, help="The summary of the RRC network.")
@click.option('--price/--no-price', default=None, help="The current price of 1 RRC in different exchanges.")
@click.option('--debug/--no-debug', default=None, help="Show debug logs.")
def network(summary, price, debug):
    if debug:
        _debug = True
    xprint('Node', 'deb', 'Entering the cli network command...')
    storing = Storing()
    networking = Networking()

    net_pub = networking.network_pub()
    if net_pub:
        storing.network_pub(net_pub)
    else:
        xprint('Node', 'err', 'Error: Cannot reach the RRC network.')
        xprint('Node', 'warn', 'Warning: Requests to the network will most likely fail.')
        xprint('Node', 'inf', 'Tip: Please check that you have a reliable internet connexion.')
        return

    session = storing.hook("Node")
    current_node = session.query(Instance).first()
    storing.release("Node")
    if current_node is None:
        xprint('Node', 'err', 'Error: You must configure the node before using this command features.')
        xprint('Node', 'inf', 'Tip: rrc node --config')
        return
    else:
        if summary:
            response = networking.network_summary()
            if response:
                xprint('Node', 'deb', ' Network summary\n')
                xprint(json.dumps(response, sort_keys=True, indent=4))

        if price:
            response = networking.network_price()
            if response:
                xprint('Node', 'deb', 'RRC Network >> Price\n')
                xprint(json.dumps(response, sort_keys=True, indent=4))

@cmd.command()
@click.option('--setup/--no-setup', default=None, help="Setup the node ownership.")
@click.option('--summary/--no-summary', default=None, help="The summary of the node ownership information.")
@click.option('--debug/--no-debug', default=None, help="Show debug logs.")
def owner(setup, summary, debug):
    if debug:
        _debug = True
    xprint('Node', 'deb', 'Entering the cli owner command...')
    storing = Storing()
    if setup:
        xprint('Node', 'inf', 'Setting up Node\' owner credentials')
        email = input('email on CoRR: ')
        session = storing.hook("Node")
        instance_owner = Owner(email=email, rewards=0.0)
        session.add(instance_owner)
        session.commit()
        storing.release("Node")

    if summary:
        session = storing.hook("Node")
        instance_owner = session.query(Owner).first()
        if instance_owner:
            xprint('Node', 'inf', '\n{0}'.format(instance_owner))
        else:
            xprint('Node', 'err', 'Error: No owner setup for this node.')
            xprint('Node', 'inf', 'Tip: You must setup the node owner\'s for this to work.')
            xprint('Node', 'inf', 'Tip: rrc owner --setup.')
            xprint('Node', 'warn', 'Warning: You will not be able to call network commands [\'summary\', \'price\']')
            xprint('Node', 'inf', 'Tip: Setup the node owner if you plan to reach the network.')
        storing.release("Node")

@cmd.command()
@click.option('--config/--no-config', default=None, help="Configure the node.")
@click.option('--summary/--no-summary', default=None, help="The summary of the node instance.")
@click.option('--start/--no-start', default=None, help="Start the node instance.")
@click.option('--stop/--no-stop', default=None, help="Stop the node instance.")
@click.option('--network/--no-network', default=None, help="Configure the node to be connected to the network.")
@click.option('--debug/--no-debug', default=None, help="Show debug logs.")
def node(config, summary, start, stop, network, debug):
    if debug:
        _debug = True

    xprint('Node', 'deb', 'RRC Node >> Entering the cli node command...')
    storing = Storing()
    networking = Networking()
    computing = Computing()
    networking.link_storage(storing)
    computing.link_storage(storing)
    net_pub = networking.network_pub()

    session = storing.hook("Node")
    current_node = session.query(Instance).first()
    if current_node and not current_node.localhost:
        networking.connect()
        storing.connect()
    storing.release("Node")

    if net_pub:
        storing.network_pub(net_pub)
    else:
        xprint('Node', 'err', 'Error: Cannot reach the RRC network.')
        xprint('Node', 'warn', 'Warning: Requests to the network will most likely fail.')
        xprint('Node', 'inf', 'Tip: Please check that you have a reliable internet connexion.')

    if summary:
        session = storing.hook("Node")
        instance = session.query(Instance).first()
        if instance:
            xprint('Node', 'inf', '\n{0}'.format(instance))
        else:
            xprint('Node', 'err', 'Error: You must configure the node before using this command features.')
            xprint('Node', 'inf', 'Tip: rrc node --config')
        storing.release("Node")

    if config:
        # Check if the owner is sure to reconfigure teh node again before continuing.
        xprint('Node', 'warn', 'Warning: The following action will reset your current setup.')
        go_on  = input("Are you sure about this: y(es) | n(o) ?  ")
        counter = 0
        while go_on.lower() not in ["y", "n"]:
            counter += 1
            xprint('Node', 'warn', 'Warning: Unknown answer. (y)es/(n)o. Attempt({0}/5)'.format(counter))
            go_on  = input("Are you sure about this: y(es) | n(o) ?  ")
            if counter == 5:
                break
        if counter == 5:
            xprint('Node', 'warn', 'Warning: Maximum attempts reached. Cheers!')
            return
        else:
            if go_on.lower() == "n":
                xprint('Node', 'warn', 'Well understood. Cheers!')
                return
            storing.generate_rsa()
            storing.rsa_private()
            storing.rsa_public()

            session = storing.hook("Node")
            current_node = session.query(Instance).first()
            if current_node:
                session.delete(current_node)
            current_node = Instance(version=version, identifier=storing.signature_node(), session="unknown", localhost=True, status="config", rewards=0.0)
            session.add(current_node)
            session.commit()
            current_owner = session.query(Owner).first()
            if current_owner:
                response = networking.node_configure(current_owner.email)
                if response:
                    xprint('Node', 'inf', 'Network Handshake success!')
                else:
                    xprint('Node', 'err', 'Error: Could not achieve a proper handshake with the RRC network.')
                    xprint('Node', 'warn', 'Warning: You will not be able to call network commands [\'summary\', \'price\']')
            else:
                xprint('Node', 'warn', 'Warning: No owner setup for this node.')
                xprint('Node', 'inf', 'Tip: rrc owner --setup.')
                xprint('Node', 'warn', 'Warning: You will not be able to call network commands [\'summary\', \'price\']')
                xprint('Node', 'inf', 'Tip: Setup the node owner if you plan to reach the network.')

            storing.release("Node")
    else:
        session = storing.hook("Node")
        current_node = session.query(Instance).first()
        if current_node is None:
            storing.release("Node")
            xprint('Node', 'err', 'Error: You must configure the node before using this command features.')
            xprint('Node', 'inf', 'Tip: rrc node --config.')
            xprint('Node', 'warn', 'Warning: You will not be able to call network commands [\'summary\', \'price\']')
            xprint('Node', 'inf', 'Tip: Setup the node owner if you plan to reach the network.')
            return
        else:
            storing.rsa_private()
            storing.rsa_public()

            current_owner = session.query(Owner).first()
            if current_owner:
                response = networking.node_configure(current_owner.email)
                if response:
                    xprint('Node', 'inf', 'Network Handshake success!')
                else:
                    xprint('Node', 'err', 'Error: Could not achieve a proper handshake with the RRC network.')
                    xprint('Node', 'warn', 'Warning: You will not be able to call network commands [\'summary\', \'price\']')
            else:
                xprint('Node', 'warn', 'Warning: No owner setup for this node.')
                xprint('Node', 'inf', 'Tip: rrc owner --setup.')
                xprint('Node', 'warn', 'Warning: You will not be able to call network commands [\'summary\', \'price\']')
                xprint('Node', 'inf', 'Tip: Setup the node owner if you plan to reach the network.')
            storing.release("Node")

    if network:
        session = storing.hook("Node")
        current_node = session.query(Instance).first()
        history = session.query(History).all()
        if current_node:
            if len(history) > 0 and current_node.localhost:
                storing.release("Node")
                xprint('Node', 'err', 'Error: Previous localhost configuration found on the system.')
                xprint('Node', 'inf', 'Tip: Reconfigure the node with --network to proceed.')
                overwride = input("Unless you want to erase the current configuration: (y)es | (n)o ?  ")
                if overwride.lower() == "y":
                    current_node.localhost = False
                    for hst in history:
                        session.detele(hst)
                    for qu in session.query(Queu).all():
                        session.delete(qu)
                    for cnt in session.query(Contract).all():
                        session.delete(cnt)
                    for lg in session.query(Log).all():
                        session.delete(lg)
                    session.commit()
                elif overwride.lower() == "n":
                    storing.release("Node")
                    xprint('Node', 'warn', 'Well understood. Cheers!')
                    return
                else:
                    storing.release("Node")
                    xprint('Node', 'warn', 'Warning: Unknown answer. (y)es/(n)o.')
                    return
            else:
                current_node.localhost = False
                session.commit()
        storing.release("Node")
        session = storing.hook("Node")
        current_owner = session.query(Owner).first()
        if current_owner is None:
            storing.release("Node")
            xprint('Node', 'err', 'Error: No owner setup for this node.')
            xprint('Node', 'inf', 'Tip: Please setup the node owner before attempting (1).')
            xprint('Node', 'inf', 'Tip: to configure the it over the RRC network (2).')
            xprint('Node', 'inf', 'Tip: rrc owner --setup.')
            xprint('Node', 'warn', 'Warning: You will not be able to call network commands [\'summary\', \'price\']')
            xprint('Node', 'inf', 'Tip: Setup the node owner if you plan to reach the network.')
            return
        else:
            storing.release("Node")
            networking.connect()
            storing.connect()
    else:
        session = storing.hook("Node")
        current_node = session.query(Instance).first()
        history = session.query(History).all()
        if len(history) > 0 and not current_node.localhost:
            storing.release("Node")
            xprint('Node', 'err', 'Error: Previous non localhost configuration found on the system.')
            xprint('Node', 'inf', 'Tip: Reconfigure the node without --network to proceed.')
            overwride = input("Unless you want to erase the current configuration: (y)es | (n)o ?  ")
            if overwride.lower() == "y":
                current_node.localhost = True
                for hst in history:
                    session.detele(hst)
                for qu in session.query(Queu).all():
                    session.delete(qu)
                for cnt in session.query(Contract).all():
                    session.delete(cnt)
                for lg in session.query(Log).all():
                    session.delete(lg)
                session.commit()
                storing.release("Node")
            else:
                storing.release("Node")
                xprint('Node', 'warn', 'Well understood. Cheers!')
                return
        else:
            if not current_node.localhost:
                networking.connect()
                storing.connect()
                xprint('Node', 'deb', 'Network Connected!')
            storing.release("Node")

    if start:
        if networking.connected():
            session = storing.hook("Node")
            instance_owner = session.query(Owner).first()
            owner = None
            if instance_owner is None:
                xprint('Node', 'err', 'Error: No owner setup found for this node.')
                xprint('Node', 'inf', 'Tip: Please setup the node owner before attempting (1).')
                xprint('Node', 'inf', 'Tip: to configure the it over the RRC network (2).')
                xprint('Node', 'warn', 'Warning: You will not be able to call network commands [\'summary\', \'price\']')
                xprint('Node', 'inf', 'Tip: Setup the node owner if you plan to reach the network.')
                storing.release("Node")
                return
            else:
                owner = instance_owner.email
                storing.release("Node")

            xprint('Node', 'warn', 'Warning: Node Owner [{0}] credentials required here.'.format(instance_owner.email))
            password1 = getpass.getpass('password on CoRR: ')
            password2 = getpass.getpass('again on CoRR: ')
            counter = 0
            while password1 != password2:
                counter += 1
                xprint('Node', 'err', 'Error: Password Mismatch! Attempt({0})'.format(counter))
                password1 = getpass.getpass('password on CoRR: ')
                password2 = getpass.getpass('again on CoRR: ')

                if counter == 5:
                    break
            if counter == 5:
                xprint('Node', 'warn', 'Warning: Maximum attempts reached. Cheers!')
                return
            else:
                # network.
                response = networking.node_network(instance_owner.email, password1)
                response = {}
                response["node"] = {}
                response["node"]["session"] = "f268471e598bf5acd768871b169d274b025bf8b62eb388585d27ac00911f036b"
                response["owner"] = {}
                response["owner"]["fname"] = "Faical Yannick"
                response["owner"]["lname"] = "Congo"
                response["owner"]["rewards"] = 1000
                if response == None:
                    xprint('Node', 'err', 'Error: could not sign in the RRC network.')
                else:
                    session = storing.hook("Node")

                    instance_owner = session.query(Owner).first()
                    instance_owner.fname = response['owner']['fname']
                    instance_owner.lname = response['owner']['lname']
                    instance_owner.rewards = response['owner']['rewards']

                    current_node = session.query(Instance).first()
                    current_node.session = response['node']['session']

                    session.commit()
                    current_node = session.query(Instance).first()
                    # if current_node.component_networking:
                    #     storing.release("Node")
                    #     xprint('Node', 'warn', 'Warning: Running networking component found!')
                    #     xprint('Node', 'inf', 'Info: Only one networking component allowed to run at a time.')
                    # else:
                    current_node.status = "running"
                    session.commit()

                    storing.release("Node")
                    # Launch the network daemon.
                    xprint('Node', 'inf', 'Networking component starting up...')
                    pid1 = networking.start()
                    # Save pid into current_node component networking.
                    xprint('Node', 'warn', pid1)
                    # Launch the computing daemon.
                    xprint('Node', 'inf', 'Computing component starting up...')
                    pid2 = computing.start()
                    # Save pid into current_node component computing.
                    xprint('Node', 'warn', pid2)
        else:
            # Localhost.
            # Launch the computing Thread.
            # Configure computing.
            session = storing.hook("Node")
            current_node = session.query(Instance).first()
            # if current_node.component_computing:
            #     storing.release("Node")
            #     xprint('Node', 'warn', 'Warning: Running computing component found!')
            #     xprint('Node', 'inf', 'Info: Only one computing component allowed to run at a time.')
            # else:
            current_node.status = "running"
            session.commit()
            storing.release("Node")
            # Launch the computing daemon.
            xprint('Node', 'inf', 'Computing component starting up...')
            pid = computing.start()

    if stop:
        xprint('Node', 'warn', 'You are about to stop this RRC node.')
        sure = input("Do you really want to proceed: (y)es | (n)o ?  ")
        if sure.lower() == "y":
            session = storing.hook("Node")
            current_node = session.query(Instance).first()
            status = current_node.status
            session.commit()
            storing.release("Node")
            if status != "stopped":
                session = storing.hook("Node")
                current_node = session.query(Instance).first()
                current_node.status = "stopping"
                session.commit()
                if not current_node.localhost:
                    networking.connect()
                    storing.connect()
                storing.release("Node")
                session = storing.hook("Node")
                current_node = session.query(Instance).first()
                current_node.status = "stopped"
                session.commit()
                storing.release("Node")
                xprint('Node', 'inf', 'This RRC Node stopped')
        elif sure.lower() == "n":
            xprint('Node', 'warn', 'Well understood. Cheers!')
        else:
            xprint('Node', 'warn', 'Warning: Unknown answer. (y)es/(n)o.')


@cmd.command()
@click.option('--queu/--no-queu', default=None, help="Show the summary of the contracts queu on the node.")
@click.option('--show', default=None, help="Show details of a specific contract from its id.")
@click.option('--page', default=1, help="Paginate the contracts display.")
@click.option('--submit', default=None, help="Submit a contract to a localhost instance.")
@click.option('--cancel', default=None, help="Cancel a contract on a localhost instance.")
@click.option('--clean/--no-queu', default=None, help="Wipe all the contracts.")
@click.option('--debug/--no-debug', default=None, help="Show debug logs.")
# Before going on the network the localhost instance has to be wipped clean.
# Same thing before starting a localhost from a network instance.
def contract(queu, show, page, submit, cancel, clean, debug):
    if debug:
        _debug = True
    xprint('Node', 'deb', 'Entering the cli contract command...')
    storing = Storing()
    networking = Networking()
    computing = Computing()
    networking.link_storage(storing)
    computing.link_storage(storing)

    session = storing.hook("Node")
    current_node = session.query(Instance).first()

    current_node.status = "stopping"
    session.commit()

    if not current_node.localhost:
        networking.connect()
        storing.connect()
    storing.release("Node")

    if queu:
        xprint('Node', 'deb', 'Pretty Table of the queu.')
        computing.queu()

    elif show:
        xprint('Node', 'deb', 'Showing a specific contract.')
        computing.show(show)

    elif submit:
        xprint('Node', 'deb', 'Submitting a contract.')
        computing.submit(submit)

    elif cancel:
        xprint('Node', 'deb', 'Requesting node to cancel a contract.')
        computing.cancel(cancel)

    elif clean:
        # Submit only work in localhost. or online when the components are off the network.
        xprint('Node', 'warn', 'You are about to erase all your workload.')
        sure = input("Do you really want to proceed: (y)es | (n)o ?  ")
        if sure.lower() == "y":
            session = storing.hook("Node")
            current_queu = session.query(Queu).all()
            current_contracts = session.query(Contract).all()
            for qu in current_queu:
                session.delete(qu)
            for cnt in current_contracts:
                session.delete(cnt)
            session.commit()
            storing.release("Node")
        elif sure.lower() == "n":
            xprint('Node', 'warn', 'Well understood. Cheers!')
        else:
            xprint('Node', 'warn', 'Warning: Unknown answer. (y)es/(n)o.')
    else:
        xprint('Node', 'deb', 'Pretty Table of the contracts.')
        computing.contracts(page)

@cmd.command()
@click.option('--summary/--no-summary', default=None, help="Show the summary of the latest events stored.")
@click.option('--page', default=None, help="Show the summary of the events on a specific page.")
@click.option('--show', default=None, help="Show the details of a specific event.")
@click.option('--clean/--no-clean', default=None, help="Wipe all the events.")
@click.option('--filter', default=None, help="Filter some events list based on keywords.")
@click.option('--export', default='json', type=click.Choice(['json', 'yaml', 'xml', 'txt']), help="Export a list of events to a specific format.")
@click.option('--email', default=None, help="Email a list of events.")
@click.option('--debug/--no-debug', default=None, help="Show debug logs.")
def history(summary, page, show, clean, filter, export, email, debug):
    if debug:
        _debug = True
    xprint('Node', 'deb', 'Entering the cli history command...')

if __name__ == '__rrc.main__':
    cmd()
