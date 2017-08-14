import zmq
import logging
from time import time, sleep
from random import randint

from config import *
from const import *
from SmartHomeTrader import SmartHomeTrader
from Filter import Filter
from gethRPC import gethRPC, encode_uint, encode_int, get_addresses

POLLING_INTERVAL = 0.5

class SmartHomeTraderWrapper(SmartHomeTrader):
  def __init__(self, name):
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    self.contractAddress = CONTRACT_ADDRESS
    self.filter = Filter()
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
      
  def get_addresses(self, num_addresses):
    return get_addresses()
      
  def poll_events(self):
    for event in filter.poll_events():
      params = event['params']
      name = event['name']
      if name == "FinancialAdded":
        self.FinancialAdded(params['address'], param['amount'])
      elif name == "AssetAdded":
        self.AssetAdded(params['address'], params['assetID'], params['power'], params['start'], params['end'])
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
    data = "0xed7272e2" + encode_uint(assetID) + encode_uint(price)
    result = gethRPC("eth_sendTransaction", params=[{'from': address, 'data': data, 'to': self.contractAddress}])
    logging.info(result)

  def acceptOffer(self, address, offerID, assetID):
    data = "0xf1edd7e2" + encode_uint(offerID) + encode_uint(assetID)
    result = gethRPC("eth_sendTransaction", params=[{'from': address, 'data': data, 'to': self.contractAddress}])
    logging.info(result)

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  trader = SmartHomeTraderWrapper("home" + str(randint(0,100)))
  trader.run()

    
