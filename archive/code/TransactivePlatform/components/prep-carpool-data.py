#!/usr/bin/python3
import logging
import time
logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
import pprint
import pandas as pd
import os
import pymongo
import random

from sklearn.cluster import DBSCAN, KMeans
from geopy.distance import great_circle
import numpy as np
from shapely.geometry import MultiPoint
import matplotlib.pyplot as plt

geo_db = pymongo.MongoClient().geo
#----DROP OLD COPY------
if "residences" in geo_db.collection_names():
    geo_db.residences.drop()
if "Pickups" in geo_db.collection_names():
    geo_db.Pickups.drop()
if "Dests" in geo_db.collection_names():
    geo_db.Dests.drop()
if "places" in geo_db.collection_names():
    geo_db.places.drop()
#-----------------------

METERS_PER_MILE = 1609.34

data_dir = 'data/trip-data.csv'
# geo_db.residences.create_index([("location","2dsphere")])
# geo_db.Pickups.create_index([("location","2dsphere")])
# geo_db.Dests.create_index([("location", "2dsphere")])
geo_db.residences.create_index([("geometry","2dsphere")])
geo_db.Pickups.create_index([("geometry","2dsphere")])
geo_db.Dests.create_index([("geometry", "2dsphere")])

def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)

try :
    trip_data = pd.read_csv(data_dir)
    trip_data = trip_data.iloc[0:75]
    #pprint.pprint(trip_data.iloc[0:100])
    # from_coordinate, from_taz to_coordinate, to_taz, departure_time
except FileNotFoundError:
    cwd = os.getcwd()
    logging.info("Current Working Directory: %s" %cwd)
    logging.info("data_dir exists? : %s" %os.path.exists(data_dir))
    quit()

logging.info("# of start TAZ : %s" %trip_data.loc[:,'from_taz'].count())
logging.info("unique start TAZ : %s" %trip_data.loc[:,'from_taz'].nunique())
logging.info("# of unique start points : %s" %trip_data.loc[:,'from_coordinate'].nunique())
logging.info("# of unique end points : %s" %trip_data.loc[:,'to_coordinate'].nunique())

ix = 0
for coord in trip_data.loc[:,'to_coordinate'].unique().tolist():
    to_lat, to_lng = coord.split(" ")
    # geo_db.Dests.insert_one({"location":{"dstID":ix,
    #                                      "type":"Point",
    #                                      "coordinates":[float(to_lng),
    #                                                     float(to_lat)]}})
    geo_db.Dests.insert_one({"geometry":{"dstID":ix,
                                         "type":"Point",
                                         "coordinates":[float(to_lng),
                                                        float(to_lat)]}})
    ix +=1


pprint.pprint(list(geo_db.Dests.find({})))
# pprint.pprint("dst: %s" %list(geo_db.Dests.find({"location.coordinates": [-86.811862, 36.143494]})))
pprint.pprint("dst: %s" %list(geo_db.Dests.find({"geometry.coordinates": [-86.811862, 36.143494]})))



#---- Put from points into DB---------------------------------------------------
if  os.path.exists("data/latlng.csv"):
    df = pd.DataFrame(columns=['ID','from_lat','from_lng', 'to_lat', 'to_lng'])
    print("parse coordinate data")
    ID = 0
    for row in trip_data.itertuples():
        from_lat, from_lng = row.from_coordinate.split(" ")
        to_lat, to_lng = row.to_coordinate.split(" ")
        #print(ID, "tooo", float(to_lat), float(to_lng))
        df = df.append({'ID' : ID,
                        'from_lat':float(from_lat), 'from_lng' : float(from_lng),
                        'to_lat':float(to_lat), 'to_lng':float(to_lng)}, ignore_index=True)
        ID += 1

    dfround = df.round(6)
    df.round(6).to_csv("data/latlng.csv")

    for row in dfround.itertuples():
        from_lng = row.from_lng
        from_lat = row.from_lat
        print("from", float(from_lat), float(from_lng))
        rnd = random.random()
        if rnd <= .5:
            providing = 1
        else:
            providing = 0
        geo_db.residences.insert_one({"geometry":{"type":"Point", "coordinates":[float(from_lng),float(from_lat)]}, "properties": {"prosumer" : providing}})
        # geo_db.residences.insert_one({"location":{"type":"Point", "coordinates":[float(from_lng),float(from_lat)]}})

