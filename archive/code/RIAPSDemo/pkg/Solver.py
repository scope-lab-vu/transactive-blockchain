#Solver.py
from riaps.run.comp import Component
from riaps.run.exc import PortError
import os
import logging

from time import time, sleep

from libs.config import *
from libs.MatchingSolver import MatchingSolver, Offer
from libs.EthereumClient import EthereumClient
from libs.MatchingContract import MatchingContract
 
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from libs.Grafana.config import Config
from libs.Grafana.dbase import Database
import datetime

import datetime

import random, string

def randomword(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class Solver(Component):
    def __init__(self):
        super(Solver, self).__init__()	        
        self.pid = os.getpid()

        self.logger.info("(PID %s) - starting Solver",str(self.pid))
        
        #Waste Space parameters
        self.delta = 1 # 1 MB #
        self.size = self.delta
        self.name = '/tmp/tmp%s' % randomword(8)
        self.logger.info(os.getcwd())
        
        #App Specific parameters
        self.solverID = 1
        print("solverID %s" %self.solverID)
        self.solution = None
        self.objective = 0 
        self.connected =0
        self.new_offers = False
        self.solver = MatchingSolver(MICROGRID)
        self.buying_offers = []
        self.selling_offers = []
        self.finalized = -1
        self.interval=-1
        self.waiting_solutionID = False
        self.PREDICTION_WINDOW = 0
        
    
        self.db = InfluxDBClient(Config.INFLUX_DBASE_HOST,Config.INFLUX_DBASE_PORT,
                                     Config.INFLUX_DBASE_USER,Config.INFLUX_DBASE_PASSWORD,
                                     "solverDbase")
        self.db.create_database(Config.INFLUX_DBASE_NAME)
        self.db.switch_database(Config.INFLUX_DBASE_NAME)  
        
        self.dbase = Database()          

#     def on_contractAddr(self):
#         self.logger.info("on_contractAddr()")
# 
#         req = self.contractAddr.recv_pyobj()
#         self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
#         
#         self.epoch = time() - req['time']
#         self.contract_address = req['contract']
#         self.logger.info("Contract address: " + self.contract_address)     
#         self.logger.info("Setting up connection to Ethereum client...")
#         client = EthereumClient(ip=MINER, port=PORT)
#         self.account = client.accounts()[0] # use the first owned address
#         self.logger.info("Creating contract object...")
#         self.contract = MatchingContract(client, self.contract_address)
#         self.connected = 1
        
    def on_contractAddr(self):
        try :            
            req = self.contractAddr.recv_pyobj()
            if 'contract' in req:            
                self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
                self.epoch = time() - req['time']
                self.time_interval = int(time() - self.epoch) // INTERVAL_LENGTH
                self.contract_address = req['contract']
                self.logger.info("Contract address: " + self.contract_address)     
                self.logger.info("Setting up connection to Ethereum client...")
                client = EthereumClient(ip=MINER, port=PORT)
                self.account = client.accounts()[0] # use the first owned address
                self.logger.info("Creating contract object...")
                self.contract = MatchingContract(client, self.contract_address)
                self.contract.registerProsumer(self.account, prosumer_id, PROSUMER_FEEDER[prosumer_id])
                self.connected = 1
            else : 
                self.logger.info("reply is:%s " %req)
        except PortError as e:
            self.logger.info("on_contractAddr:port exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("on_contractAdd: port error received")         

            

    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.info('PID(%s) - on_poller(): %s',str(self.pid),str(now))
        self.logger.info('update')
        
        if self.connected == 0 :
            self.query_contract_address()              
        
        elif self.connected == 1 :            
            self.logger.debug("Polling events...")
            
            for event in self.contract.poll_events():
                params = event['params']
                name = event['name']
                self.logger.info("{}({}).".format(name, params))
                
                if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
                    self.logger.info("{}({}).".format(name, params))
                    self.new_offers = True
                    offer = Offer(params['ID'], params['prosumer'], params['startTime'], params['endTime'], params['energy'])
                    if name == "BuyingOfferPosted":
                        self.buying_offers.append(offer)
                    else:
                        self.selling_offers.append(offer)
                elif (name == "SolutionCreated") and (params['solverID'] == self.solverID):
                    self.waiting_solutionID = False
                    solutionID = params['solutionID']
                    if self.solution is not None:
                        self.logger.info("Solution {} created by contract, adding trades...".format(solutionID))
                        trades = [trade for trade in self.solution if int(trade['p']) > 0]
                        for trade in trades:
                            self.contract.addTrade(self.account, solutionID, trade['s'].ID, trade['b'].ID, trade['t'], int(trade['p']))
                        self.logger.info("{} trades have been submitted to the contract.".format(len(trades)))
                        
                        if self.PREDICTION_WINDOW < 60:
                            self.PREDICTION_WINDOW +=5
                        self.logger.info("PREDICTION_WINDOW: %s" %self.PREDICTION_WINDOW)
                        self.dbase.post(now=datetime.datetime.now(), tag_dict={"resource":"Memory", "ID":'Solver'+str(self.solverID)}, seriesName="Waste", value=self.PREDICTION_WINDOW)
                        
                    else:
                        self.logger.info("Solution {} created by contract, but no solution has been found for this time interval (yet).".format(solutionID))
                elif name == "Finalized":
                    self.finalized = params['interval']
                    self.time_interval += 1
                    self.objective = float("-inf")
                    self.solution = None
                    # new_offers = False # TODO: offers for next interval might be added in the same block as the finalization for the previous!
                    self.logger.info("Trades for interval {} are now final, matching will consider only later intervals from now on.".format(self.finalized))
                    self.logger.info("New interval is : {}".format(self.time_interval))
                                        
                elif name == "TradeFinalized":
                    self.logger.info("{}({}).".format(name, params))
                    for offer in self.selling_offers:
                        if offer.ID == params['sellerID']:
                            offer.energy -= params['power']
                            break
                    for offer in self.buying_offers:
                        if offer.ID == params['buyerID']:
                            offer.energy -= params['power']
                            break
                                                
                elif name == "TradeAdded":
                    self.logger.info("{}({}).".format(name, params))
            
    def on_solve(self):
        now = self.solve.recv_pyobj()
        self.logger.info('PID(%s) - on_solve(): %s',str(self.pid),str(now))     
        
        if self.new_offers :
            self.new_offers = False
            self.logger.info("Solving...")
            stopWatch = {"interval":self.time_interval, "start":time(), "running" : 1}
            
            self.logger.info("buying offers")
            for offer in self.buying_offers:
                self.logger.info("%s, %s, %s, %s, %s" %(str(offer.ID), str(offer.prosumer), str(offer.startTime), str(offer.endTime), str(offer.energy)))
                
            self.logger.info("selling offers")
            for offer in self.selling_offers:
                self.logger.info("%s, %s, %s, %s, %s" %(str(offer.ID), str(offer.prosumer), str(offer.startTime), str(offer.endTime), str(offer.energy)))

            self.logger.info("interval")
            self.logger.info(self.time_interval)
            
            
            boffers=[]
            for offer in self.buying_offers:
                if offer.endTime < self.time_interval:
                    pass
                elif offer.startTime <= self.time_interval + self.PREDICTION_WINDOW:
                    # print(offer.__dict__)
                    boffers.append(offer)
                    
            soffers=[]
            for offer in self.selling_offers:
                if offer.endTime < self.time_interval:
                    pass
                elif offer.startTime <= self.time_interval + self.PREDICTION_WINDOW:
                    # print(offer.__dict__)
                    soffers.append(offer)
                               
            (solution, objective) = self.solver.solve(boffers, soffers, finalized=self.time_interval)
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
                             %(stopWatch["split"], len(self.buying_offers), len(self.selling_offers),
                               len(self.buying_offers)+len(self.selling_offers) ))
            
            if objective > self.objective:
                self.solution = solution
                self.objective = objective
                if not self.waiting_solutionID:
                    self.contract.createSolution(self.account, self.solverID)
                    self.waiting_solutionID = True
                self.logger.info("Done (objective = {}), trades will be submitted once a solution is created in the contract.".format(objective))
            else:
                self.logger.info("No better solution found (objective = {}).".format(objective))
               
        self.waste()
        
        
    def handleSpcLimit(self):
        '''This is a function called by the riaps platform and should be generated if we are doing disk limits'''
        self.logger.info('handleSpcLimit() ')
        try:
            os.remove(self.name)
            self.size = self.delta
            now = datetime.datetime.now()
            self.dbase.post(now=now, tag_dict={"resource":"storage"}, seriesName="Waste", value=self.size)

        except FileNotFoundError as e:
            self.logger.info("handleSpcLimit: Remove Error = %s" % e)
            self.logger.info("file does not exist")
    
    def handleMemLimit(self):
        self.PREDICTION_WINDOW -= 10
        self.logger.info('handleMemLimit(): PREDICTION_WINDOW = %d' %(self.PREDICTION_WINDOW))
        now = datetime.datetime.now()
        self.dbase.post(now=now, tag_dict={"resource":"Memory", "ID":'Solver'+str(self.solverID)}, seriesName="Waste", value=self.PREDICTION_WINDOW)

    
    def __destroy__(self):			
        self.logger.info("(PID %s) - stopping Solver",str(self.pid))   	        	
        
        
    def query_contract_address(self):
        msg = {
            'request': "query_contract_address"
        }
        self.logger.info(msg)        
        
        try:
            #self.cltReqPort.send_pyobj(msg)
            self.contractAddr.send_pyobj(msg)      
        except PortError as e:
            self.logger.info("query_contract_address:send exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("query_contract_address: try again")        
        
    def waste(self):
        try:
            cmd = 'dd if=/dev/zero of=%s bs=1M count=%d' % (self.name,self.size)
            res = os.system(cmd)
        except:
            self.logger.info("waste: op failed at %d" % (self.size))
        if res == 0:
            self.size += self.delta  
        now = datetime.datetime.now()
        self.dbase.post(now=now, tag_dict={"resource":"storage"}, seriesName="Waste", value=self.size)
            

