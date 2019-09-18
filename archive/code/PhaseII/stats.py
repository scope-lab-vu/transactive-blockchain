#---------------------------------------------------------------------
#  This script computes the turn around time for our blockchain based
# transactive energy solver. It is meant to be run from the shell with the
#  prosumer.sh script and >> the print statements written to a csv file.
#---------------------------------------------------------------------

import sys
from datetime import datetime

filename=sys.argv[1]
data=open(filename).readlines()
postAttempt={}
postedOffers={}
TradeAdded={}
TAT = {}

#---------------------------------------------------------------------
#  Get the ID of the prosumer.
#  This was added to id the data to be able to color it when plotting
# It finds the first line in the file containing the id and saves it.
#---------------------------------------------------------------------
sellerID = None
for line in data:
    if 'postBuyingOffer' in line:
        ID = line.split('(')[1].split(',')[0]
        break
    if 'postSellingOffer' in line:
        ID = line.split('(')[1].split(',')[0]
        break
print(ID , end='')

#---------------------------------------------------------------------
#  Captures the time of the first attempt to post an offer
#
#---------------------------------------------------------------------
for line in data:
    if 'postSellingOffer' in line:
        offertime=datetime.strptime( line.split('/')[0].strip().split(',')[0],'%Y-%d-%m %H:%M:%S')
        # the offer has a start interval time and an end interval. I'm capturing the start time.
        intervalstart= int(line.split('/')[2].split(',')[1].strip())
        power = int(line.split('(')[1].split(',')[-1].split(')')[0])/1000.0
        #print(power)
        if intervalstart not in postAttempt.keys():
            postAttempt[intervalstart]=[]
        postAttempt[intervalstart].append([offertime, power])
        #prosumer_id = line.split('(')[1].split(',')[0]
        #print(prosumer_id)
    elif 'postBuyingOffer' in line:
        offertime=datetime.strptime( line.split('/')[0].strip().split(',')[0],'%Y-%d-%m %H:%M:%S')
        intervalstart= int(line.split('/')[2].split(',')[1].strip())
        power = int(line.split('(')[1].split(',')[-1].split(')')[0])/1000.0
        #print(power)
        if intervalstart not in postAttempt.keys():
            postAttempt[intervalstart]=[]
        postAttempt[intervalstart].append([offertime, power])

#---------------------------------------------------------------------
#  This is not used currently.
#  This would be used get a lookup for the random IDs to determine
#  the "post__offer" and "TradeAdded". It could also be used to identify
#  who sold what to whom by looking at all the data. But that kind of defeats
# the point.
#---------------------------------------------------------------------
for line in data:
    if 'SellingOfferPosted' in line:
        offer = eval(line.split('(')[1].split(')')[0].strip())
        #print("offer %s" %offer)
        postedOffers[offer['ID']] = offer

#print(postedOffers)

#---------------------------------------------------------------------
#  This creates a dictionary containing the time stamp of the first time
#  that a posted offer is added to a potential trade.
#---------------------------------------------------------------------
for line in data:
    if 'TradeAdded' in line:
        #trade is a dictionary of this form:
        # {'objective': 84600, 'sellerID': 35, 'buyerID': 737, 'time': 35, 'power': 400, 'solutionID': 3}
        trade = eval(line.split('(')[1].split(')')[0].strip())
        #print(trade)
        offertime=datetime.strptime( line.split('/')[0].strip().split(',')[0],'%Y-%d-%m %H:%M:%S')
        #print("MYsplit %s" %(line.split('{')[1].split(',')[1].split(':')[1].strip()))
        intervalstart= int(trade['time'])
        power=int(trade['power'])/1000.0
        if intervalstart not in TradeAdded.keys():
            TradeAdded[intervalstart]=[]

        TradeAdded[intervalstart].append([offertime,power])

#---------------------------------------------------------------------
#  The datasets do not always line up so this fills the missing data
#  as well as prints the time interval we are computing the turn around
#  time for. This should only be run once if generating a csv since we
# don't need the time interval between every row of time delta data.
#  I did this by running this script once on a single file then copying
# the intervals. Then commented this out and ran the prosumer.sh script
#---------------------------------------------------------------------
#ix = 28
#for interval in TradeAdded.keys():
    # fill in missing data
    #while(ix < interval):
    #    print(str(ix)+ ',' , end='')
    #    print(',' + str(0))
    #    ix = ix + 1
    #ix = ix + 1 #keep up with the interval
    #print("poff %s" %postAttempt[interval][0][0])
    #print("test %s" %TradeAdded[interval][0][0])
    #print(str(interval) + ",", end='')
#---------------------------------------------------------------------
#  The datasets do not always line up so this fills the missing data.
#  This outputs the time elapsed between posting and adding to a trade
#---------------------------------------------------------------------
ix = 28
for interval in sorted(TradeAdded.keys()):
    # fill in missing data
    while(ix < interval):
        print(',' + str(0), end='')
        #print(str(ix) + ',' + str(0))
        ix = ix + 1
    ix = ix + 1 #keep up with the interval
    #print("poff %s" %postAttempt[interval][0][0])
    #print("test %s" %TradeAdded[interval][0][0])

    #ix can go out of bounds so we handle that.
    try:
        TAT[interval] = sorted(TradeAdded[interval])[0][0] - postAttempt[interval][0][0]
        print(',' + str(TAT[interval]), end='')
        #print(str(interval) + ',' + str(TAT[interval]))
    except KeyError:
        # no more offers are posted
        break

print("")
