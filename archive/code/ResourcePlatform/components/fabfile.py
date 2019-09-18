import fabric.api as fabi
import fabric.operations as fop
import sys
sys.path.append('../tests/manual')
from hosts import *
import time

fabi.env.key_filename = '~/.ssh/cluster_2018_9_10'

fabi.env.skip_bad_hosts = True
fabi.env.warn_only = True
fabi.env.abort_on_prompts=True

from EthereumClient import EthereumClient
from ResourceAllocationContract import ResourceAllocationContract
import logging
logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.DEBUG)
from config import *
import docker


@fabi.task
def postContract(gethip, gethport):
    client = EthereumClient(ip=gethip, port=gethport)
    account = client.accounts()[0] # use the first owned address

    logging.info("Deploying contract...")
    #pprint.pprint(BYTECODE)
    # use command function because we need to get the contract address later
    receiptID = client.command("eth_sendTransaction", params=[{'data': BYTECODE, 'from': account, 'gas': TRANSACTION_GAS}])
    logging.info("Transaction receipt: " + receiptID)
    while True:
        time.sleep(5)
        logging.info("Waiting for contract to be mined... (block number: {})".format(client.command("eth_blockNumber", params=[])))
        receipt = client.command("eth_getTransactionReceipt", params=[receiptID])
        # logging.debug("receipt: %s" %receipt)
        if receipt is not None:
            contract_address = receipt['contractAddress']
            logging.debug("contract_address: %s" %contract_address)
            break
    contract = ResourceAllocationContract(client, contract_address)
    logging.info("Contract address: " + contract_address)
    client.exit()

@fabi.task
def postJob():
    jobpath = "/home/riaps/projects/transactive-blockchain/code/ResourcePlatform/jobs/job0"
    jobname = "eiselesr/job0"

    doc_client = docker.from_env()
    doc_client.login(username='eiselesr', password='eiselesr@docker')
    image = doc_client.images.build(path=jobpath, tag=jobname)[0]
    for line in doc_client.images.push(jobname, stream=True):
        print (line)



@fabi.task
def testHash(gethip, gethport, contract_address='0x88ef3213c6c3c48d3f8b10b7a4304a1f5eb9400d',
             jobname="eiselesr/job0"):
    client = EthereumClient(ip=gethip, port=gethport)
    account = client.accounts()[0] # use the first owned address
    contract = ResourceAllocationContract(client, contract_address)

    APIclient = docker.APIClient(base_url='unix://var/run/docker.sock')
    image_dict = APIclient.inspect_image(jobname)
    IDsha = image_dict["Id"].split(":")[1]
    intIDsha = int(IDsha, 16)

    logging.info("IDsha:%s" %IDsha)
    logging.info("intIDsha:%s" %intIDsha)
    contract.call_func(account, "testHash", "uint256",intIDsha)

    logging.info("Entering main loop...")

    next_polling = time.time()

    loop = True
    while loop:
      logging.debug("Polling events...")
      for event in contract.poll_events():
          params = event['params']
          name = event['name']
          if (name == "Debug"):
              logging.info("{}({}).".format(name, params))
              sha = hex(params['e256'])
              logging.info(sha)
              loop = False
      next_polling += 3#POLLING_INTERVAL
      print("next_polling: %s" %next_polling)
      time.sleep(max(next_polling - time.time(), 0))
    client.exit()
    # print("TEST")


# self.directory = zmq.Context().socket(zmq.REQ)
# self.directory.connect(DIRECTORY_ADDRESS)
# self.logger.info("Directory connected ({}).".format(self.directory))
# contract_address = self.query_contract_address()
# self.logger.info("Setting up connection to Ethereum client...")
# client = EthereumClient(ip=ip, port=port)
# self.account = client.accounts()[0] # use the first owned address
# self.contract = ResourceAllocationContract(client, contract_address)
#
# self.contract.updateJobOffer(from_account=self.account, offerID=params['offerID'],
#                              architecture=self.archTypes[offer.arch], reqCPU=50, #MIPS
#                              reqRAM=50, reqStorage=offer.storage, imageHash = offer.IDsha)
