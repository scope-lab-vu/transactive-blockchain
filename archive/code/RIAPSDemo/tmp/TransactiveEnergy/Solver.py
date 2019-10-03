#Solver.py
from riaps.run.comp import Component
import os
import logging

from time import time, sleep
from config import *
from MatchingSolver import MatchingSolver, Offer
from EthereumClient import EthereumClient
from MatchingContract import MatchingContract

# from influxdb import InfluxDBClient
# from influxdb.client import InfluxDBClientError
# from Grafana.config import Config
import datetime


class Solver(Component):
    def __init__(self):
        super(Solver, self).__init__()	        
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Solver",str(self.pid))
        
        self.solverID = 1
        print("solverID %s" %self.solverID)
        self.solution = None
        self.objective = 0 
        self.connected =0
        self.new_offers = False
        self.solver = MatchingSolver()
        
        #self.query_contract_address() 
    
#         self.db = InfluxDBClient(Config.INFLUX_DBASE_HOST,Config.INFLUX_DBASE_PORT,
#                                      Config.INFLUX_DBASE_USER,Config.INFLUX_DBASE_PASSWORD,
#                                      "solverDbase")
#         self.db.create_database(Config.INFLUX_DBASE_NAME)
#         self.db.switch_database(Config.INFLUX_DBASE_NAME)            

    def on_contractAddr(self):
        req = self.contractAddr.recv_pyobj()
        self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
        
        self.epoch = time() - req['time']
        self.contract_address = req['contract']
        self.logger.info("Contract address: " + self.contract_address)     
        self.logger.info("Setting up connection to Ethereum client...")
        client = EthereumClient(ip=MINER, port=PORT)
        self.account = client.accounts()[0] # use the first owned address
        self.logger.info("Creating contract object...")
        self.contract = MatchingContract(client, self.contract_address)
            

    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.info('PID(%s) - on_poller(): %s',str(self.pid),str(now))
        self.logger.info('update')
        if self.connected == 0:
            self.query_contract_address()
            if self.contract:
                self.connected =1 
                
        self.logger.debug("Polling events...")
        
        for event in self.contract.poll_events():
            params = event['params']
            name = event['name']
            logging.info("{}({}).".format(name, params))
            
            if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
                self.logger.info("{}({}).".format(name, params))
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
                    self.logger.info("Solution {} created by contract, adding trades...".format(solutionID))
                    trades = [trade for trade in self.solution if int(trade['p']) > 0]
                    for trade in trades:
                        self.contract.addTrade(self.account, solutionID, trade['s'].ID, trade['b'].ID, trade['t'], int(trade['p']))
                    self.logger.info("{} trades have been submitted to the contract.".format(len(trades)))
                else:
                    self.logger.info("Solution {} created by contract, but no solution has been found for this time interval (yet).".format(solutionID))
            elif name == "Finalized":
                finalized = params['interval']
                self.objective = float("-inf")
                self.solution = None
                # new_offers = False # TODO: offers for next interval might be added in the same block as the finalization for the previous!
                self.logger.info("Trades for interval {} are now final, matching will consider only later intervals from now on.".format(finalized))
            elif name == "TradeFinalized":
                self.logger.info("{}({}).".format(name, params))
                for offer in selling_offers:
                    if offer.ID == params['sellerID']:
                        offer.energy -= params['power']
                        break
                for offer in buying_offers:
                    if offer.ID == params['buyerID']:
                        offer.energy -= params['power']
                        break
            elif name == "TradeAdded":
                self.logger.info("{}({}).".format(name, params))
            
    def on_solve(self):
        now = self.solve.recv_pyobj()
        self.logger.info('PID(%s) - on_solve(): %s',str(self.pid),str(now))     
        
        if self.new_offers:
            new_offers = False
            logging.info("Solving...")
            stopWatch = {"interval":finalized, "start":time(), "running" : 1}
            (solution, objective) = self.solver.solve(buying_offers, selling_offers, finalized=finalized)
            stopWatch["split"] = time()-stopWatch["start"]
            
            records = []
            record = { "time":datetime.datetime.now(),
                      "measurement" : "solveTime",
                      "tags" : {"object" : "Solver_"+str(self.solverID)},
                      "fields" : {"value" : stopWatch["split"]},
                      }
            records.append(record)
            res = self.db.write_points(records)
            
            self.logger.info("Solve Time: %s, buy offers: %s, sell offers: %s, total: %s"
                             %(stopWatch["split"], len(buying_offers), len(selling_offers),
                               len(buying_offers)+len(selling_offers) ))
            
            if objective > self.objective:
                self.solution = solution
                self.objective = objective
                if not waiting_solutionID:
                    self.contract.createSolution(self.account, self.solverID)
                    waiting_solutionID = True
                logging.info("Done (objective = {}), trades will be submitted once a solution is created in the contract.".format(objective))
            else:
                self.logger.info("No better solution found (objective = {}).".format(objective))
               
            

    
    def __destroy__(self):			
        self.logger.info("(PID %s) - stopping Solver",str(self.pid))   	        	
        
        
    def query_contract_address(self):
        msg = {
            'request': "query_contract_address"
        }
        self.logger.info(msg)
        self.contractAddr.send_pyobj(msg)  
