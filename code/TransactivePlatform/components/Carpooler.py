import datetime
import sys
import random
import pprint
import logging
logging.basicConfig(level=logging.INFO)
from math import cos, asin, sqrt, floor, atan2, sin
import pymongo
import pandas as pd
from Prosumer import Prosumer
METERS_PER_KM = 1000
from time import time, sleep
from config import *

from Grafana.config import Config
from Grafana.dbase import Database
import copy

#class Carpooler(Prosumer.Prosumer):
#    def __init__(self, srclat, srclng, dstlat, dstlng, prosumer_id, ip, port):
class Carpooler(Prosumer):
    def __init__(self,srclat,srclng,dstlat,dstlng):
        self.geo_db = pymongo.MongoClient().geo
        self.quantity = {}
        self.value = {}
        self.seats = 0
        self.providing = 0
        self.earliest = 0
        self.latest = 0
        self.srclat = srclat
        self.srclng = srclng
        self.dstlat = dstlat
        self.dstlng = dstlng
        self.pud = 1000
        self.dst = str(dstlat) +","+str(dstlng)
        self.departure_times = []
        self.dbase = Database()
        #self.randomSetup()
        super(Carpooler, self).__init__(prosumer_id, ip, port)
        if self.prosumer_id < 100 :
            self.ID = "0"+str(self.prosumer_id)
        if self.prosumer_id < 10 :
            self.ID = "0"+self.ID

    def bidBuilder(self,pups):
        self.logger.info("num pickups : %s"%len(pups))
        if pups:
            for pup in pups:
                # pup_lng, pup_lat = pup['location']['coordinates']
                # pup_id = pup['location']['pupID']
                pup_lng, pup_lat = pup['geometry']['coordinates']
                pup_id = pup['geometry']['pupID']
                pup_dist = self.distance(float(self.srclat), float(self.srclng), pup_lat, pup_lng)
                self.logger.info("Distance to pickup point : %s" %pup_dist)
                dest_dist = self.distance(pup_lat, pup_lng, float(self.dstlat), float(self.dstlng))
                self.logger.info("Distance to destination from pup %s" %dest_dist)
                for time in self.departure_times[self.earliest:self.latest+1]:
                    #t = time.strftime("%d/%m/%Y %H:%M")
                    t = int(time.timestamp())
                    #src = str(pup_lat)+","+str(pup_lng)
                    #key = src+"_"+t+"_"+self.dst
                    # print(pup_id)
                    # print(t)
                    # print(time.strftime("%d/%m/%Y %H:%M"))
                    # print(self.dst_id)
                    key = int(str(t)+str(pup_id)+str(self.dst_id))
                    #print("Key : %s" %key)
                    self.quantity[key] = self.seats
                    self.value[key] = floor(pup_dist+dest_dist)
            #pprint.pprint(self.quantity)
            #pprint.pprint(self.value)
            bid = (self.providing, self.quantity, self.value)
        else:
            self.logger.info("no pickup in range")
            bid = ()
        return bid


    def randomSetup(self):
        #--Random number of seats--
        rnd = random.random()
        if rnd >=.5:
            self.seats = 1
        elif rnd >=.2 and rnd<.5:
            self.seats = 2
        else:
            self.seats = 3
        #--Randomly assign departure interval--
        today = datetime.datetime.combine(datetime.date.today(),datetime.time(hour=7))
        for i in range(9):
            self.departure_times.append(today + datetime.timedelta(minutes=15*i))
        #pprint.pprint(self.departure_times)
        earliest = random.choice(self.departure_times)
        self.logger.info("earliest time %s" %earliest)
        self.earliest = self.departure_times.index(earliest)
        self.logger.info("earliest index %s" %self.earliest)
        latest = random.choice(self.departure_times[self.earliest:])
        self.logger.info("latest time %s" %latest)
        self.latest = self.departure_times.index(latest)

        self.directDist = self.distance(float(self.srclat), float(self.srclng), float(self.dstlat), float(self.dstlng))
        self.logger.info("Direct Distance : %s" %self.directDist)
        self.mid = self.midpoint(float(self.srclat), float(self.srclng), float(self.dstlat), float(self.dstlng))
        self.pud = self.directDist*.6
        #self.pud = random.randint(1, floor(self.directDist))
        #----Depending on provider state from mongodb set pups------------------------------------
        if self.providing:
            self.pups = list(self.getPickups(self.pud, self.mid[0],self.mid[1]))
        else:
            self.pups = list(self.getPickups(self.pud, self.srclat, srclng))
        print("mid.pups: %s" %list(self.getPickups(self.pud, self.mid[0],self.mid[1])))
        print("home.pups: %s" %list(self.getPickups(self.pud, self.srclat, srclng)))

    #----Distance-------------------------------------------------------------------
    # https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula

    def distance(self, lat1, lon1, lat2, lon2):
        '''Distance in km'''
        p = 0.017453292519943295     #Pi/180 degrees to radians
        a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 12742 * asin(sqrt(a)) #2*R*asin...

    def midpoint(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295 #Pi/180 degrees to radians
        #lat/lon for lati­tude/longi­tude in degrees, and φ/λ for lati­tude/longi­tude
        rlat1 = lat1*p
        rlat2 = lat2*p
        rlon1 = lon1*p
        drlat = (lat2-lat1)*p;
        drlon = (lon2-lon1)*p
        Bx = cos(rlat2) * cos(drlon)
        By = cos(rlat2) * sin(drlon)
        rlat3 = atan2(sin(rlat1) + sin(rlat2),
                      sqrt( (cos(rlat1)+Bx) * (cos(rlat1)+Bx) + By*By ))
        rlon3 = rlon1 + atan2(By, cos(rlat1)+Bx)
        lat3 = rlat3/p
        lon3 = rlon3/p
        print ("lat1: %s lon1: %s" %(lat1,lon1))
        print ("lat3: %s lon3: %s" %(lat3,lon3))
        print ("lat2: %s lon2: %s" %(lat2,lon2))
        return [lat3,lon3]

    #-------------------------------------------------------------------------------

    def getPickups(self, pud, lat, lng):
        print("in pups")
        print(pud, lat, lng)
        # near = self.geo_db.Pickups.find({ "location":
        #                                 { "$nearSphere":
        #                                   { "$geometry":
        #                                     { "type": "Point", "coordinates": [ float(lng), float(lat) ] }, #[ <longitude>, <latitude> ]
        #                                     "$maxDistance": pud * METERS_PER_KM } } })
        near = self.geo_db.Pickups.find({ "geometry":
                                        { "$nearSphere":
                                          { "$geometry":
                                            { "type": "Point", "coordinates": [ float(lng), float(lat) ] }, #[ <longitude>, <latitude> ]
                                            "$maxDistance": pud * METERS_PER_KM } } })

        print("Pickups in %s KMs : %s " %(pud, near.count()))
        return(near)


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
                  pass
                  #self.logger.info("{}({}).".format(name, params))
              elif (name == "OfferCreated") and (params['prosumer'] == self.prosumer_id):
                stopWatch = {"start":time(), "running" : 1}
                self.logger.info("{}({}).".format(name, params))
                offer = self.pending_offers.pop(params['misc'])
                #pprint.pprint(offer)
                self.created_offers[params['ID']] = offer
                self.current_quantity = copy.copy(offer['quantity'])
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
                #offer['quantity'].pop(params['resourceType'])
                self.current_quantity.pop(params['resourceType'])
                print("Postpop")
                pprint.pprint(self.created_offers)
                #if not len(offer['quantity']):
                if not len(self.current_quantity):
                  self.contract.postOffer(self.account, params['ID'])
              elif (name == "OfferPosted") and (params['ID'] in self.created_offers):
                  stopWatch["split"] = time() - stopWatch["start"]
                  print("Offer Posted: %s \n Post Duration: %s" %(params['ID'],stopWatch["split"]))
                  self.logger.info("{}({}).".format(name, params))
              elif (name == "AssignmentAdded") and (params['providingOfferID'] in self.created_offers):
                  #AssignmentAdded(uint64 ID, uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value, uint64 objective);
                  self.logger.info("providing offer : {}({}).".format(name, params))
              elif (name == "AssignmentAdded") and (params['consumingOfferID'] in self.created_offers):
                  #AssignmentAdded(uint64 ID, uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value, uint64 objective);
                  self.logger.info("consuming offer : {}({}).".format(name, params))
              elif (name == "AssignmentFinalized") and (params['providingOfferID'] in self.created_offers):
                  resourceType = str(params['resourceType'])
                  timestamp = resourceType[:10]
                  pickup_time = datetime.datetime.fromtimestamp(int(timestamp))
                  src = resourceType[10:-1]
                  dst = resourceType[-1]
                  carpoolerID = self.prosumer_id
                  offerID = params['providingOfferID']
                  print("keys: %s" %self.created_offers.keys())
                  pprint.pprint(self.created_offers)
                  print("RT: {}".format(resourceType))
                  quantity = params['quantity']
                  #my_quantity = self.created_offers[offerID]['quantity'][resourceType]
                  #print("My offer : {} \n Matched Offer: {}".format(my_quantity, quantity))
                  value = params['value']
                  self.logger.info("Finalized Providing Offer : {}({}).".format(name,params))
                  print(pickup_time, src, dst, carpoolerID, offerID, type(quantity))
                  tag_dict = {'ID' : carpoolerID, 'src' : src, 'dst':dst}
                  self.dbase.log(pickup_time-datetime.timedelta(minutes=15), tag_dict, "Q_produce", 0)
                  self.dbase.log(pickup_time-datetime.timedelta(minutes=15), tag_dict, "V_produce", 0)
                  self.dbase.log(pickup_time, tag_dict, "Q_produce", quantity)
                  self.dbase.log(pickup_time, tag_dict, "V_produce", value)
                  self.dbase.log(pickup_time+datetime.timedelta(minutes=15), tag_dict, "Q_produce", 0)
                  self.dbase.log(pickup_time+datetime.timedelta(minutes=15), tag_dict, "V_produce", 0)
              elif (name == "AssignmentFinalized") and (params['consumingOfferID'] in self.created_offers):
                  resourceType = str(params['resourceType'])
                  timestamp = resourceType[:10]
                  pickup_time = datetime.datetime.fromtimestamp(int(timestamp))
                  src = resourceType[10:-1]
                  dst = resourceType[-1]
                  carpoolerID = self.prosumer_id
                  offerID = params['consumingOfferID']
                  print("keys: %s" %self.created_offers.keys())
                  pprint.pprint(self.created_offers)
                  print("RT: {}".format(resourceType))
                  quantity = params['quantity']
                  #my_quantity = self.created_offers[offerID]['quantity'][resourceType]
                  #print("My offer : {} \n Matched Offer: {}".format(my_quantity, quantity))
                  value = params['value']
                  self.logger.info("Finalized Consuming Offer : {}({}).".format(name,params))
                  print(pickup_time, src, dst, carpoolerID, offerID, type(quantity))
                  tag_dict = {'ID' : carpoolerID, 'src' : src, 'dst':dst}
                  self.dbase.log(pickup_time-datetime.timedelta(minutes=15), tag_dict, "Q_consume", 0)
                  self.dbase.log(pickup_time-datetime.timedelta(minutes=15), tag_dict, "V_consume", 0)
                  self.dbase.log(pickup_time, tag_dict, "Q_consume", quantity)
                  self.dbase.log(pickup_time, tag_dict, "V_consume", value)
                  self.dbase.log(pickup_time+datetime.timedelta(minutes=15), tag_dict, "Q_consume", 0)
                  self.dbase.log(pickup_time+datetime.timedelta(minutes=15), tag_dict, "V_consume", 0)
              elif (name == "FinalizeRequested"):
                  logging.info("{}({}).".format(name, params))
              elif(name == "FinalizeComplete"):
                  logging.info("{}({}).".format(name, params))

          sleep(max(next_polling - time(), 0))


if __name__ == "__main__":
    prosumer_id = 101
    ip = 'localhost'
    port = 10000
    if len(sys.argv) > 1:
        prosumer_id = int(sys.argv[1])
    if len(sys.argv) > 2:
        ip = sys.argv[2]
    if len(sys.argv) > 3:
        port = sys.argv[3]
    if len(sys.argv) > 4:
        trip_file=sys.argv[4]
    trips = (pd.read_csv(trip_file)).round(6)
    my_trip = trips.loc[trips['ID'] == prosumer_id]
    #print("my trip \n%s" %my_trip)
    srclat = my_trip.loc[prosumer_id,'from_lat']
    srclng = my_trip.loc[prosumer_id,'from_lng']
    dstlat = my_trip.loc[prosumer_id,'to_lat']
    dstlng = my_trip.loc[prosumer_id,'to_lng']

    CP = Carpooler(srclat,srclng,dstlat,dstlng)
    #pprint.pprint("all dst: %s" %list(CP.geo_db.Dests.find({})))
    print(srclat,srclng,dstlat,dstlng)
    #pprint.pprint("dst: %s" %list(CP.geo_db.Dests.find({"location.coordinates": [dstlng, dstlat]})))

    #dst = list(CP.geo_db.Dests.find({"location.coordinates": [dstlng, dstlat]}))
    #CP.dst_id = dst[0]['location']['dstID']
    #GET THE ID OF MY DESTINATION
    dst = list(CP.geo_db.Dests.find({"geometry.coordinates": [dstlng, dstlat]}))
    CP.dst_id = dst[0]['geometry']['dstID']

    residence = list(CP.geo_db.residences.find({"geometry.coordinates": [srclng, srclat]}))[0]
    CP.providing = residence['properties']['prosumer']

    #print("pups: %s" %list(CP.geo_db.Pickups.find({})))
    # pups = list(CP.getPickups(self.pud, self.srclat, srclng))
    # pups = list(CP.getPickups(self.pud, self.mid[0],self.mid[1
    CP.randomSetup()
    bid = CP.bidBuilder(CP.pups)
    print(type(bid))
    if bid:
        print("BID:")
        pprint.pprint(bid)
        print("post offer")
        CP.post_offer(providing=bid[0], quantity=bid[1], value=bid[2])
        earliest = CP.departure_times[CP.earliest]
        latest = CP.departure_times[CP.latest]
        for pup in CP.pups:
            src_id = pup['geometry']['pupID']
            tag_dict = {'ID' : CP.ID, 'src' : src_id, 'dst':CP.dst_id}
            #tag_dict = {'ID' : CP.ID}
            CP.dbase.log(earliest-datetime.timedelta(minutes=15), tag_dict, "Providing:%s" %CP.providing, 0)
            CP.dbase.log(earliest, tag_dict, "Providing:%s" %CP.providing, CP.seats)
            CP.dbase.log(latest, tag_dict, "Providing:%s" %CP.providing, CP.seats)
            CP.dbase.log(latest+datetime.timedelta(minutes=15), tag_dict, "Providing:%s" %CP.providing, 0)


        print("run")
        CP.run()
    else:
        print("providing: %s, directDist: %s, Pickup distance %s"
        %(CP.providing, CP.directDist, CP.pud))
        sys.exit()
