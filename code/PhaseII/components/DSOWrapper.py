import zmq
import logging
import sys
from time import sleep

from config import *
from EthereumClient import EthereumClient

class DSOWrapper: 
  def __init__(self, ip, port):
    self.client = EthereumClient(ip=ip, port=port)    
    self.account = self.client.get_addresses()[0] # use the first owned address
    self.deploy_contract()
    super(DSOWrapper, self).__init__()
    
  def run(self):
    logging.info("Entering main function...")
    trader = zmq.Context().socket(zmq.REP)
    trader.bind(DSO_ADDRESS)
    logging.info("Listening for traders...")
    while True:
      msg = trader.recv_pyobj()
      if msg['request'] == "query_contract_address":
        logging.info("query_contract_address()")
        trader.send_pyobj(self.contractAddress)
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
        self.contractAddress = receipt['contractAddress']
        break
    logging.info("Contract address: " + self.contractAddress)                
    
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

