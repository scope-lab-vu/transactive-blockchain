#Trader.py
from riaps.run.comp import Component
import os
import logging

class Trader(Component):
    def __init__(self):
        super(Trader, self).__init__()	        
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting Trader",str(self.pid))
        
        self.prosumer_id = 101
        self.net_production = net_production
        self.selling_offers = set()
        self.buying_offers = set()
        self.connected =0
        
        self.dbase = Database()
        self.role = None
        self.roleID = 0
        #self.grid = zmq.Context().socket(zmq.PUB)
        #self.grid.bind('tcp://127.0.0.1:2000')
        self.interval_asks = {}
        self.interval_bids = {}

        

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
        self.contract.registerProsumer(self.account, prosumer_id, PROSUMER_FEEDER[prosumer_id])


    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.info('PID(%s) - on_poller(): %s',str(self.pid),str(now))
        
        if self.connected == 0:
            self.query_contract_address()
            if self.contract:
                self.connected =1 
    
    def __destroy__(self):			
        self.logger.info("(PID %s) - stopping Trader",str(self.pid))   	        	        


    def query_contract_address(self):
        msg = {
            'request': "query_contract_address"
        }
        self.logger.info(msg)
        self.contractAddr.send_pyobj(msg)      