import zmq
import logging
import sys
from random import random

from config import *
from EthereumClient import EthereumClient
from MatchingContract import MatchingContract

class SmartHomeTraderWrapper:
  def __init__(self, prosumer_id, net_production, ip, port):
    self.prosumer_id = prosumer_id
    self.net_production = net_production
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    contract_address = self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port)
    self.account = client.accounts()[0] # use the first owned address
    self.contract = MatchingContract(client, contract_address)
    super(SmartHomeTraderWrapper, self).__init__()

  def run(self):
    time_interval = START_INTERVAL
    next = time()
    while True:
      self.post_offers(self, time_interval)
      time_interval += 1
      next += INTERVAL_LENGTH
      sleep(max(next - time(), 0))
    
  def post_offers(self, time_interval):
    remaining_offers = []
    logging.info("Posting offers...")
    for offer in self.net_production:
      if offer['start'] <= time_interval + PREDICTION_WINDOW: # offer in near future, post it
        if offer['energy'] < 0:
          self.contract.postBuyingOffer(self.account, self.prosumer_id, offer['start'], offer['end'], -offer['energy'])
        else:
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
    contract_address = self.dso.recv_pyobj()
    logging.info("Contract address: " + self.contract_address)
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
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
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
  data = read_data(prosumer_id)
  trader = SmartHomeTraderWrapper(prosumer_id, data, ip, port) 
  trader.run()

    
