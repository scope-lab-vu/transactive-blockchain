import zmq
import logging
import sys
from time import time, sleep
from threading import Thread

from config import *
from EthereumClient import EthereumClient
from MatchingContract import MatchingContract

class DSOWrapper:
  def __init__(self, ip, port):
    self.client = EthereumClient(ip=ip, port=port)
    self.account = self.client.accounts()[0] # use the first owned address
    self.deploy_contract()
    super(DSOWrapper, self).__init__()

  def finalizer(self):
    logging.info("Finalizer thread starting...")
    next_interval = START_INTERVAL # must be in sync with the starting interval of the smart contract
    next_finalization = time() + INTERVAL_LENGTH
    while True:
      sleep(next_finalization - time())
      next_finalization += INTERVAL_LENGTH
      logging.info("Finalizing interval {}".format(next_interval))
      self.contract.finalize(self.account, next_interval)
      next_interval += 1

  def run(self):
    logging.info("Entering main function...")
    thread = Thread(target=self.finalizer)
    thread.start()
    trader = zmq.Context().socket(zmq.REP)
    trader.bind(DSO_ADDRESS)
    t = time()
    logging.info("START_INTERVAL %s" %(START_INTERVAL))
    logging.info("time %s" %(t))
    epoch = t - START_INTERVAL * INTERVAL_LENGTH
    logging.info("epoch %s" %(epoch))
    logging.info("Listening for traders and solvers...")
    while True:
      msg = trader.recv_pyobj()
      if msg['request'] == "query_contract_address":
        logging.info("query_contract_address()")
        logging.info("time elapsed since epoch %s" %(time()-epoch))
        trader.send_pyobj({'contract': self.contract_address, 'time': time() - epoch})
      else:
        logging.error("Unknown request: " + msg['request'])
        trader.send_pyobj("Unknown request!")

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
    self.contract = MatchingContract(self.client, self.contract_address)
    self.contract.setup(self.account, MICROGRID.C_ext, MICROGRID.C_int, START_INTERVAL)
    logging.info("Contract address: " + self.contract_address)
if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  ip = None
  port = None
  if len(sys.argv) > 1:
    ip = sys.argv[1]
  if len(sys.argv) > 2:
    port = sys.argv[2]
  dso = DSOWrapper(ip, port)
  dso.run()
