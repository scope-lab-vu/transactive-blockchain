import zmq
import logging
import sys
import os
from time import time, sleep

from config import *
from ResourceAllocationLP import ResourceAllocationLP, ArchitectureJob, JobOffer, ResourceOffer
from EthereumClient import EthereumClient
from ResourceAllocationContract import ResourceAllocationContract

POLLING_INTERVAL = 1 # seconds

class Solver(ResourceAllocationLP):
  def __init__(self, ip, port, solverID,DIRECTORY_IP):
    self.solverID = solverID
    logging.info("Connecting to directory...")
    self.directory = zmq.Context().socket(zmq.REQ)
    self.directory.connect("tcp://%s:10001" %DIRECTORY_IP)
    logging.info("Directory connected ({}).".format(self.directory))
    self.query_contract_address()
    logging.info("Setting up connection to Ethereum client...")
    client = EthereumClient(ip=ip, port=port)
    self.account = client.accounts()[0] # use the first owned address
    logging.info("Creating contract object...")
    self.contract = ResourceAllocationContract(client, self.contract_address)
    self.objective = 0
    self.solution = None
    super(Solver, self).__init__()

  def run(self):
    unposted_ro = {}
    posted_ro = {}
    unposted_jo = {}
    posted_jo = {}
    logging.info("Entering main loop...")
    next_polling = time() + POLLING_INTERVAL
    while True:
      logging.debug("Polling events...")
      for event in self.contract.poll_events():
        params = event['params']
        name = event['name']
        logging.info("{}({}).".format(name, params))
        if name == "ResourceOfferPosted":
          posted_ro[params['offerID']] = ResourceOffer(params['offerID'], params['actorID'], params['architecture'], params['capCPU'], params['capRAM'], params['capStorage'], params['price'])

        elif name == "ResourceOfferCanceled":
          unposted_ro[params['offerID']] = posted_ro.pop(params['offerID'])

        elif name == "JobOfferCreated":
          unposted_jo[params['offerID']] = JobOffer(params['offerID'], params['actorID'], params['timeLimit'], params['price'])

        elif name == "JobOfferUpdated":
          unposted_jo[params['offerID']].update(params['architecture'], ArchitectureJob(params['reqCPU'], params['reqRAM'], params['reqStorage'], params['imageHash']))

        elif name == "JobOfferPosted":
          posted_jo[params['offerID']] = unposted_jo.pop(params['offerID'])

        elif name == "JobOfferCanceled":
          unposted_jo[params['offerID']] = posted_jo.pop(params['offerID'])

        elif name == "Closed":
          # initiate creating a solution as soon as possible
          logging.info("{}({}).".format(name, params))

          self.contract.createSolution(self.account, self.solverID)
          # solve allocation and store solution
          logging.info("Solving job allocation problem with {len(posted_jo)} job offers and {len(posted_ro)} resource offers...")
          logging.info("JOS")
          logging.info(type(posted_jo))
          logging.info(posted_jo)
          logging.info(posted_jo.values())
          logging.info(type(posted_jo.values()))
          logging.info("ROS")
          logging.info(posted_ro)
          logging.info(posted_ro.values())
          (solution, objective) = self.solve(posted_jo.values(), posted_ro.values())
          self.solution = solution
          logging.info(f"Job allocation problem solved, objective = {objective}")

        elif name == "SolutionCreated" and params['actorID'] == self.solverID:
          logging.info("Solution {params['solutionID']} created, adding assignments...")
          for assign in self.solution:
            if assign['a'] > 0:
              self.contract.addAssignment(self.account, params['solutionID'], assign['jo'].offerID, assign['ro'].offerID)
          logging.info("Assignments added")
        elif name == "AssignmentFinalized":
          # clear everything for new round
          self.solution = None
          unposted_ro = {}
          posted_ro = {}
          unposted_jo = {}
          posted_jo = {}
      sleep(max(next_polling - time(), 0))

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
  if len(sys.argv) > 3:
    solverID = sys.argv[3]
  if len(sys.argv) > 4:
      DIRECTORY_IP = sys.argv[4]
  solverID = os.getpid()
  solver = Solver(ip, port, solverID,DIRECTORY_IP)
  solver.run()
