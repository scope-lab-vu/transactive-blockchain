import zmq
import logging
import sys
from time import time, sleep

from config import *
from MatchingSolver import MatchingSolver, Offer
from EthereumClient import EthereumClient
from Filter import Filter

POLLING_INTERVAL = 1 # seconds

class MatchingSolverWrapper(MatchingSolver):
  def __init__(self, ip, port):
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    self.client = EthereumClient(ip=ip, port=port) 
    self.account = self.client.get_addresses()[0] # use the first owned address
    logging.info("Creating event filter...")
    self.filter = Filter(self.client, address=self.contract_address)
    self.objective = 0
    super(MatchingSolverWrapper, self).__init__(MICROGRID)

  def run(self):
    finalized = START_INTERVAL - 1
    buying_offers = []
    selling_offers = []
    logging.info("Entering main loop...")
    current_time = time()
    next_polling = current_time + POLLING_INTERVAL
    next_solving = current_time + SOLVING_INTERVAL
    next_finalizing = current_time + FINALIZING_INTERVAL
    while True:
      current_time = time()
      if current_time > next_polling:
        logging.debug("Polling events...")
        next_polling = current_time + POLLING_INTERVAL
        for event in self.filter.poll_events():
          params = event['params']
          name = event['name']
          if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
            logging.info("{}({}).".format(name, params))
            offerID = params['ID']
            prosumer = params['prosumer']
            startTime = params['startTime']
            endTime = params['endTime']
            energy = params['energy']
            if name == "BuyingOfferPosted":
              buying_offers.append(Offer(offerID, prosumer, startTime, endTime, energy))
            else:
              selling_offers.append(Offer(offerID, prosumer, startTime, endTime, energy))
          elif name == "SolutionCreated":
            solutionID = params['ID']
            logging.info("Solution {} created by contract, adding trades...".format(solutionID))
            trades = [trade for trade in self.solution if int(trade['p']) > 0]
            for trade in trades:
              self.addTrade(solutionID, trade['s'].ID, trade['b'].ID, trade['t'], int(trade['p']))
            logging.info("{} trades have been submitted to the contract.".format(len(trades)))
          elif name == "TradeAdded":
            logging.info("{}({}).".format(name, params))
      if current_time > next_solving:
        logging.info("Solving...")
        next_solving = current_time + SOLVING_INTERVAL
        (solution, objective) = self.solve(buying_offers, selling_offers, finalized=finalized)
        if objective > self.objective:
          self.solution = solution
          self.objective = objective
          self.createSolution()
          logging.info("Done, trades will be submitted once the solution is created in the contract.")
        else:
          logging.info("No better solution found.")
      if current_time > next_finalizing:
        next_finalizing += FINALIZING_INTERVAL
        finalized += 1
        logging.info("Trades for interval {} are now final, matching will consider only later intervals from now on.".format(finalized))
      sleep(max(min(next_polling, next_solving, next_finalizing) - time(), 0))
      
  def createSolution(self):
    logging.info("createSolution()")
    data = "0xf5757421"
    self.client.transaction(self.account, data, self.contract_address)

  def addTrade(self, solutionID, sellerID, buyerID, time, power):
    logging.info("addTrade({}, {}, {}, {}, {})".format(solutionID, sellerID, buyerID, time, power))
    data = "0x9e52b99f" + \
      EthereumClient.encode_uint(solutionID) + \
      EthereumClient.encode_uint(sellerID) + \
      EthereumClient.encode_uint(buyerID) + \
      EthereumClient.encode_uint(time) + \
      EthereumClient.encode_uint(power)
    self.client.transaction(self.account, data, self.contract_address)

  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.dso.send_pyobj(msg)
    self.contract_address = self.dso.recv_pyobj()
    logging.info("Contract address: " + self.contract_address)

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

