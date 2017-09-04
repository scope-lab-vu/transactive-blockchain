import zmq
import logging
import sys
from time import sleep

from config import *
from DSO import DSO
from EthereumClient import EthereumClient

class DSOWrapper(DSO): 
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
      if msg['request'] == "withdraw_assets":
        logging.info("withdraw_assets({})".format(msg))
        params = msg['params']
        try:
          result = self.withdraw_assets(params['prosumer'], params['auth'], params['asset'], params['financial'], params['address'])
        except Exception as e:
          logging.exception(e)
          result = "Error occurred during message processing."
        logging.info(result)
        trader.send_pyobj(result)
      elif msg['request'] == "query_contract_address":
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
            
  def sendEther(self, address):
    # TODO: this should also be implemented using the transaction interface of EthereumClient
    # TODO: check this, especially the amount of Ether
    logging.info("sendEther()")
    result = self.client.command("eth_sendTransaction", params=[{'to': address, 'value': "0xffffff", 'from': self.account}])
    logging.debug("Result: " + result)

  # contract function calls 
  
  def addFinancialBalance(self, address, amount):
    logging.info("addFinancialBalance({}, {})".format(address, amount))
    data = "0x3b719dc0" + EthereumClient.encode_address(address) + EthereumClient.encode_uint(amount)
    self.client.transaction(self.account, data, self.contractAddress)

  def addEnergyAsset(self, address, power, start, end):
    logging.info("addEnergyAsset({}, {}, {}, {})".format(address, power, start, end))
    data = "0x23b87507" + EthereumClient.encode_address(address) + EthereumClient.encode_int(power) + EthereumClient.encode_uint(start) + EthereumClient.encode_uint(end)
    self.client.transaction(self.account, data, self.contractAddress)
    
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

