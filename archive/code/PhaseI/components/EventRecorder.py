import zmq
import logging
import sys
import os
from time import time, sleep, asctime

from config import *
from Filter import Filter
from EthereumClient import EthereumClient

POLLING_INTERVAL = 1 # seconds

class EventRecorder:
  def __init__(self, ip, port):
    self.geth = EthereumClient(ip=ip, port=port)
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Creating event filter...")
    self.filter = Filter(self.geth, ip=ip, port=port)
  
  def run(self):
    logging.info("Entering main loop...")
    next_polling = time() + POLLING_INTERVAL
    with open("events." + asctime(), "wt") as fout:
      while True:
        current_time = time()
        if current_time > next_polling:
          logging.debug("Polling events...")
          next_polling = current_time + POLLING_INTERVAL
          for event in self.filter.poll_events():
            params = event['params']
            name = event['name']
            log = str((asctime(), event['name'], event['params']))
            print(log)
            fout.write(log + "\n")
            fout.flush()
            os.fsync(fout)
        sleep(next_polling - current_time)

  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)
    self.contractAddress = self.dso.recv_pyobj()
    logging.info("Contract address: " + self.contractAddress)

if __name__ == "__main__":
  logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
  ip = None
  port = None
  if len(sys.argv) > 1:
    ip = sys.argv[1]
  if len(sys.argv) > 2:
    port = sys.argv[2]
  recorder = EventRecorder(ip, port) 
  recorder.run()

    
