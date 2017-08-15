import zmq
import logging

from config import *
from DSO import DSO
from gethRPC import gethRPC, encode_address, encode_uint, encode_int, get_addresses

class DSOWrapper(DSO): 
  def __init__(self):
    self.contractAddress = CONTRACT_ADDRESS
    self.account = get_addresses()[0]
    super(DSOWrapper, self).__init__()
    logging.info("Test result: " + str(gethRPC("eth_sendTransaction", params=[{'data': "0xf8a8fd6d", 'to': self.contractAddress, 'from': self.account}])))
    
  def run(self):
    logging.info("Entering main function...")
    trader = zmq.Context().socket(zmq.REP)
    trader.bind(DSO_ADDRESS)
    logging.info("Listening for traders...")
    while True:
      msg = trader.recv_pyobj()
      logging.info("withdraw_assets({})".format(msg))
      try:
        result = self.withdraw_assets(msg['prosumer'], msg['auth'], msg['asset'], msg['financial'], msg['address'])
      except Exception as e:
        logging.exception(e)
        result = "Malformed message."
      logging.info(result)
      trader.send_pyobj(result)
            
  def sendEther(self, address):
    # TODO: check this, especially the amount of Ether
    result = gethRPC("eth_sendTransaction", params=[{'to': address, 'value': "0xffffff", 'from': self.account}])
    logging.info(result)

  # contract function calls 

  def addFinancialBalance(self, address, amount):
    logging.info("addFinancialBalance({}, {})".format(address, amount))
    data = "0x3b719dc0" + encode_address(address) + encode_uint(amount)
    result = gethRPC("eth_sendTransaction", params=[{'data': data, 'to': self.contractAddress, 'from': self.account}])
    logging.info("Result: " + result)

  def addEnergyAsset(self, address, power, start, end):
    logging.info("addEnergyAsset({}, {})".format(address, power, start, end))
    data = "0x23b87507" + encode_address(address) + encode_int(power) + encode_uint(start) + encode_uint(end)
    result = gethRPC("eth_sendTransaction", params=[{'data': data, 'to': self.contractAddress, 'from': self.account}])
    logging.info("Result: " + result)
    
if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  dso = DSOWrapper()
  dso.run()

