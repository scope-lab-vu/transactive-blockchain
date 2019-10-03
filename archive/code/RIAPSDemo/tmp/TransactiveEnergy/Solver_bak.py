#Solver.py
from riaps.run.comp import Component
import os
import logging

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
    
#         self.db = InfluxDBClient(Config.INFLUX_DBASE_HOST,Config.INFLUX_DBASE_PORT,
#                                      Config.INFLUX_DBASE_USER,Config.INFLUX_DBASE_PASSWORD,
#                                      "solverDbase")
#         self.db.create_database(Config.INFLUX_DBASE_NAME)
#         self.db.switch_database(Config.INFLUX_DBASE_NAME)
            

    def on_contractAddr(self):
        req = self.contractAddr.recv_pyobj()
        self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
        
        self.epoch = time() - rep['time']
        self.contract_address = rep['contract']
        self.logger.info("Contract address: " + self.contract_address)     
        self.logger.info("Setting up connection to Ethereum client...")
        client = EthereumClient(ip=MINER, port=PORT)
        self.account = client.accounts()[0] # use the first owned address
        self.logger.info("Creating contract object...")
        self.contract = MatchingContract(client, self.contract_address)
            

    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.info('PID(%s) - on_poller(): %s',str(self.pid),str(now))
        #self.query_contract_address() 
    
    def __destroy__(self):			
        self.logger.info("(PID %s) - stopping Solver",str(self.pid))   	        	
        
        
    def query_contract_address(self):
        msg = {
            'request': "query_contract_address"
        }
        self.logger.info(msg)
        self.contractAddr.send_pyobj(msg)  
