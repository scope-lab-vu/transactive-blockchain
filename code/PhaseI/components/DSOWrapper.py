import zmq
import logging
from time import sleep

from config import *
from DSO import DSO
from Geth import Geth

class DSOWrapper(DSO): 
  def __init__(self):
    self.geth = Geth()    
    self.account = self.geth.get_addresses()[0]
    self.deploy_contract()
    super(DSOWrapper, self).__init__()
    # TODO: remove testing code once event filtering works reliably
    #logging.info("Test result: " + str(self.geth.command("eth_sendTransaction", params=[{'data': "0xf8a8fd6d", 'to': self.contractAddress, 'from': self.account}])))
    
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
          result = "Malformed message."
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
    receiptID = self.geth.command("eth_sendTransaction", params=[{"data": BYTECODE, "gas": '0x4300000', "from": self.account}])
    logging.info("Transaction receipt: " + receiptID)
    while True:
      sleep(5)
      logging.info("Block number: " + self.geth.command("eth_blockNumber", params=[]))
      receipt = self.geth.command("eth_getTransactionReceipt", params=[receiptID])
      if receipt is not None:
        self.contractAddress = receipt['contractAddress']
        break
    logging.info("Contract address: " + self.contractAddress)    
            
  def sendEther(self, address):
    # TODO: check this, especially the amount of Ether
    logging.info("sendEther()")
    result = self.geth.command("eth_sendTransaction", params=[{'to': address, 'value': "0xffffff", 'from': self.account}])
    logging.info("Result: " + result)

  # contract function calls 
  
  def printReceipt(self, receiptID):
    while True:
      sleep(1)
      logging.info("Block number: " + self.geth.command("eth_blockNumber", params=[]))
      receipt = self.geth.command("eth_getTransactionReceipt", params=[receiptID])
      if receipt is not None:              
        logging.info(receipt)
        break       

  def addFinancialBalance(self, address, amount):
    logging.info("addFinancialBalance({}, {})".format(address, amount))
    data = "0x3b719dc0" + Geth.encode_address(address) + Geth.encode_uint(amount)
    result = self.geth.command("eth_sendTransaction", params=[{'data': data, 'to': self.contractAddress, 'from': self.account, 'gas': "0x4300000"}])
    logging.info("Result: " + result)

  def addEnergyAsset(self, address, power, start, end):
    logging.info("addEnergyAsset({}, {}, {}, {})".format(address, power, start, end))
    data = "0x23b87507" + Geth.encode_address(address) + Geth.encode_int(power) + Geth.encode_uint(start) + Geth.encode_uint(end)
    result = self.geth.command("eth_sendTransaction", params=[{'data': data, 'to': self.contractAddress, 'from': self.account, 'gas': "0x4300000"}])
    logging.info("Result: " + result)
    
if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  dso = DSOWrapper()
  dso.run()

