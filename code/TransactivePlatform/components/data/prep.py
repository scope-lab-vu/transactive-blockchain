#!/usr/bin/python3
import pymongo
import logging
import os
import pandas as pd
import pprint
import datetime
import random
METERS_PER_MILE = 1609.34

logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO)
data_dir = 'trip-data.csv'
geo_db = pymongo.MongoClient().geo
geo_db.residences.create_index([("location","2dsphere")])

try :
    trip_data = pd.read_csv(data_dir)
    # pprint.pprint(trip_data)
    # from_coordinate
    # from_taz
    # to_coordinate
    # to_taz
    # departure_time
except FileNotFoundError:
    cwd = os.getcwd()
    logging.info("Current Working Directory: %s" %cwd)
    logging.info("data_dir exists? : %s" %os.path.exists(data_dir))
    quit()

logging.info("# of start TAZ : %s" %trip_data.loc[:,'from_taz'].count())

logging.info("unique start TAZ : %s" %trip_data.loc[:,'from_taz'].nunique())
logging.info("# of unique nd points : %s" %trip_data.loc[:,'to_coordinate'].nunique())

#---- Put from points into DB---------------------------------------------------
for row in trip_data.itertuples():
    lat, lng = row.from_coordinate.split(" ")
    geo_db.residences.insert_one({"location":{"type":"Point", "coordinates":[float(lng),float(lat)]}})
#-------------------------------------------------------------------------------

#---- My location---------------------------------------------------------------
src_lat, src_lng = trip_data.loc[0,'from_coordinate'].split(" ")
#-------------------------------------------------------------------------------

#---- My Destination------------------------------------------------------------
dst_lat, dst_lng = trip_data.loc[0,'to_coordinate'].split(" ")
#-------------------------------------------------------------------------------

#----Distance-------------------------------------------------------------------
# https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
from math import cos, asin, sqrt
def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295     #Pi/180
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a)) #2*R*asin...
#-------------------------------------------------------------------------------

#----Departure time interval----------------------------------------------------
today = datetime.datetime.combine(datetime.date.today(),datetime.time(hour=7))
departure_times = []
for i in range(9):
    #print (i)
    departure_times.append(today + datetime.timedelta(minutes=15*i))
#print(departure_times)
earliest = random.choice(departure_times)
index = departure_times.index(earliest)
latest = random.choice(departure_times[index:])
#-------------------------------------------------------------------------------

#----How Far I'll travel to pick up---------------------------------------------
pud = random.uniform(1, 5)
print("Pick up distance in miles %s" %pud)
#-------------------------------------------------------------------------------

#----Value----------------------------------------------------------------------
my_value = random.randint(1,100)

#----providing------------------------------------------------------------------
rnd = random.random()
if rnd <= .1:
    providing = True
else:
    providing = False
#-------------------------------------------------------------------------------

#----seats available/required---------------------------------------------------
rnd = random.random()
if rnd >=.5:
    num_seats = 1
elif rnd >=.2 and rnd<.5:
    num_seats = 2
else:
    num_seats = 3
print("Number of seats %s" %num_seats)
#-------------------------------------------------------------------------------

#----Within pickup range--------------------------------------------------------
near = geo_db.residences.find({ "location":
                                { "$nearSphere":
                                  { "$geometry":
                                    { "type": "Point", "coordinates": [ float(src_lng), float(src_lat) ] }, #[ <longitude>, <latitude> ]
                                    "$maxDistance": pud * METERS_PER_MILE } } })
print(near.count())
#-------------------------------------------------------------------------------



geo_db.residences.drop()
logging.info("count: %s" %geo_db.residences.count())
