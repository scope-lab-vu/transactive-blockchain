import zmq
import logging
import sys
from time import time, sleep

from config import *
from EthereumClient import EthereumClient

POLLING_INTERVAL = 1 # seconds

class SmartHomeTraderWrapper:
  def __init__(self, name, net_production, ip, port):
    self.net_production = net_production
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    self.client = EthereumClient(ip=ip, port=port)
    super(SmartHomeTraderWrapper, self).__init__(name)
  
  def postOffer(self, address, assetID, price):
    logging.info("postOffer({}, {}) using address {}".format(assetID, price, address))
    data = "0xed7272e2" + EthereumClient.encode_uint(assetID) + EthereumClient.encode_uint(price)
    self.client.transaction(address, data, self.contractAddress)

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

    
