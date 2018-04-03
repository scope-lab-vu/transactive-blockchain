#!/usr/bin/python3
import logging
logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
import pandas as pd
import os
import pymongo

# This line would make the next two work because context adds components to the path
# However the last will work on its own.
from context import carpooler
#import components.Prosumer as Prosumer
#from components import Prosumer
#from context import Prosumer

METERS_PER_MILE = 1609.34

data_dir = 'data/trip-data.csv'
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
#cp1 = carpooler.Carpooler(src_lat, src_lng, dst_lat, dst_lng, 101, 'localhost', 9000)
cp1 = carpooler.Carpooler(src_lat, src_lng, dst_lat, dst_lng)
print(cp1.seats)
cp1.run()
