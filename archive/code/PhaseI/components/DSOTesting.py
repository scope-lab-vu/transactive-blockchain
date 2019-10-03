import zmq
import logging

from config import *
from DSOWrapper import DSOWrapper
  
class DSOTesting(DSOWrapper): 
  def __init__(self):
    self.ledger = zmq.Context().socket(zmq.REQ)
    self.ledger.connect(LEDGER_ADDRESS)
    super(DSOTesting, self).__init__()
                
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
    
  # contract function calls 

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
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  dso = DSOTesting()
  dso.run()

