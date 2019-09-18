import zmq
import logging
from random import randint

from config import *
from const import *
from SmartHomeTraderWrapper import SmartHomeTraderWrapper

class SmartHomeTraderTesting(SmartHomeTraderWrapper):
  def __init__(self, name):
    self.ledger = zmq.Context().socket(zmq.REQ)
    self.ledger.connect(LEDGER_ADDRESS)
    self.nextEvent = 0
    super(SmartHomeTraderTesting, self).__init__(name)
          
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
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  trader = SmartHomeTraderTesting("home" + str(randint(0,100)))
  trader.run()

    
