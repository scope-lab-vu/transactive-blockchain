import sys
from datetime import datetime

filename=sys.argv[1]
data=open(filename).readlines()

#find buyers
# buyerID = None
# for line in data:
#     if 'postBuyingOffer' in line:
#         buyerID = line.split('(')[1].split(',')[0]
#         print (buyerID, end='')
#         break
#     if 'postSellingOffer' in line:
#         break

sellerID = None
for line in data:
    if 'postBuyingOffer' in line:
        quit()
    if 'postSellingOffer' in line:
        sellerID = line.split('(')[1].split(',')[0]
        break

#print(sellerID)

postAttempt={}
for line in data:
    if 'postSellingOffer' in line:
        offertime=datetime.strptime( line.split('/')[0].strip().split(',')[0],'%Y-%d-%m %H:%M:%S')
        intervalstart= int(line.split('/')[2].split(',')[1].strip())
        power = int(line.split('(')[1].split(',')[-1].split(')')[0])/1000.0
        #print(power)
        if intervalstart not in postAttempt.keys():
            postAttempt[intervalstart]=[]
        postAttempt[intervalstart].append([offertime, power])

postedOffers={}
for line in data:
    if 'SellingOfferPosted' in line:
        offer = eval(line.split('(')[1].split(')')[0].strip())
        #print("offer %s" %offer)
        postedOffers[offer['ID']] = offer

#
# buyerID = {}
interval = 0
ix = 1
trades = {}
wasTrade = True
solutionID = 0
for line in data:
    if 'Posting offers for interval' in line:
        interval = int(line.split('interval')[1].split('...')[0])
        if not wasTrade:
            #print(',' + str(0) + ',' + str(0), end='')
            pass

        #print("")
        while(ix < interval):
            trades[ix] = [0]
            #print(' ' + str(ix), end='')
            #print(',' + str(0) + ',' + str(0))
            trades[ix].append(0)
            ix = ix + 1
        ix = ix + 1
        #print("this interval %s" %interval)
        #print('\n')
        #I don't recall what this try was for exactly
        try:
            trades[interval] = postAttempt[interval][0][1]
            #print(trades.keys())
            #trades[interval].append(postAttempt[interval][0][1])
            #print(str(interval) +','+ str(postAttempt[interval][0][1]), end='')
        except KeyError:
            pass
            #print("wtf %s" %interval)
            #trades[interval].append(0)
            #print(interval + 0, end='')
        trades[interval] = list()
        wasTrade = False


    if 'TradeAdded' in line:
        trade = eval(line.split('(')[1].split(')')[0].strip())
        if trade['time'] == int(interval):
            wasTrade = True
            power = str(trade['power']/1000)
            if trade['sellerID'] in postedOffers.keys():
                if (solutionID !=0) and (solutionID != trade['solutionID']):
                    trades[interval] = list()
                solutionID = trade['solutionID']
                trades[interval].append(power)
                #print(',' + power, end='')
#print(trades)
for i in trades:
    print(str(i) , end='')
    if not trades[i]:
        print("," + str(0), end='')
    for v in trades[i]:
        print (',' + str(v) , end='')
    print("")
#print (trades)
print("\n")
