#DSO.py
from riaps.run.comp import Component
import os
import logging
from time import time, sleep


from libs.config import *
from libs.EthereumClient import EthereumClient
from libs.MatchingContract import MatchingContract

#from asyncio.log import logger

class DSO(Component):
    def __init__(self):
        super(DSO, self).__init__()            
        self.pid = os.getpid()
        self.logger.info("(PID %s) - starting DSO",str(self.pid))
        self.client = EthereumClient(ip=MINER, port=PORT)
        self.account = self.client.accounts()[0] # use the first owned address
        self.deploy_contract()
        self.next_interval = START_INTERVAL
        t = time()
        self.epoch = t - START_INTERVAL * INTERVAL_LENGTH
        

    def on_contractAddr(self):
        msg = self.contractAddr.recv_pyobj()
        self.logger.info("PID (%s) - on_query():%s",str(self.pid),str(msg))
        if msg['request'] == "query_contract_address":
            self.logger.info("query_contract_address()")
            self.logger.info("time elapsed since epoch %s" %(time()-self.epoch))
            self.contractAddr.send_pyobj({'contract': self.contract_address, 'time': time() - self.epoch})
        else:
            self.logger.error("Unknown request: " + msg['request'])
            self.contractAddr.send_pyobj("Unknown request!")
    
    def on_finalizer(self):
        now = self.finalizer.recv_pyobj()
        self.logger.info('PID(%s) - on_finalizer(): %s',str(self.pid),str(now))    
        self.logger.info("Finalizing interval {}".format(self.next_interval))
        self.contract.finalize(self.account, self.next_interval)
        self.next_interval += 1
    
    def __destroy__(self):			
        self.logger.info("(PID %s) - stopping DSO",str(self.pid))   	
        
    def deploy_contract(self):
        self.logger.info("Deploying contract...")
        # use command function because we need to get the contract address later
        receiptID = self.client.command("eth_sendTransaction", params=[{'data': BYTECODE, 'from': self.account, 'gas': TRANSACTION_GAS}])
        self.logger.info("Transaction receipt: " + receiptID)
        while True:
            sleep(5)
            self.logger.info("Waiting for contract to be mined... (block number: {})".format(self.client.command("eth_blockNumber", params=[])))
            receipt = self.client.command("eth_getTransactionReceipt", params=[receiptID])
            if receipt is not None:
                self.contract_address = receipt['contractAddress']
                break
        self.contract = MatchingContract(self.client, self.contract_address)
        self.contract.setup(self.account, MICROGRID.C_ext, MICROGRID.C_int, START_INTERVAL)
        self.logger.info("Contract address: " + self.contract_address)  
         
        
    