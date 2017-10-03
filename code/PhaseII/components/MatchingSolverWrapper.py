import zmq
import logging
import sys
from time import time, sleep

from config import *
from MatchingSolver import MatchingSolver, Offer
from EthereumClient import EthereumClient
from Filter import Filter

POLLING_INTERVAL = 1 # seconds
SOLVING_INTERVAL = 10 # seconds

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
    self.filter = Filter(self.client)
    super(MatchingSolverWrapper, self).__init__(MICROGRID)

  def run(self):
    buying_offers = []
    selling_offers = []
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
          if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
            logging.info("Offer recorded ({}).".format(params))
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
            for trade in self.latest_solution:
              self.addTrade(solutionID, trade['s'].ID, trade['b'].ID, trade['t'], int(trade['p']))
            logging.info("{} trades have been submitted to the contract.".format(len(self.latest_solution)))
      if current_time > next_solving:
        logging.info("Solving...")
        next_solving = current_time + SOLVING_INTERVAL
        self.createSolution()
        self.solve(buying_offers, selling_offers)
        logging.info("Done, trades will be submitted once the solution is created in the contract.")
      sleep(min(next_polling, next_solving) - current_time)
      
  def createSolution(self):
    logging.info("createSolution()")
    data = "0xf5757421"
    self.client.transaction(self.account, data, self.contractAddress)

  def addTrade(self, solutionID, sellerID, buyerID, time, power):
    logging.info("addTrade({}, {}, {}, {}, {})".format(solutionID, sellerID, buyerID, time, power))
    data = "0x9e52b99f" + \
      EthereumClient.encode_uint(solutionID) + \
      EthereumClient.encode_uint(sellerID) + \
      EthereumClient.encode_uint(buyerID) + \
      EthereumClient.encode_uint(time) + \
      EthereumClient.encode_uint(power)
    self.client.transaction(self.account, data, self.contractAddress)

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
  solver = MatchingSolverWrapper(ip, port)
  solver.run()

