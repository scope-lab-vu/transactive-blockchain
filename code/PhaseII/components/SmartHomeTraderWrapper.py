import zmq
import logging
import sys
from random import random

from config import *
from EthereumClient import EthereumClient

class SmartHomeTraderWrapper:
  def __init__(self, prosumer_id, net_production, ip, port):
    self.prosumer_id = prosumer_id
    self.net_production = net_production
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    self.client = EthereumClient(ip=ip, port=port)
    self.account = self.client.get_addresses()[0] # use the first owned address
    super(SmartHomeTraderWrapper, self).__init__()

  def run(self):
    # post all offers
    logging.info("Posting offers...")
    for offer in self.net_production:
      if offer['energy'] < 0:
        self.postBuyingOffer(self.prosumer_id, offer['start'], offer['end'], -offer['energy'])
      else:
        self.postSellingOffer(self.prosumer_id, offer['start'], offer['end'], offer['energy'])
    logging.info("Offers posted.")
  
  def postBuyingOffer(self, prosumer, startTime, endTime, energy):
    logging.info("postBuyingOffer({}, {}, {}, {})".format(prosumer, startTime, endTime, energy))
    data = "0xc37df44e" + \
      EthereumClient.encode_uint(prosumer) + \
      EthereumClient.encode_uint(startTime) + \
      EthereumClient.encode_uint(endTime) + \
      EthereumClient.encode_uint(energy)
    self.client.transaction(self.account, data, self.contractAddress)

  def postSellingOffer(self, prosumer, startTime, endTime, energy):
    logging.info("postSellingOffer({}, {}, {}, {})".format(prosumer, startTime, endTime, energy))
    data = "0x8375ced0" + \
      EthereumClient.encode_uint(prosumer) + \
      EthereumClient.encode_uint(startTime) + \
      EthereumClient.encode_uint(endTime) + \
      EthereumClient.encode_uint(energy)
    self.client.transaction(self.account, data, self.contractAddress)

  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)
    self.contractAddress = self.dso.recv_pyobj()
    logging.info("Contract address: " + self.contractAddress)

def read_data(prosumer_id):
  logging.info("Reading net production values...")
  feeder = int(prosumer_id / 100)
  prosumer = prosumer_id % 100
  with open(DATA_PATH + "prosumer_{}.csv".format(prosumer_id), "rt") as fin:
    line = next(fin)
    data = []
    for line in fin:
      fields = line.split(',')
      data.append({
        'start': int(fields[0]), 
        'end': int(fields[1]),
        'energy': int(1000 * float(fields[2]))
      }) 
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

    
