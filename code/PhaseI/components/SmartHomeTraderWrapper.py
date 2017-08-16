import zmq
import logging
import sys
from time import time, sleep

from config import *
from const import *
from SmartHomeTrader import SmartHomeTrader
from Filter import Filter
from Geth import Geth

POLLING_INTERVAL = 5 # seconds

class SmartHomeTraderWrapper(SmartHomeTrader):
  def __init__(self, name, net_production):
    self.net_production = net_production
    self.geth = Geth()
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    logging.info("DSO connected ({}).".format(self.dso))
    self.dso.connect(DSO_ADDRESS)
    self.contractAddress = CONTRACT_ADDRESS
    logging.info("Creating event filter...")
    self.filter = Filter()
    super(SmartHomeTraderWrapper, self).__init__(name)
    
  def run(self):
    logging.info("Entering main loop...")
    next_prediction = time() + TIME_INTERVAL
    next_polling = time() + POLLING_INTERVAL
    while True:
      current_time = time()
      if current_time > next_prediction:
        logging.info("Predicting net production for next time interval...")
        next_prediction = current_time + TIME_INTERVAL
        self.predict()
      if current_time > next_polling:
        logging.info("Polling events...")
        next_polling = current_time + POLLING_INTERVAL
        self.poll_events()
      sleep(min(next_prediction - current_time, next_polling - current_time))

  def net_production_predictor(self, timestep):
    return self.net_production[timestep % len(self.net_production)]
      
  def get_addresses(self, num_addresses):
    logging.info("Querying own addresses...")
    return self.geth.get_addresses()
      
  def poll_events(self):
    for event in self.filter.poll_events():
      logging.info("Event: " + str(event))
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
    logging.info("{}.postOffer({}, {})".format(address, assetID, price))
    data = "0xed7272e2" + Geth.encode_uint(assetID) + Geth.encode_uint(price)
    result = self.geth.command("eth_sendTransaction", params=[{'from': address, 'data': data, 'to': self.contractAddress}])
    logging.info("Result: " + result)

  def acceptOffer(self, address, offerID, assetID):
    logging.info("{}.acceptOffer({}, {})".format(address, offerID, assetID))
    data = "0xf1edd7e2" + Geth.encode_uint(offerID) + Geth.encode_uint(assetID)
    result = self.geth.command("eth_sendTransaction", params=[{'from': address, 'data': data, 'to': self.contractAddress}])
    logging.info("Result: " + result)

def read_data(prosumer_id):
  logging.info("Reading net production values...")
  with open(DATA_PATH + "day_power_profile.csv", "rt") as fin:
    lines = fin.readlines()
    if lines[3].split(',')[prosumer_id] == "": # if peak production value is missing, prosumer is consumer
      mult = -1
    else: # otherwise, prosumer is producer
      mult = 1
    data = [int(mult * float(line.split(',')[prosumer_id])) for line in lines[5:]]
    logging.info("Read {} values.".format(len(data)))
    return data

if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  if len(sys.argv) > 1:
    prosumer_id = int(sys.argv[1])
    if prosumer_id < 1: 
      print("Prosumer ID must be greater than zero!")
  else:
    prosumer_id = 1
  trader = SmartHomeTraderWrapper("prosumer_" + str(prosumer_id), read_data(prosumer_id)) 
  trader.run()

    
