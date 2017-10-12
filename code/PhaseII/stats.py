import sys
from datetime import datetime
filename=sys.argv[1]
data=open(filename).readlines()
postedOffers={}
TradeAdded=[]
for line in data:
    if 'postSellingOffer' in line:
       offertime=datetime.strptime( line.split('/')[0].strip().split(',')[0],'%Y-%d-%m %H:%M:%S')
       intervalstart= int(line.split('/')[2].split(',')[1].strip())
       if intervalstart not in postedOffers.keys():
        postedOffers[intervalstart]=[]
       postedOffers[intervalstart].append(offertime)
        
for line in data:
    if 'TradeAdded' in line:
       offertime=datetime.strptime( line.split('/')[0].strip().split(',')[0],'%Y-%d-%m %H:%M:%S')
       intervalstart= int(line.split('{')[1].split(',')[0].split(':')[1].strip())
       power=int(line.split('{')[1].split(',')[5].strip("}).").split(':')[1].strip())/1000.0
       if intervalstart not in TradeAdded.keys():
        TradeAdded[intervalstart]=[]
       TradeAdded[intervalstart].append([offertime,power])        
        
        
#intervals=range(1,96)
#for interval in intervals:
#  searchstring="postSellingOffer({}".format(interval)
#  for line in data:
  