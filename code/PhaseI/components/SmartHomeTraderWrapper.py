import zmq
import logging
import sys
from time import time, sleep

from config import *
from const import *
from SmartHomeTrader import SmartHomeTrader
from EthereumClient import EthereumClient

POLLING_INTERVAL = 1 # seconds

class SmartHomeTraderWrapper(SmartHomeTrader):
  def __init__(self, name, net_production, ip, port):
    self.net_production = net_production
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Creating event filter...")
    self.client = EthereumClient(ip=ip, port=port)
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
        logging.debug("Polling events...")
        next_polling = current_time + POLLING_INTERVAL
        self.poll_events()
      sleep(min(next_prediction - current_time, next_polling - current_time))

  def net_production_predictor(self, timestep):
    return self.net_production[timestep % len(self.net_production)]
      
  def get_addresses(self, num_addresses):
    logging.info("Querying own addresses...")
    return self.client.get_addresses()
      
  def poll_events(self):
    for event in self.client.filter.poll_events():
      logging.info("Event: " + str(event))
      params = event['params']
      name = event['name']
      if name == "FinancialAdded":
        self.FinancialAdded(params['address'], params['amount'])
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
      'request': "withdraw_assets", 
      'params': {
        'prosumer': self.name, 
        'auth': "password", 
        'asset': asset, 
        'address': address, 
        'financial': financial 
      }
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)    
    response = self.dso.recv_pyobj()
    logging.info(response)

  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)
    self.contractAddress = self.dso.recv_pyobj()
    logging.info("Contract address: " + self.contractAddress)
        
  # contract function calls
  
  def postOffer(self, address, assetID, price):
    logging.info("postOffer({}, {}) using address {}".format(assetID, price, address))
    data = "0xed7272e2" + EthereumClient.encode_uint(assetID) + EthereumClient.encode_uint(price)
    self.client.transaction(address, data, self.contractAddress)

  def acceptOffer(self, address, offerID, assetID):
    logging.info("acceptOffer({}, {}) using address {}".format(offerID, assetID, address))
    data = "0xf1edd7e2" + EthereumClient.encode_uint(offerID) + EthereumClient.encode_uint(assetID)
    self.client.transaction(address, data, self.contractAddress)

def read_data(prosumer_id):
  logging.info("Reading net production values...")
  with open(DATA_PATH + "day_power_profile.csv", "rt") as fin:
    lines = fin.readlines()
    if lines[3].split(',')[prosumer_id] == "": # if peak production value is missing, prosumer is consumer
      mult = -10
    else: # otherwise, prosumer is producer
      mult = 10
    data = [int(mult * float(line.split(',')[prosumer_id])) for line in lines[5:]]
    logging.info("Read {} values.".format(len(data)))
    return data

def read_data2(prosumer_id):
  logging.info("Reading net production values...")
  with open(DATA_PATH + "day_power_profile2.csv", "rt") as fin:
    line = next(fin)
    name = line.split(',')[prosumer_id]
    data = [int(10 * float(line.split(',')[prosumer_id])) for line in fin]
    logging.info("Read {} values.".format(len(data)))
    return (name, data)

if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  prosumer_id = 1
  ip = None
  port = None
  if len(sys.argv) > 1:
    prosumer_id = int(sys.argv[1])
    if prosumer_id < 1: 
      raise Exception("Prosumer ID must be greater than zero!")
  if len(sys.argv) > 2:
    ip = sys.argv[2]
  if len(sys.argv) > 3:
    port = sys.argv[3]
  (name, data) = read_data2(prosumer_id)
  trader = SmartHomeTraderWrapper(name, data, ip, port) 
  trader.run()

    
