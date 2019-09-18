import zmq
import logging
import sys
from time import time, sleep
from threading import Thread

from config import *
from EthereumClient import EthereumClient
from ResourceAllocationContract import ResourceAllocationContract

import pprint

class Directory:
  def __init__(self, gethip, gethport, DIRECTORY_IP):
      logging.debug("gethip: %s, type: %s" %(gethip, type(gethip)))
      self.client = EthereumClient(ip=gethip, port=gethport)
      logging.debug("client: %s" %self.client)
      self.account = self.client.accounts()[0] # use the first owned address
      logging.debug("account: %s" %self.account)
      self.deploy_contract()
      logging.debug("contract deployed")
      super(Directory, self).__init__()

  def finalizer(self):
    logging.info("Finalizer thread starting...")
    next_interval = START_INTERVAL # must be in sync with the starting interval of the smart contract
    next_finalization = time() + INTERVAL_LENGTH
    while True:
    #   sleep(next_finalization - time())
    #   next_finalization += INTERVAL_LENGTH
      print("Press c ENTER to close or f ENTER to finalize")
      cmd = input("Press Enter to continue")
      if cmd == "c":
          self.contract.close(self.account)
      if cmd =="f":
          logging.info("Finalizing interval {}".format(next_interval))
          self.contract.finalize(self.account)
          next_interval += 1

  def run(self):
    logging.info("Entering main function...")
    thread = Thread(target=self.finalizer)
    thread.start()
    client = zmq.Context().socket(zmq.REP)
    client.bind("tcp://%s:10001" %DIRECTORY_IP)
    # client.bind('tcp://127.0.0.1:10001')
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
    #pprint.pprint(BYTECODE)
    # use command function because we need to get the contract address later
    # receiptID = self.client.command("eth_sendTransaction", params=[{'data': BYTECODE, 'from': self.account, 'gas': TRANSACTION_GAS}])
    # logging.info("Transaction receipt: " + receiptID)
    receiptID = None
    while True:
      if not receiptID:
          logging.info("submit contract")
          receiptID = self.client.command("eth_sendTransaction", params=[{'data': BYTECODE, 'from': self.account, 'gas': TRANSACTION_GAS}], verbose=True)
          logging.info("Transaction receipt: " + receiptID)
      else:
          sleep(5)
          logging.info("Waiting for contract to be mined... (block number: {})".format(self.client.command("eth_blockNumber", params=[])))
          receipt = self.client.command("eth_getTransactionReceipt", params=[receiptID])
          if receipt is not None:
              self.contract_address = receipt['contractAddress']
              break
    self.contract = ResourceAllocationContract(self.client, self.contract_address)
    logging.info("Contract address: " + self.contract_address)

if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.DEBUG)
  ip = None
  port = None
  if len(sys.argv) > 1:
    ip = sys.argv[1]
  if len(sys.argv) > 2:
    port = sys.argv[2]
  if len(sys.argv) > 3:
      DIRECTORY_IP = sys.argv[3]
  directory = Directory(ip, port,DIRECTORY_IP)
  directory.run()
