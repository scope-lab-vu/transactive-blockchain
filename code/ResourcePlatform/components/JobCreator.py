import datetime
import sys
import random
import pprint
import logging
logging.basicConfig(level=logging.INFO)
import pymongo
import pandas as pd

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
    def __init__(self,image_dict, ioid, timeLimit, price):
        self.repoDigestSha = image_dict["RepoDigests"][0]
        self.IDsha = image_dict["Id"].split(":")[1]
        self.IDint = int(self.IDsha, 16)
        self.storage = image_dict["Size"] #in bytes
        self.os = image_dict["Os"]
        self.arch = image_dict["Architecture"]
        self.ioid = ioid #internal offer ID?
        self.timeLimit = timeLimit
        self.price = price
        logging.info("job arch is %s" %self.arch)


class JobCreator(Actor):
    def __init__(self):
        # self.logger = logging.getLogger(__name__)
        self.quantity = {}
        self.value = {}
        self.dbase = Database()
        self.resourceTypes = {"instructions" : 0,
                              "storage" : 1}
        self.archTypes = {"amd64" : 0,
                          "arm" :1}
        self.APIclient = docker.APIClient(base_url='unix://var/run/docker.sock')
        #self.randomSetup()
        super(JobCreator, self).__init__(prosumer_id, ip, port, DIRECTORY_IP) #command line arguments, specifying ip and port of geth client

        # THIS IS TO HELP GRAFANA PUT IDs IN ASSCENDING ORDER
        if self.prosumer_id < 100 :
            self.ID = "0"+str(self.prosumer_id)
        if self.prosumer_id < 10 :
            self.ID = "0"+self.ID

    def post_offer(self, jobname, timeLimit, price):
        image_dict = self.APIclient.inspect_image(jobname)
        offer = Offer(image_dict, self.next_offer, timeLimit, price)
        self.pending_offers[self.next_offer] = offer
        self.contract.createJobOffer(self.account, self.prosumer_id, offer.timeLimit, offer.price, offer.ioid)
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

                elif (name == "JobOfferCreated") and (params['actorID'] == self.prosumer_id):
                    '''JobOfferCreated(uint64 offerID, uint64 actorID, uint64 timeLimit, uint64 price, uint ioid)'''
                    stopWatch = {"start":time(), "running" : 1} #USING THIS TO MEASURE TIME UNTIL OFFER IS POSTED
                    self.logger.info("{}({}).".format(name, params))
                    offer = self.pending_offers.pop(params['ioid']) #post_offer in Actor.py adds offers to pending_offers.
                    self.created_offers[params['offerID']] = offer
                    '''updateJobOffer(self, from_account, offerID, architecture, reqCPU, reqRAM, reqStorage, imageHash)'''
                    self.contract.updateJobOffer(from_account=self.account, offerID=params['offerID'],
                                                 architecture=self.archTypes[offer.arch], reqCPU=50, #MIPS
                                                 reqRAM=50, reqStorage=offer.storage, imageHash = offer.IDint)

                elif (name == "JobOfferUpdated") and (params['offerID'] in self.created_offers):
                    '''JobOfferUpdated(uint64 offerID, uint64 architecture, uint64 reqCPU, uint64 reqRAM, uint64 reqStorage, string imageHash)'''
                    self.logger.info("{}({}).".format(name, params))
                    print("JobCreator.CREATED OFFERS:")
                    pprint.pprint(self.created_offers)
                    self.contract.postJobOffer(self.account, params['offerID'])

                elif (name == "JobOfferPosted") and (params['offerID'] in self.created_offers):
                    '''JobOfferPosted(uint64 offerID)'''
                    stopWatch["split"] = time() - stopWatch["start"]
                    print("Offer Posted: %s \n Post Duration: %s" %(params['offerID'],stopWatch["split"]))
                    self.logger.info("{}({}).".format(name, params))

                elif (name == "AssignmentAdded") and (params['jobOfferID'] in self.created_offers):
                    '''AssignmentAdded(uint64 solutionID, uint64 jobOfferID, uint64 resourceOfferID)'''
                    self.logger.info("job offer : {}({}).".format(name, params))

                elif (name == "AssignmentFinalized") and (params['jobOfferID'] in self.created_offers):
                    '''AssignmentFinalized(uint64 jobOfferID, uint64 resourceOfferID)'''
                    self.logger.info("Finalized job Offer : {}({}).".format(name,params))

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
    if len(sys.argv) > 4 :
        jobspath = sys.argv[4]
    if len(sys.argv) > 5:
        DIRECTORY_IP = sys.argv[5]
    A = JobCreator()

    jobpath = "/home/riaps/projects/transactive-blockchain/code/ResourcePlatform/jobs/job0"
    jobname = "eiselesr/job0"

    client = docker.from_env()
    client.login(username='eiselesr', password='eiselesr@docker')

    #build image
    image = client.images.build(path=jobpath, tag=jobname)[0]
    #push image
    for line in client.images.push(jobname, stream=True):
        print (line)


    A.post_offer(jobname=jobname, timeLimit=60, price=10000 )#price units will have to be small, cents or less probably.
    A.run()
