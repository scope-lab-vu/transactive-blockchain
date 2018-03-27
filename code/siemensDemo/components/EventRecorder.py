import zmq
import logging
import sys
from time import time, sleep

from config import *
from MatchingSolver import MatchingSolver, Offer
from EthereumClient import EthereumClient
from MatchingContract import MatchingContract

from Grafana.config import Config
from Grafana.dbase import Database
import collections

POLLING_INTERVAL = 1 # seconds

class EventRecorder():
  def __init__(self, ip, port):
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port)
    self.account = client.accounts()[0] # use the first owned address
    logging.info("Creating contract object...")
    self.contract = MatchingContract(client, self.contract_address)

    self.dbase = Database()

  def run(self):
    logging.info("Entering main loop...")
    next_polling = time()

    interval_trades = {}
    solutions = collections.defaultdict(dict)
    solution2solver ={}
    finalized = 0
    in_db = True

    while True:
      logging.debug("Polling events...")
      simulation_time = time() - self.epoch
      for event in self.contract.poll_events():
        params = event['params']
        name = event['name']
        logging.info("[time = {}] {}({}).".format(simulation_time, name, params))
        # TODO: record data to database

        if name == "Finalized":
          finalized = params['interval']
          stopWatch = {"interval":finalized, "start":time(), "running" : 1}
          logging.info("interval finalized : {}".format(finalized))
          interval_trades[finalized] = []
          in_db = False
        elif name == "TradeFinalized":
          if (stopWatch["running"]):
              stopWatch["running"] = 0
              stopWatch["split"] = time() - stopWatch["start"]
              self.dbase.log(finalized, "Solver", "FinalizeTime", stopWatch["split"])
          interval = params['time']
          power = params['power']
          interval_trades[finalized].append(power)
          self.dbase.log(finalized,"Solver", "TotalEnergyTraded", sum(interval_trades[finalized]))
        elif name == "TradeAdded":
            interval = params['time']
            ID = params['solutionID']
            pwr =  params['power']
            solverID = solution2solver[ID]
            if int(ID) < 10 :
                ID = "0"+str(ID)
            if int(ID) < 100 :
                ID = "0"+str(ID)
            try:
                solutions[ID][interval] += pwr
            except KeyError:
                solutions[ID][interval] = pwr
            #TradeAdded({'solutionID': 63, 'power': 400, 'time': 93, 'objective': 400, 'buyerID': 65, 'sellerID': 27}).
            logging.info("TradeAdded : interval:{}, Solver:{}, SolutionID:{}, pwr:{}".format(interval,solverID,ID,solutions[ID][interval]))
            self.dbase.log(interval, "solution"+str(ID), "Solver"+str(solverID),  solutions[ID][interval])
            logging.info("{}({}).".format(name, params))
        elif (name == "SolutionCreated"):
            solverID = params['solverID']
            solutionID = params['solutionID']
            solution2solver[solutionID] = solverID
            logging.info("SolutionCreated Solver:{} Solution:{}".format(solverID, solutionID))
        elif in_db == False and interval_trades[finalized]:
          #logging.info("All trades : {}".format(interval_trades[finalized]))
          #logging.info("Total Energy Traded: {}".format(sum(interval_trades[finalized])))
          #self.dbase.log(finalized,"Solver", "TotalEnergyTraded", sum(interval_trades[finalized]))
          in_db = True

      next_polling += POLLING_INTERVAL
      sleep(max(next_polling - time(), 0))

  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)
    response = self.dso.recv_pyobj()
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
