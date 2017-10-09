import zmq
import logging
import sys
from time import time, sleep

from config import *
from MatchingSolver import MatchingSolver, Offer
from EthereumClient import EthereumClient
from MatchingContract import MatchingContract

POLLING_INTERVAL = 1 # seconds

class MatchingSolverWrapper(MatchingSolver):
  def __init__(self, ip, port):
    logging.info("Connecting to DSO...")
    self.dso = zmq.Context().socket(zmq.REQ)
    self.dso.connect(DSO_ADDRESS)
    logging.info("DSO connected ({}).".format(self.dso))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port) 
    self.account = self.client.accounts()[0] # use the first owned address
    logging.info("Creating contract object...")
    self.contract = MatchingContract(client, address)
    self.objective = float("-inf")
    self.solution = None
    super(MatchingSolverWrapper, self).__init__(MICROGRID)

  def run(self):
    finalized = START_INTERVAL - 1
    buying_offers = []
    selling_offers = []
    logging.info("Entering main loop...")
    current_time = time()
    next_polling = current_time + POLLING_INTERVAL
    next_solving = current_time + SOLVING_INTERVAL
    next_finalizing = current_time + INTERVAL_LENGTH
    while True:
      current_time = time()
      if current_time > next_polling:
        logging.debug("Polling events...")
        next_polling = current_time + POLLING_INTERVAL
        for event in self.contract.poll_events():
          params = event['params']
          name = event['name']
          if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
            logging.info("{}({}).".format(name, params))
            offer = Offer(params['ID'], params['prosumer'], params['startTime'], params['endTime'], params['energy'])
            if name == "BuyingOfferPosted":
              buying_offers.append(offer)
            else:
              selling_offers.append(offer)
          elif name == "SolutionCreated":
            solutionID = params['ID']
            if self.solution is not None:
              logging.info("Solution {} created by contract, adding trades...".format(solutionID))
              trades = [trade for trade in self.solution if int(trade['p']) > 0]
              for trade in trades:
                self.contract.addTrade(self.account, solutionID, trade['s'].ID, trade['b'].ID, trade['t'], int(trade['p']))
              logging.info("{} trades have been submitted to the contract.".format(len(trades)))
            else:
              logging.info("Solution {} created by contract, but no solution has been found for this time interval (yet).".format(solutionID))
          elif name == "TradeAdded":
            logging.info("{}({}).".format(name, params))
      if current_time > next_solving:
        logging.info("Solving...")
        next_solving = current_time + SOLVING_INTERVAL
        (solution, objective) = self.solve(buying_offers, selling_offers, finalized=finalized)
        if objective > self.objective:
          self.solution = solution
          self.objective = objective
          self.contract.createSolution(self.account)
          logging.info("Done, trades will be submitted once the solution is created in the contract.")
        else:
          logging.info("No better solution found.")
      if current_time > next_finalizing:
        next_finalizing += INTERVAL_LENGTH
        finalized += 1
        self.objective = float("-inf")
        self.solution = None
        logging.info("Trades for interval {} are now final, matching will consider only later intervals from now on.".format(finalized))
      sleep(max(min(next_polling, next_solving, next_finalizing) - time(), 0))
      
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

