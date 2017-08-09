import zmq
import logging
from time import time, sleep

from config import *
from const import *
from SmartHomeTrader import SmartHomeTrader

class SmartHomeTraderWrapper(SmartHomeTrader):
  def __init__(self, name):
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    self.ledger = zmq.Context().socket(zmq.REQ)
    self.ledger.connect(LEDGER_ADDRESS)
    super(SmartHomeTraderWrapper, self).__init__(name)
    
  def run(self):
    next_prediction = time() + TIME_INTERVAL
    while True:
      sleep(TIME_INTERVAL * 0.1)
      current_time = time()
      if current_time > next_prediction:
        next_prediction = current_time + TIME_INTERVAL
        self.predict()
      
  # DSO message sender 
  def withdraw_assets(self, address, asset, financial):
    # TODO: provide auth
    msg = { 
      'prosumer': self.name, 
      'auth': "password", 
      'asset': asset, 
      'address': address, 
      'financial': financial 
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)    
    response = self.dso.recv_pyobj()
    logging.info(response)
    
  # contract function calls
  def postOffer(self, address, assetID, price):
    msg = { 
      'function': 'postOffer',
      'params': {
        'address': address,
        'assetID': assetID,
        'price': price
      }
    }
    logging.info(msg)
    self.ledger.send_pyobj(msg)
    response = self.ledger.recv_pyobj()
    logging.info(response)
   def acceptOffer(self, address, offerID, assetID):
    msg = { 
      'function': 'acceptOffer',
      'params': {
        'address': address,
        'offerID': offerID,
        'assetID': assetID
      }
    }
    logging.info(msg)
    self.ledger.send_pyobj(msg)
    response = self.ledger.recv_pyobj()
    logging.info(response)


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  trader = SmartHomeTraderWrapper("home1")
  trader.run()

    
