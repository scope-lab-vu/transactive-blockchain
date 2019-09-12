import zmq
import logging
import sys
from time import time, sleep

from config import *
from EthereumClient import EthereumClient
from ResourceAllocationContract import ResourceAllocationContract

from Grafana.config import Config
from Grafana.dbase import Database
import datetime

POLLING_INTERVAL = 1 # seconds

class EventRecorder():
  def __init__(self, ip, port):
    logging.info("Connecting to directory...")
    self.directory = zmq.Context().socket(zmq.REQ)
    self.directory.connect(DIRECTORY_ADDRESS)
    logging.info("Directory connected ({}).".format(self.directory))
    contract_address = self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port)
    self.account = client.accounts()[0] # use the first owned address
    logging.info("Creating contract object...")
    self.contract = ResourceAllocationContract(client, self.contract_address)
    self.dbase = Database()
    self.time = datetime.datetime.combine(datetime.date.today(),datetime.time(hour=7))

  def run(self):
    logging.info("Entering main loop...")
    next_polling = time()
    while True:
      logging.debug("Polling events...")
      simulation_time = time() - self.epoch
      for event in self.contract.poll_events():
        params = event['params']
        name = event['name']
        logging.info("[time = {}] {}({}).".format(simulation_time, name, params))
        # TODO: record data to database
        if (name == "Debug"):
            logging.info("{}({}).".format(name, params))
        # elif (name == "FinalizeRequested"):
        #     stopWatch = {"start":time(), "running" : 1}
        #     logging.info("{}({}).".format(name, params))
        # elif(name == "FinalizeComplete"):
        #     stopWatch["split"] = time() - stopWatch["start"]
        #     logging.info("{}({}).".format(name, params))
        #     tag_dict = {}
        #     self.dbase.log(self.time-datetime.timedelta(seconds=1), tag_dict, "FinalizeTime", 0)
        #     self.dbase.log(self.time, tag_dict, "FinalizeTime", stopWatch["split"])
      next_polling += POLLING_INTERVAL
      sleep(max(next_polling - time(), 0))

  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.directory.send_pyobj(msg)
    response = self.directory.recv_pyobj()
    self.epoch = time() - response['time']
    self.contract_address = response['contract']
    logging.info("Contract address: " + self.contract_address)

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