else:
    print("import coordinate data")
    df = pd.read_csv("data/latlng.csv")

#-------------------------------------------------------------------------------

#---- Generate pick up points---------------------------------------------------
#http://geoffboeing.com/2014/08/clustering-to-reduce-spatial-data-set-size/
coords = df.as_matrix(columns=['from_lat', 'from_lng'])
print("coords")
print(np.radians(coords))
kms_per_radian = 6371.0088
epsilon = .7 / kms_per_radian
#db = DBSCAN(eps=epsilon, min_samples=3, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
db = KMeans(n_clusters=20).fit(np.radians(coords))
cluster_labels = db.labels_
num_clusters = len(set(cluster_labels))-1
clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
#print(clusters)
print('Number of clusters: {}'.format(num_clusters))
centermost_points = clusters.map(get_centermost_point)
lats, lons = zip(*centermost_points)
rep_points = pd.DataFrame({'lon':lons, 'lat':lats})
print("rep_points \n%s" %rep_points)
#rs = rep_points.apply(lambda row: df[(df['lat']==row['lat']) and (df['lon']==row['lon'])].iloc[0], axis=1)
rs = rep_points

fig, ax = plt.subplots(figsize=[10, 6])
rs_scatter = ax.scatter(rs['lon'], rs['lat'], c='#99cc99', edgecolor='None', alpha=0.7, s=300)
df_scatter = ax.scatter(df['from_lng'], df['from_lat'], c='k', alpha=0.9, s=3)
ax.set_title('Full data set vs DBSCAN reduced set')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
#ax.legend([df_scatter, rs_scatter], ['Full set', 'Reduced set'], loc='upper right')
plt.show()

#-----------------------------------------------------------------------------
ix = 0
for point in rep_points.to_dict('records'):
    # print(point)
    geo_db.Pickups.insert_one({"geometry":{"pupID":ix, "type":"Point", "coordinates":[float(point['lon']),float(point['lat'])]}})
    # geo_db.Pickups.insert_one({"location":{"pupID":ix, "type":"Point", "coordinates":[float(point['lon']),float(point['lat'])]}})

    ix +=1
    #geo_db.Pickups.insert_many(rep_points.to_dict('records'))
pprint.pprint(list(geo_db.Pickups.find({})))
#-------------------------------------------------------------------------------

#---- Singleton test------------------------------------------------------------
if False:
    ID = 1
    src_lat, src_lng = trip_data.loc[0,'from_coordinate'].split(" ")
    pickups = list(getPickups(15, src_lat, src_lng))
    dst_lat, dst_lng = trip_data.loc[0,'to_coordinate'].split(" ")
    cp1 = Carpooler(src_lat, src_lng, dst_lat, dst_lng,pickups)
    bid = cp1.bidBuilder()
    pprint.pprint(bid)
#-------------------------------------------------------------------------------

# #---- Get in range pickup points for all trips ---------------------------------
# pickups_in_range = {}
# total = 0
# for trip in df.itertuples():
#     #pud = random.uniform(1, 5)
#     pud = 15
#     pickups = getPickups(pud, trip.from_lat, trip.from_lng)
#     if str(pickups.count()) in pickups_in_range:
#         pickups_in_range[str(pickups.count())] += 1
#     else:
#         pickups_in_range[str(pickups.count())] = 1
#     total +=1
#
#     #print (list(pickups))
# print(pickups_in_range)
# print(total)
# #-------------------------------------------------------------------------------

# P1 = Prosumer(prosumer_id=ID, ip=ETHCLIENT_IP, port=ETHCLIENT_PORT)
# quantity={
#     1: 2,
#     2: 2,
#     3: 2,
#     4: 2}
# value={
#     1: 100,
#     2: 75,
#     3: 50,
#     4: 50}
# P1.post_offer(providing=True, quantity=quantity, value=value )
# P1.run()
# while True:
#     time.sleep(1)
#     print("help")
