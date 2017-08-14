import zmq
import logging

from config import *
from DSO import DSO
from gethRPC import gethRPC, encode_uint, encode_int

class DSOWrapper(DSO): 
  def __init__(self):
    self.contractAddress = CONTRACT_ADDRESS
    super(DSOWrapper, self).__init__()
    
  def run(self):
    trader = zmq.Context().socket(zmq.REP)
    trader.bind(DSO_ADDRESS)
    while True:
      msg = trader.recv_pyobj()
      logging.info("withdraw_assets({})".format(msg))
      try:
        result = self.withdraw_assets(msg['prosumer'], msg['auth'], msg['asset'], msg['financial'], msg['address'])
      except:
        result = "Malformed message."
      logging.info(result)
      trader.send_pyobj(result)
            
  def sendEther(self, address):
    # TODO: check this, especially the amount of Ether
    result = gethRPC("eth_sendTransaction", params=[{'to': address, 'value': "0xffffff"}])
    logging.info(result)

  # contract function calls 

  def addFinancialBalance(self, address, amount):
    data = "0x3b719dc0" + encode_uint(address) + encode_uint(amount)
    result = gethRPC("eth_sendTransaction", params=[{'data': data, 'to': self.contractAddress}])
    logging.info(result)

  def addEnergyAsset(self, address, power, start, end):
    data = "0x23b87507" + encode_uint(address) + encode_int(power) + encode_uint(start) + encode_uint(end)
    result = gethRPC("eth_sendTransaction", params=[{'data': data, 'to': self.contractAddress}])
    logging.info(result)
    
if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  dso = DSOWrapper()
  dso.run()

