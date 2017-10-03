import zmq
import logging
import sys
from time import time, sleep

from config import *
from MatchingSolver import MatchingSolver, Microgrid
from EthereumClient import EthereumClient

POLLING_INTERVAL = 1 # seconds
SOLVING_INTERVAL = 60 # seconds

class MatchingSolverWrapper(MatchingSolver):
  def __init__(self, ip, port):
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    self.client = EthereumClient(ip=ip, port=port) 
    logging.info("Creating event filter...")
    self.filter = Filter(self.client)
    super(MatchingSolverWrapper, self).__init__(MICROGRID)

  def run(self):
    logging.info("Entering main loop...")
    next_polling = time() + POLLING_INTERVAL
    next_solving = time() + SOLVING_INTERVAL
    while True:
      current_time = time()
      if current_time > next_polling:
        logging.debug("Polling events...")
        next_polling = current_time + POLLING_INTERVAL
        for event in self.filter.poll_events():
          params = event['params']
          name = event['name']
          if name == "OfferPosted":
            self.OfferPosted(params['offerID'], params['power'], params['start'], params['end'], params['price'])
      if current_time > next_solving:
        logging.debug("Solving...")
        # TODO: writeme (create solution in contract, call solve in super, and submit the solution values)
      sleep(next_polling - current_time)

if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  ip = None
  port = None
  if len(sys.argv) > 1:
    ip = sys.argv[1]
  if len(sys.argv) > 2:
    port = sys.argv[2]
  solver = MatchingSolverWrapper(ip, port)
  solver.run()

