import zmq
import logging
import sys

from config import *
from EthereumClient import EthereumClient

class SmartHomeTraderWrapper:
  def __init__(self, prosumer_id, net_production, ip, port):
    self.net_production = net_production
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    self.client = EthereumClient(ip=ip, port=port)
    self.account = self.client.get_addresses()[0] # use the first owned address
    super(SmartHomeTraderWrapper, self).__init__(name)

  def run():
    # post all offers
    logging.info("Posting offers...")
    for t in range(len(net_production)):
      if net_production[t] < 0:
        self.postBuyingOffer(prosumer_id, t, t, -net_production[t])
      else:
        self.postSellingOffer(prosumer_id, t, t, net_production[t])
    logging.info("Offers posted.")
  
  def postBuyingOffer(self, prosumer, startTime, endTime, energy):
    logging.info("postBuyingOffer({}, {}, {}, {})".format(prosumer, startTime, endTime, energy))
    data = "0xc37df44e" + 
      EthereumClient.encode_uint(prosumer) + 
      EthereumClient.encode_uint(startTime) +
      EthereumClient.encode_uint(endTime) +
      EthereumClient.encode_uint(energy)
    self.client.transaction(self.account, data, self.contractAddress)

  def postSellingOffer(self, prosumer, startTime, endTime, energy):
    logging.info("postSellingOffer({}, {}, {}, {})".format(prosumer, startTime, endTime, energy))
    data = "0x8375ced0" + 
      EthereumClient.encode_uint(prosumer) + 
      EthereumClient.encode_uint(startTime) +
      EthereumClient.encode_uint(endTime) +
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
  with open(DATA_PATH + "TODO.csv", "rt") as fin:
    line = next(fin)
    # TODO: data format?
    data = [int(1000 * float(line.split(',')[prosumer_id])) for line in fin]
    logging.info("Read {} values.".format(len(data)))
    return data

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
  data = read_data2(prosumer_id)
  trader = SmartHomeTraderWrapper(prosumer_id, data, ip, port) 
  trader.run()

    
