import zmq
import logging
from time import time, sleep
from random import randint

from config import *
from const import *
from SmartHomeTrader import SmartHomeTrader

POLLING_INTERVAL = 0.5

class SmartHomeTraderWrapper(SmartHomeTrader):
  def __init__(self, name):
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    self.ledger = zmq.Context().socket(zmq.REQ)
    self.ledger.connect(LEDGER_ADDRESS)
    self.nextEvent = 0
    super(SmartHomeTraderWrapper, self).__init__(name)
    
  def run(self):
    next_prediction = time() + TIME_INTERVAL
    next_polling = time() + POLLING_INTERVAL
    while True:
      current_time = time()
      if current_time > next_prediction:
        next_prediction = current_time + TIME_INTERVAL
        self.predict()
      if current_time > next_polling:
        next_polling = current_time + POLLING_INTERVAL
        self.poll_events()
      sleep(min(next_prediction - current_time, next_polling - current_time))
      
  def poll_events(self):
    msg = { 
      'function': 'pollEvents', 
      'params': {
        'nextEvent': self.nextEvent 
      }
    }
    logging.debug(msg)
    self.ledger.send_pyobj(msg)    
    response = self.ledger.recv_pyobj()
    logging.debug(response)
    self.nextEvent = response['nextEvent']
    for (name, params) in response['events']:
      if name == "AssetAdded":
        self.AssetAdded(params['address'], params['assetID'], params['power'], params['start'], params['end'])
      elif name == "FinancialAdded":
        self.FinancialAdded(params['address'], params['amount'])
      elif name == "OfferPosted":
        self.OfferPosted(params['offerID'], params['power'], params['start'], params['end'], params['price'])
      elif name == "OfferRescinded":
        self.OfferRescinded(params['offerID'])
      elif name == "OfferAccepted":
        self.OfferAccepted(params['offerID'], params['assetID'], params['transPower'], params['transStart'], params['transEnd'], params['price'])
      
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
        'sender': address,
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
        'sender': address,
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
  trader = SmartHomeTraderWrapper("home" + str(randint(0,100)))
  trader.run()

    
