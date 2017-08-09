import zmq
import logging

from config import *
from DSO import DSO
  
class DSOWrapper(DSO): 
  def __init__(self):
    self.ledger = zmq.Context().socket(zmq.REQ)
    self.ledger.connect(LEDGER_ADDRESS)
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
            
  # contract function calls 
  def sendEther(self, address):
    msg = { 
      'function': 'sendEther',
      'params': {
        'address': address,
        'amount': 1,
      }
    }
    logging.info(msg)
    self.ledger.send_pyobj(msg)
    response = self.ledger.recv_pyobj()
    logging.info(response)   
  def addFinancialBalance(self, address, amount):
    msg = { 
      'function': 'addFinancialBalance',
      'params': {
        'address': address,
        'amount': amount
      }
    }
    logging.info(msg)
    self.ledger.send_pyobj(msg)
    response = self.ledger.recv_pyobj()
    logging.info(response)
  def addEnergyAsset(self, address, power, start, end):
    msg = { 
      'function': 'addEnergyAsset',
      'params': {
        'address': address,
        'power': power,
        'start': start,
        'end': end
      }
    }
    logging.info(msg)
    self.ledger.send_pyobj(msg)
    response = self.ledger.recv_pyobj()
    logging.info(response)
    
if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  dso = DSOWrapper()
  dso.run()

