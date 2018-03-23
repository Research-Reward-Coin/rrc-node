
<p align="center">
    <img src="https://rawgit.com/usnistgov/corr/master/corr-view/frontend/images/logo.svg"
         height="240"
         alt="CoRR logo"
         class="inline">
</p>

<h1> <p align="center"><sup><strong>
RRC &ndash; The Research Reward Coin
</strong></sup></p>
</h1>

<p align="center"><sup><strong>
See the transactions here <a href="https://corr-root.org/rrc">corr-root.org/rrc</a>.
</strong></sup></p>

One reason why fraud is happening in computational science is due to the blind
trust in the scientist words for it. While one is not void of mistakes, it is sad to
see that there is more and more intentional fabricated results.
Instead of waiting for years to witness numerous failures in repeating, reproducing
or even replicating findings, we think that smart contracts are the right technology
to speed up the process of corroboration. Instead of wasting your time to create the environment to run and later check the findings
we propose a solution that requires only computational resources (machines).
As any viable cryptocurrency out there, we propose to fuel the whole infrastructure with reward incentives. This means that every time a machine corroborate a finding, if it is validated, its owner will receive some rewards: RRC (Research Reward Coin).
Although, The RRC is initially void of pecuniary value, we have a plan to induce it.
This is research and it has to generate incentives for grants and donations. And since
reproducibility is growing to prove fundamental in the eyes of everyone,
we think money to support such initiatives will derive intrinsically. We hope.
Alternatively, researchers worried about the free fall of trust in computational science will feel more confident in providing rewards to confirm that their findings are in fact as they say repeatable, reproducible and replicable.

## Compute Pi at 43 decimals!

