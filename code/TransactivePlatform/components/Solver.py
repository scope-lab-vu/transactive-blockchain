import zmq
import logging
import sys
import os
from time import time, sleep

from config import *
from ResourceAllocationLP import ResourceAllocationLP, Offer
from EthereumClient import EthereumClient
from ResourceAllocationContract import ResourceAllocationContract

POLLING_INTERVAL = 1 # seconds

class Solver(ResourceAllocationLP):
  def __init__(self, ip, port, solverID):
    self.solverID = solverID
    logging.info("Connecting to directory...")
    self.directory = zmq.Context().socket(zmq.REQ)
    self.directory.connect(DIRECTORY_ADDRESS)
    logging.info("Directory connected ({}).".format(self.directory))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port)
    self.account = client.accounts()[0] # use the first owned address
    logging.info("Creating contract object...")
    self.contract = ResourceAllocationContract(client, self.contract_address)
    self.objective = 0
    self.solution = None
    super(Solver, self).__init__(PRECISION)

  def run(self):
    offers = {} # between OfferCreated and OfferPosted
    cons_offers = [] # after OfferPosted
    prov_offers = [] # after OfferPosted
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
          logging.info("{}({}).".format(name, params))
          if name == "OfferCreated":
            offers[params['ID']] = Offer(params['ID'], params['providing'], params['prosumer'])
          elif name == "OfferUpdated":
            offer = offers[params['ID']]
            res_type = params['resourceType']
            offer.quantity[res_type] = params['quantity']
            offer.value[res_type] = params['value']
          elif name == "OfferPosted":
            new_offers = True
            offer = offers[params['ID']]
            if offer.providing:
              prov_offers.append(offer)
            else:
              cons_offers.append(offer)
          elif name == "OfferCanceled":
            offer = offers[params['ID']]
            if offer.providing:
              prov_offers.remove(offer)
            else:
              cons_offers.remove(offer)
          elif (name == "SolutionCreated") and (params['misc'] == self.solverID):
            logging.info("{}({}).".format(name, params))
            waiting_solutionID = False
            solutionID = params['ID']
            if self.solution is not None:
              logging.info("Solution {} created by contract, adding assignments...".format(solutionID))
              assignments = [assign for assign in self.solution if int(assign['q']) > 0]
              for assign in assignments:
                print("solutionID : POID : COID : T : Q : V")
                print(solutionID,assign['po'].ID, assign['co'].ID, assign['t'],
                             int(assign['q']), assign['co'].value[assign['t']])
                self.contract.check(self.account)
                self.contract.addAssignment(self.account, solutionID,
                  assign['po'].ID, assign['co'].ID, assign['t'], int(assign['q']), assign['co'].value[assign['t']])
              logging.info("{} assignments have been submitted to the contract.".format(len(assignments)))
            else:
              logging.info("Solution {} created by contract, but no solution has been found for this time interval (yet).".format(solutionID))
      if current_time > next_solving:
        next_solving = current_time + SOLVING_INTERVAL
        if new_offers:
          new_offers = False
          logging.info("Solving...")
          (solution, objective) = self.solve(prov_offers, cons_offers)
          if objective > self.objective:
            self.solution = solution
            self.objective = objective
            if not waiting_solutionID:
              self.contract.checkcreateSolution(self.account)
              self.contract.close(self.account)
              self.contract.checkcreateSolution(self.account)
              self.contract.createSolution(self.account, self.solverID)
              waiting_solutionID = True
            logging.info("Done (objective = {}), assignments will be submitted once a solution is created in the contract.".format(objective))
          else:
            logging.info("No better solution found (objective = {}).".format(objective))
      sleep(max(min(next_polling, next_solving) - time(), 0))

  def query_contract_address(self):
    msg = {
      'request': "query_contract_address"
    }
    logging.info(msg)
    self.directory.send_pyobj(msg)
    response = self.directory.recv_pyobj()
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
  solver = Solver(ip, port, solverID)
  solver.run()
