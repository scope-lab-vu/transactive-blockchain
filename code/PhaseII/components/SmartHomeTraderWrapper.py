import zmq
import logging
import sys
from time import time, sleep
from random import random

from config import *
from EthereumClient import EthereumClient
from MatchingContract import MatchingContract
from Grafana.config import Config
from Grafana.dbase import Database


POLLING_INTERVAL = 1 # seconds

class SmartHomeTraderWrapper:
  def __init__(self, prosumer_id, net_production, ip, port):
    self.prosumer_id = prosumer_id
    self.net_production = net_production
    self.selling_offers = set()
    self.buying_offers = set()
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    contract_address = self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port)
    self.account = client.accounts()[0] # use the first owned address
    self.contract = MatchingContract(client, contract_address)
    logging.info("Registering with the smart contract...")
    self.contract.registerProsumer(self.account, prosumer_id, PROSUMER_FEEDER[prosumer_id])
    self.dbase = Database()
    self.role = None
    super(SmartHomeTraderWrapper, self).__init__()

  def run(self):
    current_time = time()
    time_interval = int(current_time - self.epoch) // INTERVAL_LENGTH
    next_polling = current_time + POLLING_INTERVAL
    next_prediction = self.epoch + (time_interval + 1) * INTERVAL_LENGTH 
    interval_trades = {}
    # we stop after the END_INTERVAL
    while time_interval <= END_INTERVAL:
      current_time = time()
      if current_time > next_polling:
        logging.debug("Polling events...")
        next_polling = current_time + POLLING_INTERVAL
        for event in self.contract.poll_events():
          params = event['params']
          name = event['name']
          if (name == "BuyingOfferPosted") and (params['prosumer'] == self.prosumer_id):
            self.buying_offers.add(params['ID'])
            logging.info("{}({}).".format(name, params))
          elif (name == "SellingOfferPosted") and (params['prosumer'] == self.prosumer_id):
            self.selling_offers.add(params['ID'])
            logging.info("{}({}).".format(name, params))
          elif (name == "TradeAdded") and ((params['sellerID'] in self.selling_offers) or (params['buyerID'] in self.buying_offers)):
            logging.info("{}({}).".format(name, params))
          elif name == "Finalized":
            finalized = params['interval']
            logging.info("interval finalized : {}".format(finalized))
            interval_trades[finalized] = []
          elif (name == "TradeFinalized") and ((params['sellerID'] in self.selling_offers) or (params['buyerID'] in self.buying_offers)):
            logging.info("{}({}).".format(name, params))
            finalized = params['time']
            power = params['power']
            interval_trades[finalized].append(power)
            self.dbase.log(finalized,self.role,self.prosumer_id,sum(interval_trades[finalized]))

      if current_time > next_prediction:
        self.post_offers(time_interval)
        time_interval += 1
        next_prediction += INTERVAL_LENGTH
      sleep(max(min(next_prediction, next_polling) - time(), 0))
    
  def post_offers(self, time_interval):
    remaining_offers = []
    logging.info("Posting offers for interval {}...".format(time_interval))
    for offer in self.net_production:
      if offer['end'] < time_interval: # offer in the past, discard it
        pass
      elif offer['start'] <= time_interval + PREDICTION_WINDOW: # offer in near future, post it
        if offer['energy'] < 0:
          self.role = "consumer"
          logging.info("postBuyingOffer({}, {}, {}, {})".format(self.prosumer_id, offer['start'], offer['end'], -offer['energy']))
          self.contract.postBuyingOffer(self.account, self.prosumer_id, offer['start'], offer['end'], -offer['energy'])
        else:
          self.role = "producer"
          logging.info("postSellingOffer({}, {}, {}, {})".format(self.prosumer_id, offer['start'], offer['end'], offer['energy']))
          self.contract.postSellingOffer(self.account, self.prosumer_id, offer['start'], offer['end'], offer['energy'])
      else: # offer in far future, post it later
        remaining_offers.append(offer)
    self.net_production = remaining_offers
    logging.info("Offers posted.")
  
  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)
    response = self.dso.recv_pyobj()
    self.epoch = time() - response['time']
    contract_address = response['contract']
    logging.info("Contract address: " + contract_address)
    return contract_address

def read_data(prosumer_id):
  logging.info("Reading net production values...")
  feeder = int(prosumer_id / 100)
  prosumer = prosumer_id % 100
  with open(DATA_PATH + "prosumer_{}.csv".format(prosumer_id), "rt") as fin:
    line = next(fin)
    data = []
    for line in fin:
      try:
        fields = line.split(',')
        data.append({
          'start': int(fields[0]), 
          'end': int(fields[1]),
          'energy': int(1000 * float(fields[2]))
        })
      except Exception:
        pass
    if not len(data):
      raise Exception("No values found in data file!") 
    logging.info("Read {} values.".format(len(data)))
    return data

def test_data(prosumer_id):
  logging.info("Generating random test data...")
  return [{
    'start': t,
    'end': t,
    'energy': int(random() * 1000 - 500)} for t in range(10)]

if __name__ == "__main__":
  prosumer_id = 101
  ip = None
  port = None
  if len(sys.argv) > 1:
    prosumer_id = int(sys.argv[1])
    if prosumer_id < 101: 
      raise Exception("Format of prosumer identifier is FPP, where F and PP are the number of feeder and prosumer, respectively.")
  if len(sys.argv) > 2:
    ip = sys.argv[2]
  if len(sys.argv) > 3:
    port = sys.argv[3]
  logging.basicConfig(format='%(asctime)s / prosumer {} / %(levelname)s: %(message)s'.format(prosumer_id), level=logging.INFO)
  data = read_data(prosumer_id)
  trader = SmartHomeTraderWrapper(prosumer_id, data, ip, port) 
  trader.run()

    
