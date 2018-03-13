import zmq
import logging
import sys
from time import time, sleep
from random import random

from config import *
from EthereumClient import EthereumClient
from ResourceAllocationContract import ResourceAllocationContract

POLLING_INTERVAL = 1 # seconds

class Prosumer:
  def __init__(self, prosumer_id, ip, port):
    self.prosumer_id = prosumer_id
    logging.info("Connecting to directory...")
    self.directory = zmq.Context().socket(zmq.REQ)
    self.directory.connect(DIRECTORY_ADDRESS)
    logging.info("Directory connected ({}).".format(self.directory))
    contract_address = self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port)
    self.account = client.accounts()[0] # use the first owned address
    self.contract = ResourceAllocationContract(client, contract_address)
    super(Prosumer, self).__init__()

  def run(self):
    current_time = time()
    time_interval = int(current_time - self.epoch) // INTERVAL_LENGTH
    next_polling = current_time + POLLING_INTERVAL
    # we stop after the END_INTERVAL
    while time_interval <= END_INTERVAL:
      current_time = time()
      if current_time > next_polling:
        logging.debug("Polling events...")
        next_polling = current_time + POLLING_INTERVAL
        for event in self.contract.poll_events():
          params = event['params']
          name = event['name']
      sleep(max(next_polling - time(), 0))
  
  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.directory.send_pyobj(msg)
    response = self.directory.recv_pyobj()
    self.epoch = time() - response['time']
    contract_address = response['contract']
    logging.info("Contract address: " + contract_address)
    return contract_address

if __name__ == "__main__":
  prosumer_id = 101
  ip = None
  port = None
  if len(sys.argv) > 1:
    prosumer_id = int(sys.argv[1])
  if len(sys.argv) > 2:
    ip = sys.argv[2]
  if len(sys.argv) > 3:
    port = sys.argv[3]
  logging.basicConfig(format='%(asctime)s / prosumer {} / %(levelname)s: %(message)s'.format(prosumer_id), level=logging.INFO)
  trader = Prosumer(prosumer_id, ip, port) 
  trader.run()

    
