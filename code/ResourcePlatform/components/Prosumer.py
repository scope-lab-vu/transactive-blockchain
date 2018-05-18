import zmq
import logging
logging.basicConfig(level=logging.INFO)
import sys
from time import time, sleep
from random import random

from config import *
from EthereumClient import EthereumClient
from ResourceAllocationContract import ResourceAllocationContract

POLLING_INTERVAL = 1 # seconds

class Prosumer:
  def __init__(self, prosumer_id, ip, port):
    self.logger = logging.getLogger(__name__)
    self.prosumer_id = prosumer_id
    self.logger.info("Connecting to directory...")
    self.directory = zmq.Context().socket(zmq.REQ)
    self.directory.connect(DIRECTORY_ADDRESS)
    self.logger.info("Directory connected ({}).".format(self.directory))
    contract_address = self.query_contract_address()
    self.logger.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port)
    self.account = client.accounts()[0] # use the first owned address
    self.contract = ResourceAllocationContract(client, contract_address)
    # offer management
    self.next_offer = 0 # offer ID that is unique within prosumer
    self.pending_offers = {} # between createOffer and OfferCreated
    self.created_offers = {} # between updateOffer and OfferUpdated
    super(Prosumer, self).__init__()

  def run(self):
    current_time = time()
    time_interval = int(current_time - self.epoch) // INTERVAL_LENGTH
    self.logger.info("time_interval %s" %time_interval)
    next_polling = current_time + POLLING_INTERVAL
    # we stop after the END_INTERVAL
    while time_interval <= END_INTERVAL:
      current_time = time()
      if current_time > next_polling:
        #self.logger.debug("Polling events...")
        next_polling = current_time + POLLING_INTERVAL
        for event in self.contract.poll_events():
          params = event['params']
          name = event['name']
          if (name == "OfferCreated") and (params['prosumer'] == self.prosumer_id):
            self.logger.info("{}({}).".format(name, params))
            offer = self.pending_offers.pop(params['misc'])
            self.created_offers[params['ID']] = offer
            for res_type in offer['quantity']:
              self.contract.updateOffer(self.account, params['ID'], res_type, offer['quantity'][res_type], offer['value'][res_type])
          elif (name == "OfferUpdated") and (params['ID'] in self.created_offers):
            self.logger.info("{}({}).".format(name, params))
            offer = self.created_offers[params['ID']]
            offer['quantity'].pop(params['resourceType'])
            if not len(offer['quantity']):
              self.contract.postOffer(self.account, params['ID'])
          elif (name == "OfferPosted") and (params['ID'] in self.created_offers):
              self.logger.info("{}({}).".format(name, params))
      sleep(max(next_polling - time(), 0))

  def post_offer(self, providing, quantity, value):
    self.pending_offers[self.next_offer] = {'quantity': quantity, 'value': value}
    self.contract.createOffer(self.account, providing, self.next_offer, self.prosumer_id)
    self.next_offer += 1

  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    self.logger.info(msg)
    self.directory.send_pyobj(msg)
    response = self.directory.recv_pyobj()
    self.epoch = time() - response['time']
    contract_address = response['contract']
    self.logger.info("Contract address: " + contract_address)
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