Testing the RRC node comes with some Pi fun!
Let's say we have a code that computes pi at a certain decimal.
Such code will be wrapped in a docker container and pushed to [dockerhub](https://hub.docker.com).
To run the container, you will need to provide two volumes. The first volume is the input folder.
This folder contains the precision desired. 43 here by default.
The second volume is where we dump the actual value of pi at that decimal.
First let's build the software with pip  and python:

	$ cd testFolder
	$ git clone https://github.com/Research-Reward-Coin/rrc-node.git
	$ cd rrc-node
	$ pip install -r requirements.txt
	$ python setup.py install

To test that your installation worked you should be able to run:

	$ rrc --help
	$ Usage: rrc [OPTIONS] COMMAND [ARGS]...
	$ Options:
	$   --help  Show this message and exit.
	$ Commands:
	$   block
	$   contract
	$   history
	$   network
	$   node
	$   owner
	$   unlock
	$   version
  $   digest

Each of these commands also come with specific help details when called with --help.
For example:

	$ rrc contract --help
	$ Usage: rrc contract [OPTIONS]
	$ Options:
	$  --queu / --no-queu    Show the summary of the contracts queu on the node.
	$  --show TEXT           Show details of a specific contract from its id.
	$  --page INTEGER        Paginate the contracts display.
	$  --submit TEXT         Submit a contract to a localhost instance.
	$  --cancel TEXT         Cancel a contract on a localhost instance.
	$  --clean / --no-queu   Wipe all the contracts.
	$  --debug / --no-debug  Show debug logs.
	$  --help                Show this message and exit.

In the following we will explain how to setup and configure the RRC node locally.
The current version does not allow network based connection. This work has to come
at a later time. The network based connection needs [CoRR](https://github.com/usnistgov/corr).

### Setup the node owner

The node ownership is required on localhost mode.
Before doing anything with the node software, you must provide an owner email.
Since it is for localhost purposes, this email will not be validated against [CoRR](https://github.com/usnistgov/corr).
This will be done when the node is launched on the RRC network.

	$ rrc owner --setup
	$ 2018-xx-xx xx:xx:01 RRC Node >> Entering the cli owner command...
	$ 2018-xx-xx xx:xx:01 RRC Node >> Setting up Node' owner credentials
	$ email on CoRR: yannick.congo@gmail.com              <--- Type an email here.
	$ 2018-xx-xx xx:xx:02 RRC Storing >> Node accessing database...
	$ 2018-xx-xx 11:xx:02 RRC Storing >> Node releasing database...

To confirm that an owner for this node has been provided. Do the following:

	$ rrc owner --summary
	$ 2018-xx-xx xx:xx:05 RRC Node >> Entering the cli owner command...
	$ 2018-xx-xx xx:xx:05 RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:05 RRC Node >>
	$ {
	$    "email": "yannick.congo@gmail.com",
	$    "fname": null,
	$    "lname": null,
	$    "rewards": 0.0
	$ }
	$ 2018-xx-xx xx:xx:05 RRC Storing >> Node releasing database...

This shows that an ownership has been setup. Ignore the fact that fname, lname and rewards are not set. These are updated only when the node is connected to the RRC node. fname, lname and rewards will come from [CoRR](https://github.com/usnistgov/corr).
After setting up the node owner, we must configure the node to generate parameters needed to launch it.

### Configure the node

After the setup of the owner, we must generate a few parameters to launch the node.
Such parameters are the node identifier and its RSA key pair.

	$ rrc node --config
	$ 2018-xx-xx xx:xx:07 RRC Node >> RRC Node >> Entering the cli node command...
	$ 2018-xx-xx xx:xx:07 RRC Networking >> Fetching the RRC network public key...
	$ 2018-xx-xx xx:xx:07 RRC Networking >> Error: Server return code [404]
	$ 2018-xx-xx xx:xx:07 RRC Networking >> Tip: Try again later.
	$ 2018-xx-xx xx:xx:07 RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:07 RRC Storing >> Node releasing database...
	$ 2018-xx-xx xx:xx:07 RRC Node >> Error: Cannot reach the RRC network.
	$ 2018-xx-xx xx:xx:07 RRC Node >> Warning: Requests to the network will most likely fail.
	$ 2018-xx-xx xx:xx:07 RRC Node >> Tip: Please check that you have a reliable internet connexion.
	$ 2018-xx-xx xx:xx:07 RRC Node >> Warning: The following action will reset your current setup.
	$ Are you sure about this: y(es) | n(o) ?  y       <--- Type y here to accept.
	$ 2018-xx-xx xx:xx:11 RRC Storing >> Generating a new RSA key pair...
	$ 2018-xx-xx xx:xx:15 RRC Storing >> Storing the key pair...
	$ 2018-xx-xx xx:xx:15 RRC Storing >> done.
	$ 2018-xx-xx xx:xx:15 RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:15 RRC Networking >> Warning: Node running in localhost.
	$ 2018-xx-xx xx:xx:15 RRC Networking >> Beware: Limited access to the RRC network.
	$ 2018-xx-xx xx:xx:15 RRC Node >> Error: Could not achieve a proper handshake with the RRC network.
	$ 2018-xx-xx xx:xx:15 RRC Node >> Warning: You will not be able to call network commands ['summary', 'price']
	$ 2018-xx-xx xx:xx:15 RRC Storing >> Node releasing database...
	$ 2018-xx-xx xx:xx:15 RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:15 RRC Storing >> Node releasing database...

A this point, your localhost rrc-node is ready to be launched.
In this example it took us an overall 15 seconds to  achieve this.
To continue, you will need to terminals.
The first one will be showing the node running and the second will allow us to send requests to it in localhost.
In the first terminal, to launch the node, run:

	$ rrc node --start
	$ 2018-xx-xx xx:xx:20 RRC Node >> RRC Node >> Entering the cli node command...
	$ 2018-xx-xx xx:xx:20 RRC Networking >> Fetching the RRC network public key...
	$ 2018-xx-xx xx:xx:21 RRC Networking >> Error: Server return code [404]
	$ 2018-xx-xx xx:xx:21 RRC Networking >> Tip: Try again later.
	$ 2018-xx-xx xx:xx:21 RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:21 RRC Storing >> Node releasing database...
	$ 2018-xx-xx xx:xx:21 RRC Node >> Error: Cannot reach the RRC network.
	$ 2018-xx-xx xx:xx:21 RRC Node >> Warning: Requests to the network will most likely fail.
	$ 2018-xx-xx xx:xx:21 RRC Node >> Tip: Please check that you have a reliable internet connexion.
	$ 2018-xx-xx xx:xx:21 RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:21 RRC Networking >> Warning: Node running in localhost.
	$ 2018-xx-xx xx:xx:21 RRC Networking >> Beware: Limited access to the RRC network.
	$ 2018-xx-xx xx:xx:21 RRC Node >> Error: Could not achieve a proper handshake with the RRC network.
	$ 2018-xx-xx xx:xx:21 RRC Node >> Warning: You will not be able to call network commands ['summary', 'price']
	$ 2018-xx-xx xx:xx:21 RRC Storing >> Node releasing database...
	$ 2018-xx-xx xx:xx:21 RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:21 RRC Node >> Computing component starting up...
	$ 2018-xx-xx xx:xx:21 RRC Computing >> running...
	$ 2018-xx-xx xx:xx:21 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:21 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:21 RRC Computing >> Processing request...

Your rrc node is running on localhost. Its computing component is waiting for request to process.

### The pi example

Yeyi! As said before we have a pi [example](./example).
It contains:

 - [pi](example/pi): A computation of pi that is based on Gauss' refinement of Machin's formula.
 - [pi-2](example/pi-2): Computation of pi that uses the mpmath library.
 - [precision](example/precision.zip): A compressed folder containing the precision of 43 decimals.
 - [precision-1](example/precision-1.zip): A compressed folder containing the precision of 10 decimals.
 - [precision-2](example/precision-2.zip): A compressed folder containing the precision of 20 decimals.
 - [precision-3](example/precision-3.zip): A compressed folder containing the precision of 30 decimals.
 - [precision-4](example/precision-4.zip): A compressed folder containing the precision of 40 decimals.

Each ***compute.py*** code in ***pi*** and ***pi-2*** reads in the precision from one the previous compressed
options. Each of the two computations of pi, has a precision and a computed folder that allows the reader to
quickly test the code. Thus clearing all the questions you might have. These computations also comes with
***Dockerfiles*** which were used to build the two conatainers used in this use case:

 - [The pi container](https://hub.docker.com/r/palingwende/pi/)
 - [The pi-2 container](https://hub.docker.com/r/palingwende/pi-2/)

The two containers are the one used in the pi RRC contracts examples. The following section will address them.

### Some RRC contracts.

Along with the pi computations, we provide four contracts that will help grasp the
purpose of RRC and how blockchain based smart contracts are play a crucial role.
First let's list them:

  - [contract-repeatable.yaml](example/contract-repeatable.yaml): A smart contract to confirm that
  the running [the pi container](https://hub.docker.com/r/palingwende/pi/) twice with [precision](example/precision.zip)
  produces the same outcome. This also was verified for any ***precision***.
  - [contract-reproducible.yaml](example/contract-reproducible.yaml): A smart contract to confirm that
  running [the pi container](https://hub.docker.com/r/palingwende/pi/) will always produce a ***pi*** file in
  the ***computed*** folder with a digest that matches ***d42997e6d918a969ee2addbc99cd46d447813e977e5c31d201a9b871f8a9d2d6***.
  - [contract-replicable.yaml](example/contract-replicable.yaml): A smart contract to confirm that
  running [the pi-2 container](https://hub.docker.com/r/palingwende/pi/) with [precision-2](example/precision.zip)
  produces the same outcome as [the pi container](https://hub.docker.com/r/palingwende/pi/) with the same ***precision***.
  This proves that ***computation pi-2*** replicates ***computation pi*** at ***precision-2*** which is ***20***.
  - [contract-rejected.yaml](example/contract-rejected.yaml): A smart contract that shows that the same
  ***computation pi-2*** does not replicate ***computation pi*** at ***precision-1*** which is ***10***.

We encourage you to take a look at each one of them to be acknowledged with the
terminology. We have done our best in commenting the contracts. We encourage you
to try making your own contracts to run your own container codes.
Caution: You must ajust certain fields before running the contracts to avoid failures:

 - location: Based on where you clone the repo, replace the path/to section in inputs.
 - id_of_the_contract_replicated: For ***contract-rejected*** and ***contract-replicable*** change this to be the id of the
 referred contract after its execution: Use either rrc contract or rrc block.

### Finally the fun part: Hands on!

You should have noticed by now that the node is a big talker.
We are in debug mode. A future option will be available to make it less verbose.
You can now go to your second terminal window.
We recomand that you have the two terminal windows visible to see the effect
of running a command in the second one.
Now, let's run [contract-repeatable.yaml](example/contract-repeatable.yaml):

	$ rrc contract --submit /path/to/rrc-node/example/contract-repeatable.yaml.
	$ 2018-xx-xx xx:xx:25 RRC Node >> Entering the cli contract command...
	$ 2018-xx-xx xx:xx:25 RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:25 RRC Storing >> Node releasing database...
	$ 2018-xx-xx xx:xx:25 RRC Node >> Submitting a contract.
	$ 2018-xx-xx xx:xx:25 RRC Computing >> Requesting the computation of contract file [example/contract-repeatable.yaml].
	$ 2018-xx-xx xx:xx:25 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:25 RRC Computing >> Requesting the computation of contract [72ffbd1c31b36ebb75a9ff0cddbac02a0e9c2994ea632ecb0713e19d64702849].
	$ 2018-xx-xx xx:xx:25 RRC Storing >> Computing releasing database...

In the first terminal, you see few things such as these pop up:

	$ 2018-xx-xx xx:xx:26 RRC Computing >> Processing request...
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:26 RRC Computing >> Prexecuting contract           <--- The node queu should have one contract. [72ffbd1c31b36ebb75a9ff0cddbac02a0e9c2994ea632ecb0713e19d64702849]
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:26 RRC Computing >> Inputs Digest: 4a1d014c12a83283ecf3cd3d685bf9bd7cc94c6a58af46237dd5c08f9b85d927
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:26 RRC Computing >> Fetched inputs matches with the expectations.
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:26 RRC Computing >> Job expected output has been registered.
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:26 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:28 RRC Computing >> 9d9785de14f8dfa7bccab81b56aaa816517125fd6a8e7ba5485d81422b3cfbc8
	$ 2018-xx-xx xx:xx:28 RRC Computing >> Pulled container digest matches.
	$ 2018-xx-xx xx:xx:28 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:28 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:28 RRC Computing >> Executing contract [72ffbd1c31b36ebb75a9ff0cddbac02a0e9c2994ea632ecb0713e19d64702849].
	$ 2018-xx-xx xx:xx:28 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:28 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:39 RRC Computing >> Processing request...
	$ 2018-xx-xx xx:xx:39 RRC Computing >> Postexecuting contract [72ffbd1c31b36ebb75a9ff0cddbac02a0e9c2994ea632ecb0713e19d64702849].
	$ 2018-xx-xx xx:xx:39 RRC Computing >> Container loaded!
	$ 2018-xx-xx xx:xx:40 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:40 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:50 RRC Computing >> Processing request...
	$ 2018-xx-xx xx:xx:50 RRC Computing >> Postexecuting contract [72ffbd1c31b36ebb75a9ff0cddbac02a0e9c2994ea632ecb0713e19d64702849].
	$ 2018-xx-xx xx:xx:50 RRC Computing >> Container loaded!
	$ 2018-xx-xx xx:xx:50 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:50 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:55 RRC Computing >> Processing request...
	$ 2018-xx-xx xx:xx:55 RRC Computing >> Postexecuting contract [72ffbd1c31b36ebb75a9ff0cddbac02a0e9c2994ea632ecb0713e19d64702849].
	$ 2018-xx-xx xx:xx:55 RRC Storing >> Computing accessing database...
	$ 2018-xx-xx xx:xx:55 RRC Storing >> Computing releasing database...
	$ 2018-xx-xx xx:xx:59 RRC Computing >> Processing request...          <--- The node queu is empty again.

Notice that we have redacted duplicated database access and release debug logs.
The overall computation of the pi repeatable contract took ***33*** seconds.
With as expected more time used for computing the container and assessing the confirmation.
If you are fast enough. Right after viewing preexecuting... you should be able to see
the contract in the node queu. by typing:

	  $ rrc contract --queu

This contract will be cleared from the queu shortly after the last postexecuting sequence
around xx:xx:55. The same command should return an empty queu.
If you missed it in the queu, don't worry, contracts are permently stored. Run the following:

	  $ rrc contract

You will retrieve a list of contract containing the contract you have ran.
A good sign of the contract leaving the queu is the apperance of a new block.
Since this will be your first contract (we assume an bare node), the subsequent block
will be the ***genesis block***. To view the last block of the chain run:

	$ rrc block
	$ 2018-03-17 23:41:05 RRC Networking >> Fetching the RRC network public key...
	$ 2018-xx-xx xx:xx:xx RRC Networking >> Error: Server return code [404]
	$ 2018-xx-xx xx:xx:xx RRC Networking >> Tip: Try again later.
	$ 2018-xx-xx xx:xx:xx RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:xx RRC Storing >> Node releasing database...
	$ 2018-xx-xx xx:xx:xx RRC Networking >> Fetching the RRC network public key...
	$ 2018-xx-xx xx:xx:xx RRC Networking >> Error: Server return code [404]
	$ 2018-xx-xx xx:xx:xx RRC Networking >> Tip: Try again later.
	$ 2018-xx-xx xx:xx:xx RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:xx RRC Storing >> Node releasing database...
	$ 2018-xx-xx xx:xx:xx RRC Storing >> Node accessing database...
	$ 2018-xx-xx xx:xx:xx RRC Node >> Last Block:
	 {
	     "contract": {
	         "container": "9d9785de14f8dfa7bccab81b56aaa816517125fd6a8e7ba5485d81422b3cfbc8",
	         "id": "72ffbd1c31b36ebb75a9ff0cddbac02a0e9c2994ea632ecb0713e19d64702849",
	         "inputs": "4a1d014c12a83283ecf3cd3d685bf9bd7cc94c6a58af46237dd5c08f9b85d927",
	         "outputs": {
	             "computed/pi": "d42997e6d918a969ee2addbc99cd46d447813e977e5c31d201a9b871f8a9d2d6"
	         },
	         "scope": "repeatable"
	     },
	     "genesis": true,
	     "hash": "3f2d8f883817fd789d3f82dea37d6319e7717b4e606c59c94168edd99fca3988",
	     "last": true,
	     "nodes": {
	         "af471328fad0b5f33da62485f3e1a3177a31a03da51f3c827a20715edee9caf1": "confirmed"
	     },
	     "previous": null,
	     "reward": 57.0,
	     "status": "hooked",
	     "timestamps": {
	         "chained": "xxxx-xx-xx xx:xx:xx",
	         "created": "2018-03-17 23:13:30",
	         "hooked": "2018-03-17 23:13:30",
	         "validated": "2018-03-17 23:13:30"
	     }
	 }
	$ 2018-xx-xx xx:xx:xx RRC Storing >> Node releasing database...

By running ***contract-reproducible.yaml*** this time, we have the following block:

	 {
	     "contract": {
	         "container": "9d9785de14f8dfa7bccab81b56aaa816517125fd6a8e7ba5485d81422b3cfbc8",
	         "id": "d17f5947720df7bfa5ab16a3d94d2efc990df4bf0ae7ffcb335d0635e86941e1",
	         "inputs": "4a1d014c12a83283ecf3cd3d685bf9bd7cc94c6a58af46237dd5c08f9b85d927",
	         "outputs": {
	             "computed/pi": "d42997e6d918a969ee2addbc99cd46d447813e977e5c31d201a9b871f8a9d2d6"
	         },
	         "scope": "reproducible"
	     },
	     "genesis": false,
	     "hash": "12304a3edc18b5e1d7a3d3e819cb7dc56a92e475392f425f701b7073c7313cd6",
	     "last": true,
	     "nodes": {
	         "af471328fad0b5f33da62485f3e1a3177a31a03da51f3c827a20715edee9caf1": "confirmed"
	     },
	     "previous": "3f2d8f883817fd789d3f82dea37d6319e7717b4e606c59c94168edd99fca3988",
	     "reward": 35.0,
	     "status": "hooked",
	     "timestamps": {
	         "chained": "xxxx-xx-xx xx:xx:xx",
	         "created": "2018-03-17 23:48:32",
	         "hooked": "2018-03-17 23:48:32",
	         "validated": "2018-03-17 23:48:32"
	     }
	 }

By comparing the two previous blocks, one is forced to witness that while the first is
a genesis block, with a previous hash to null and the reward of 57. RRC, the second
has its previous hash being the one of the first and a reward of 35.0. It is important to
notice the nodes section. Both blocks have a confirmation for the current node for the two
contracts.
Now to obviously check how much reward this node made so far we run:

	  $  rrc node --summary
	  $ 2018-xx-xx xx:xx:xx RRC Node >> RRC Node >> Entering the cli node command...
	  $ 2018-xx-xx xx:xx:xx RRC Networking >> Fetching the RRC network public key...
	  $ 2018-xx-xx xx:xx:xx RRC Networking >> Error: Server return code [404]
	  $ 2018-xx-xx xx:xx:xx RRC Networking >> Tip: Try again later.
	  $ 2018-xx-xx xx:xx:xx RRC Storing >> Node accessing database...
	  $ 2018-xx-xx xx:xx:xx RRC Storing >> Node releasing database...
	  $ 2018-xx-xx xx:xx:xx RRC Node >> Error: Cannot reach the RRC network.
	  $ 2018-xx-xx xx:xx:xx RRC Node >> Warning: Requests to the network will most likely fail.
	  $ 2018-xx-xx xx:xx:xx RRC Node >> Tip: Please check that you have a reliable internet connexion.
	  $ 2018-xx-xx xx:xx:xx RRC Storing >> Node accessing database...
	  $ 2018-xx-xx xx:xx:xx RRC Node >>
	   {
	       "components": {
	           "computing": null,
	           "networking": null
	       },
	       "id": "af471328fad0b5f33da62485f3e1a3177a31a03da51f3c827a20715edee9caf1",
	       "localhost": true,
	       "rewards": 92.0,
	       "session": "unknown",
	       "status": "stopping",
	       "version": "0.1"
	   }
	  $ 2018-xx-xx xx:xx:xx RRC Storing >> Node releasing database...
	  $ 2018-xx-xx xx:xx:xx RRC Storing >> Node accessing database...
	  $ 2018-xx-xx xx:xx:xx RRC Networking >> Warning: Node running in localhost.
	  $ 2018-xx-xx xx:xx:xx RRC Networking >> Beware: Limited access to the RRC network.
	  $ 2018-xx-xx xx:xx:xx RRC Node >> Error: Could not achieve a proper handshake with the RRC network.
	  $ 2018-xx-xx xx:xx:xx RRC Node >> Warning: You will not be able to call network commands ['summary', 'price']
	  $ 2018-xx-xx xx:xx:xx RRC Storing >> Node releasing database...
	  $ 2018-xx-xx xx:xx:xx RRC Storing >> Node accessing database...
	  $ 2018-xx-xx xx:xx:xx RRC Storing >> Node releasing database...

You can concur with me that ***57.0 + 35.0*** makes a total of ***92.0*** RRC.

### Is pi-2 replicating pi?

To run the two replicate contract requests ***contract-replicable*** and ***contract-rejected***,
you must have a previous contract id to reference to for the outputs.
For this reason we recommend that you run a repeatable contract first then use the contract id to
update the any of the two replicate ones.
For example to run the ***contract-replicable*** you must:

  $ edit ***contract-repeatable*** inputs section.
  $ replace ***precision.zip*** by ***precision-2.zip***.
  $ replace the value in digest with: 83048598f51116a035456c500b2718e73b8fa6237ceedff3068043e4997bbc96
  $ rrc contract --submit /path/to/rrc-node/example/contract-repeatable.yaml
  $ ...
  $ xxxx-xx-xx xx:xx:xx RRC Computing >> Requesting the computation of contract [xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx].
  $ ...
  $ copy xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  $ edit ***contract-replicable*** outputs section.
  $ replace id_of_the_contract_replicated with xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  $ rrc contract --submit /path/to/rrc-node/example/contract-replicable.yaml
  $ then check the block when the contract is computed.
  $ rrc block
  $ You should have a replicate block added, confirmed and an increase of 40 RRC in the node rewards.
  $ rrc node --summary

The same process applies for ***contract-rejected*** except that the submited contract will be rejected since
***pi*** and ***pi-2*** do not produce the same results for ***precision 10***. In any case for localhost, the node
is always paid for its efforts.
We have to note that for the network version a block rejecting a contract execution does not mean reward.
The rewards on the network are based on the majority response. If the majority of nodes reject the contract,
then they will get the rewards while the minority won't.  These complexities as you can imagine have a delay
impact in the expected robust design of the network version.

#### Overview of a RRC block

The RRC network generate a blockchain that has the following structure for a block:

{
    "contract": {
        "container": "9d9785de14f8dfa7bccab81b56aaa816517125fd6a8e7ba5485d81422b3cfbc8",
        "id": "72ffbd1c31b36ebb75a9ff0cddbac02a0e9c2994ea632ecb0713e19d64702849",
        "inputs": "4a1d014c12a83283ecf3cd3d685bf9bd7cc94c6a58af46237dd5c08f9b85d927",
        "outputs": {
            "computed/pi": "d42997e6d918a969ee2addbc99cd46d447813e977e5c31d201a9b871f8a9d2d6"
        },
        "scope": "repeatable"
    },
    "genesis": true,
    "hash": "3f2d8f883817fd789d3f82dea37d6319e7717b4e606c59c94168edd99fca3988",
    "last": true,
    "nodes": {
        "af471328fad0b5f33da62485f3e1a3177a31a03da51f3c827a20715edee9caf1": "confirmed"
    },
    "previous": null,
    "reward": 57.0,
    "status": "hooked",
    "timestamps": {
        "chained": "xxxx-xx-xx xx:xx:xx",
        "created": "2018-03-17 23:13:30",
        "hooked": "2018-03-17 23:13:30",
        "validated": "2018-03-17 23:13:30"
    }
}
$ 2018-xx-xx xx:xx:xx RRC Storing >> Node releasing database...

By running ***contract-reproducible.yaml*** this time, we have the following block:

    {
        "contract": { <--- The section concerning the RRC contract.
            "container": "9d978...cfbc8",      <--- The digest of the container.
            "id": "d17f5...941e1",             <--- The id of the contract.
            "inputs": "4a1d0...5d927",         <--- The digest of the inputs compressed folder.
            "outputs": {                       <--- Filenames and digests of the produced files.
                "computed/pi": "d4299...9d2d6" <--- The computed/pi result and its digest.
            },
            "scope": "reproducible"            <--- The scope of the contract.
        },
        "genesis": false, <--- Is this the genesis block?
        "hash": "12304...13cd6", <--- The hash of the current block: Include only the contract section and the previous hash.
        "last": true, <--- Is this block the last one?
        "nodes": { <--- The nodes involves in confirming or rejecting the contract.
            "af471...9caf1": "confirmed"
        },
        "previous": "3f2d8...a3988", <--- The hash of the previous
        "reward": 35.0, <--- The rewards offered for computing this contract and agreeing with the majority.
        "status": "hooked", <--- The block status. Currently hooked as the last chain.
        "timestamps": { <--- The timestamps of the status evolution of the block.
            "chained": "xxxx-xx-xx xx:xx:xx",
            "created": "2018-xx-xx xx:xx:01",
            "hooked": "2018-xx-xx xx:xx:01",
            "validated": "2018-xx-xx xx:xx:01"
        }
    }

To have a broader sense of what a contract is in RRC please review the provide example contract of computing Pi.
The hash of a block is the SHA256 of the previous block hash and the contract content.
A block status starts as ***created*** when the contract enter the postexecuting state, then when the result is validated as
confirmed or rejected, the status moves to ***validated*** and finally when the new its hash is computed from the previous hash,
it is ***hooked***. When a new block is added to the latest block, the field latest goes to false and the status moves to
***chained*** meaning that the block has a previous and a next.
The genesis block is the only one that has a previous to null.
Why Pi? Because we intend to use the repeatable contract computation as the genesis block for the network RRC deployment.

Beware: We are still working on a solid test suite. So if you encounter any issue please email me at faical.congo@nist.gov or
yannick.congo@gmail.com. I will try to assess your issues as quick as possible.
Another note is that this code is on research state. It is a proof of concept that a permissioned blockchain based smart contract
is an actual thing that can be used as an alternative to drive incentives into more corroboration in computational findings.
We have not addressed the question of rating here. But a biproduct of such as system is that researcher are accountable based
on a rating that grows good the more corroboration they have on their finding and worse the less corroboration they have based
on the number of paper they publish.
