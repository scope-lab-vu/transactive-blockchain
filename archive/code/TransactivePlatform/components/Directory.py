import zmq
import logging
import sys
from time import time, sleep
from threading import Thread

from config import *
from EthereumClient import EthereumClient
from ResourceAllocationContract import ResourceAllocationContract

class Directory:
  def __init__(self, ip, port):
    self.client = EthereumClient(ip=ip, port=port)
    self.account = self.client.accounts()[0] # use the first owned address
    self.deploy_contract()
    super(Directory, self).__init__()

  def finalizer(self):
    logging.info("Finalizer thread starting...")
    next_interval = START_INTERVAL # must be in sync with the starting interval of the smart contract
    next_finalization = time() + INTERVAL_LENGTH
    while True:
      sleep(next_finalization - time())
      next_finalization += INTERVAL_LENGTH
      logging.info("Finalizing interval {}".format(next_interval))
      #self.contract.finalize(self.account)
      next_interval += 1

  def run(self):
    logging.info("Entering main function...")
    thread = Thread(target=self.finalizer)
    thread.start()
    client = zmq.Context().socket(zmq.REP)
    client.bind(DIRECTORY_ADDRESS)
    epoch = time() - START_INTERVAL * INTERVAL_LENGTH
    logging.info("Listening for clients...")
    while True:
      msg = client.recv_pyobj()
      if msg['request'] == "query_contract_address":
        logging.info("query_contract_address()")
        client.send_pyobj({'contract': self.contract_address, 'time': time() - epoch})
      else:
        logging.error("Unknown request: " + msg['request'])
        client.send_pyobj("Unknown request!")

  def deploy_contract(self):
    logging.info("Deploying contract...")
    # use command function because we need to get the contract address later
    receiptID = self.client.command("eth_sendTransaction", params=[{'data': BYTECODE, 'from': self.account, 'gas': TRANSACTION_GAS}])
    logging.info("Transaction receipt: " + receiptID)
    while True:
      sleep(5)
      logging.info("Waiting for contract to be mined... (block number: {})".format(self.client.command("eth_blockNumber", params=[])))
      receipt = self.client.command("eth_getTransactionReceipt", params=[receiptID])
      if receipt is not None:
        self.contract_address = receipt['contractAddress']
        break
    self.contract = ResourceAllocationContract(self.client, self.contract_address)
    self.contract.setup(self.account, NUM_TYPES, PRECISION, MAX_QUANTITY)
    logging.info("Contract address: " + self.contract_address)

if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  ip = None
  port = None
  if len(sys.argv) > 1:
    ip = sys.argv[1]
  if len(sys.argv) > 2:
    port = sys.argv[2]
  directory = Directory(ip, port)
  directory.run()
