import zmq
import logging
import sys
import os
from time import time, sleep

from config import *
from MatchingSolver import MatchingSolver, Offer
from EthereumClient import EthereumClient
from MatchingContract import MatchingContract

POLLING_INTERVAL = 1 # seconds

class MatchingSolverWrapper(MatchingSolver):
  def __init__(self, ip, port, solverID):
    self.solverID = solverID
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
    self.objective = 0
    self.solution = None
    super(MatchingSolverWrapper, self).__init__(MICROGRID)

  def run(self):
    finalized = -1
    buying_offers = []
    selling_offers = []
    new_offers = False
    waiting_solutionID = False
    logging.info("Entering main loop...")
    current_time = time()
    next_polling = current_time + POLLING_INTERVAL
    next_solving = current_time + SOLVING_INTERVAL
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
            new_offers = True
            offer = Offer(params['ID'], params['prosumer'], params['startTime'], params['endTime'], params['energy'])
            if name == "BuyingOfferPosted":
              buying_offers.append(offer)
            else:
              selling_offers.append(offer)
          elif (name == "SolutionCreated") and (params['solverID'] == self.solverID):
            waiting_solutionID = False
            solutionID = params['solutionID']
            if self.solution is not None:
              logging.info("Solution {} created by contract, adding trades...".format(solutionID))
              trades = [trade for trade in self.solution if int(trade['p']) > 0]
              for trade in trades:
                self.contract.addTrade(self.account, solutionID, trade['s'].ID, trade['b'].ID, trade['t'], int(trade['p']))
              logging.info("{} trades have been submitted to the contract.".format(len(trades)))
            else:
              logging.info("Solution {} created by contract, but no solution has been found for this time interval (yet).".format(solutionID))
          elif name == "Finalized":
            finalized = params['interval']
            self.objective = float("-inf")
            self.solution = None
            # new_offers = False # TODO: offers for next interval might be added in the same block as the finalization for the previous!
            logging.info("Trades for interval {} are now final, matching will consider only later intervals from now on.".format(finalized))
          elif name == "TradeFinalized":
            logging.info("{}({}).".format(name, params))
            for offer in selling_offers:
              if offer.ID == params['sellerID']:
                offer.energy -= params['power']
                break
            for offer in buying_offers:
              if offer.ID == params['buyerID']:
                offer.energy -= params['power']
                break
          elif name == "TradeAdded":
            logging.info("{}({}).".format(name, params))
      if current_time > next_solving:
        next_solving = current_time + SOLVING_INTERVAL
        if new_offers:
          new_offers = False
          logging.info("Solving...")
          (solution, objective) = self.solve(buying_offers, selling_offers, finalized=finalized) 
          if objective > self.objective:
            self.solution = solution
            self.objective = objective
            if not waiting_solutionID:
              self.contract.createSolution(self.account, self.solverID)
              waiting_solutionID = True
            logging.info("Done (objective = {}), trades will be submitted once a solution is created in the contract.".format(objective))
          else:
            logging.info("No better solution found (objective = {}).".format(objective))
      sleep(max(min(next_polling, next_solving) - time(), 0))
      
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
  solverID = os.getpid()
  solver = MatchingSolverWrapper(ip, port, solverID)
  solver.run()

