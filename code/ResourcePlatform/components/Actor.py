import datetime
import sys
import random
import pprint
import logging
logging.basicConfig(level=logging.INFO)
import pymongo
import pandas as pd
from Prosumer import Prosumer
from time import time, sleep
from config import *

from Grafana.config import Config
from Grafana.dbase import Database
import copy
import docker

class Actor(Prosumer):
    def __init__(self, providing):
        self.quantity = {}
        self.value = {}
        self.providing = providing
        print("providing %s" %self.providing)
        self.dbase = Database()
        self.resourceTypes = {"instructions" : 0,
                              "storage" : 1}
        #self.randomSetup()
        super(Actor, self).__init__(prosumer_id, ip, port) #command line arguments, specifying ip and port of geth client

        # THIS IS TO HELP GRAFANA PUT IDs IN ASSCENDING ORDER
        if self.prosumer_id < 100 :
            self.ID = "0"+str(self.prosumer_id)
        if self.prosumer_id < 10 :
            self.ID = "0"+self.ID

    def bidBuilder(self, jobname):
        image_dict = APIclient.inspect_image(jobname)
        repoDigestSha = image_dict["RepoDigests"][0]
        IDsha = image_dict["Id"]
        size = image_dict["Size"]
        os = image_dict["Os"]
        arch = image_dict["Architecture"]
        # bid = (providing, {RT_float:quantity}, {RT_float:value})
        bid = (0, {self.resourceTypes["storage"]: size}, {self.resourceTypes["storage"]: 100})
        return bid

        # Alternate way to get data
        #     dist_dict = APIclient.inspect_distribution(jobname)
        #     pprint.pprint(dist_dict)
        #     sha256 = dist_dict['Descriptor']['digest']
        #     size = dist_dict['Descriptor']['size']
        #     os = dist_dict['Platforms'][0]['os']
        #     arch = dist_dict['Platforms'][0]['architecture']
        # print(sha256, size, os, arch)


    def setup(self):
        pass

    def run(self):
        current_time = time()
        time_interval = int(current_time - self.epoch) // INTERVAL_LENGTH
        self.logger.info("time_interval %s" %time_interval)
        next_polling = current_time + POLLING_INTERVAL
        # we stop after the END_INTERVAL
        while time_interval <= END_INTERVAL:
          current_time = time()
          if current_time > next_polling:
            #self.logger.debug("Polling events...")
            next_polling = current_time + POLLING_INTERVAL
            for event in self.contract.poll_events():
              params = event['params']
              name = event['name']
              #self.logger.info("{}({}).".format(name, params))
              if (name == "Debug"):
                  #self.logger.info("{}({}).".format(name, params))
                  pass
              elif (name == "OfferCreated") and (params['prosumer'] == self.prosumer_id):
                stopWatch = {"start":time(), "running" : 1} #USING THIS TO MEASURE TIME UNTIL OFFER IS POSTED
                self.logger.info("{}({}).".format(name, params))
                offer = self.pending_offers.pop(params['misc']) #post_offer in Prosumer.py adds offers to pending_offers.
                #pprint.pprint(offer)
                self.created_offers[params['ID']] = offer
                self.current_quantity = copy.copy(offer['quantity']) #NEED THIS OTHERWISE OFFERUPDATED WILL EMPTY self.created_offers.
                print("NEWLY CREATED OFFER")
                pprint.pprint(self.created_offers)
                for res_type in offer['quantity']:
                  pprint.pprint(self.created_offers[params['ID']]['quantity'][res_type])
                  self.contract.updateOffer(self.account, params['ID'], res_type, offer['quantity'][res_type], offer['value'][res_type])
              elif (name == "OfferUpdated") and (params['ID'] in self.created_offers):
                self.logger.info("{}({}).".format(name, params))
                offer = self.created_offers[params['ID']]
                print("Prepop")
                pprint.pprint(self.created_offers)
                self.current_quantity.pop(params['resourceType'])
                print("Postpop")
                pprint.pprint(self.created_offers)
                #IF THERE ARE MORE ENTRIES IN AN OFFER, KEEP POSTING
                if not len(self.current_quantity):
                  self.contract.postOffer(self.account, params['ID'])
              elif (name == "OfferPosted") and (params['ID'] in self.created_offers):
                  stopWatch["split"] = time() - stopWatch["start"]
                  print("Offer Posted: %s \n Post Duration: %s" %(params['ID'],stopWatch["split"]))
                  self.logger.info("{}({}).".format(name, params))
              elif (name == "AssignmentAdded") and (params['providingOfferID'] in self.created_offers):
                  self.logger.info("providing offer : {}({}).".format(name, params))
              elif (name == "AssignmentAdded") and (params['consumingOfferID'] in self.created_offers):
                  self.logger.info("consuming offer : {}({}).".format(name, params))
              elif (name == "AssignmentFinalized") and (params['providingOfferID'] in self.created_offers):
                  self.logger.info("Finalized Providing Offer : {}({}).".format(name,params))
              elif (name == "AssignmentFinalized") and (params['consumingOfferID'] in self.created_offers):
                  self.logger.info("Finalized Consuming Offer : {}({}).".format(name,params))
              elif (name == "FinalizeRequested"):
                  logging.info("{}({}).".format(name, params))
              elif(name == "FinalizeComplete"):
                  logging.info("{}({}).".format(name, params))

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
        providing = sys.argv[4]
    if len(sys.argv) > 5 :
        jobspath = sys.argv[5]
    A = Actor(providing)

    jobpath = "/home/riaps/projects/transactive-blockchain/code/ResourcePlatform/jobs/job0"
    jobname = "eiselesr/job0"
    APIclient = docker.APIClient(base_url='unix://var/run/docker.sock')
    client = docker.from_env()
    client.login(username='eiselesr', password='eiselesr@docker')

    #build image
    image = client.images.build(path=jobpath, tag=jobname)[0]
    #push image
    for line in client.images.push(jobname, stream=True):
        print (line)

    bid = A.bidBuilder(jobname)
    print(type(bid))
    if bid:
        print("BID:")
        pprint.pprint(bid)
        print("post offer")
        A.post_offer(providing=bid[0], quantity=bid[1], value=bid[2])
        print("run")
        A.run()
    else:
        print("no bid")
        sys.exit()
