import datetime
import sys
import random
import pprint
import logging
logging.basicConfig(level=logging.INFO)
import pymongo
import pandas as pd
import math

from time import time, sleep
from binascii import hexlify

#LOCAL IMPORTS
from Actor import Actor
from Grafana.config import Config
from Grafana.dbase import Database
from config import *


import copy
import docker

class Offer():
    '''no need for timeLimit, because offer can be canceled for maintenance'''
    def __init__(self, ioid, cpu, ram, storage, price):
        self.ioid = ioid
        self.cpu = cpu
        self.ram = ram
        self.storage = storage
        self.price = price

class ResourceProvider(Actor):
    def __init__(self):
        # self.logger = logging.getLogger(__name__)
        self.dbase = Database()
        self.resourceTypes = {"CPU" : 0, #instructions per second
                              "storage" : 1}
        self.arch = {"arm" :1,
                     "amd64" : 0}
        self.APIclient = docker.APIClient(base_url='unix://var/run/docker.sock')
        #self.randomSetup()
        super(ResourceProvider, self).__init__(prosumer_id, ip, port,DIRECTORY_IP) #command line arguments, specifying ip and port of geth client

        # THIS IS TO HELP GRAFANA PUT IDs IN ASSCENDING ORDER
        if self.prosumer_id < 100 :
            self.ID = "0"+str(self.prosumer_id)
        if self.prosumer_id < 10 :
            self.ID = "0"+self.ID

    def post_offer(self, MIPS, ram, storage, price):
        offer = Offer(self.next_offer, MIPS, ram, storage, price)
        self.pending_offers[self.next_offer] = offer
        '''postResourceOffer(self, from_account, actorID, architecture, capCPU, capRAM, capStorage, price)'''
        self.stopWatch = {"start":time(), "running" : 1} #USING THIS TO MEASURE TIME UNTIL OFFER IS POSTED
        self.contract.postResourceOffer(self.account, self.prosumer_id, self.arch["amd64"], offer.cpu, offer.ram, offer.storage, offer.price)
        self.next_offer += 1 #defined in Prosumer.py

    def run(self):
        current_time = time()
        self.logger.info("current_time %s" %current_time)
        time_interval = int(current_time - self.epoch) // INTERVAL_LENGTH
        self.logger.info("time_interval %s" %time_interval)
        next_polling = current_time + POLLING_INTERVAL
        self.logger.info("POLLING_INTERVAL %s" %POLLING_INTERVAL)
        # we stop after the END_INTERVAL
        while time_interval <= END_INTERVAL:
          current_time = time()
          if current_time > next_polling:
            self.logger.debug("Polling events...")
            next_polling = current_time + POLLING_INTERVAL
            for event in self.contract.poll_events():
                params = event['params']
                name = event['name']
                #self.logger.info("{}({}).".format(name, params))
                if (name == "Debug"):
                    self.logger.info("{}({}).".format(name, params))
                    pass
                elif (name == "ResourceOfferPosted") and (params['actorID'] == self.prosumer_id):
                    '''ResourceOfferPosted(uint64 offerID, uint64 actorID, uint64 architecture, uint64 capCPU, uint64 capRAM, uint64 capStorage, uint64 price)'''
                    self.stopWatch["split"] = time() - self.stopWatch["start"]
                    print("Offer Posted: %s \n Post Duration: %s" %(params['offerID'],self.stopWatch["split"]))
                    self.logger.info("{}({}).".format(name, params))

                elif (name == "AssignmentAdded") and (params['resourceOfferID'] in self.created_offers):
                    '''AssignmentAdded(uint64 solutionID, uint64 jobOfferID, uint64 resourceOfferID)'''
                    self.logger.info("resource offer : {}({}).".format(name, params))

                elif (name == "AssignmentFinalized") and (params['resourceOfferID'] in self.created_offers):
                    '''AssignmentFinalized(uint64 jobOfferID, uint64 resourceOfferID)'''
                    self.logger.info("Finalized resource Offer : {}({}).".format(name,params))

          sleep(max(next_polling - time(), 0)) # Sleep until the next time to check for events from the blockchain


if __name__ == "__main__":
    prosumer_id = 101
    ip = 'localhost' #GETH CLIENT IP
    port = 10000 #GETH CLIENT PORT
    if len(sys.argv) > 1:
        prosumer_id = int(sys.argv[1])
    if len(sys.argv) > 2:
        ip = sys.argv[2]
    if len(sys.argv) > 3:
        port = sys.argv[3]
    if len(sys.argv) > 4:
        DIRECTORY_IP = sys.argv[4]

    RP = ResourceProvider()
    cpuSpeed = 990 #MHz sudo ./perf stat ls
    IPC = .2 #0.12-.30 sudo ./perf stat ls
    MIPS = math.floor(cpuSpeed * IPC)
    storage = 2708480 #MB $(df /var/lib/docker --output=avail | tail -1)
    ramTotal = 485 #MB total=$(free -m | awk 'NR==2{printf $2}') #NR==2 gives second row, printf $2 gives second entry
    ramUsed = 47 #MB used=$(free -m | awk 'NR==2{printf $3}')
    ram = math.floor(ramTotal*.9 - ramUsed)
    RP.post_offer(MIPS=MIPS, ram=ram, storage=storage*1000000, price=1) #price per IPS
    RP.run()
