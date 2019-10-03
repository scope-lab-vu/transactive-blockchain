from MatchingSolver import MatchingSolver
from MatchingSolver import Offer
from Microgrid import Microgrid
import itertools
import matplotlib.pyplot as plt
import numpy as np

def partition(collection):
    if len(collection) == 1:
        yield [ collection ]
        return

    first = collection[0]
    for smaller in partition(collection[1:]):
        # insert `first` in each of the subpartition's subsets
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[ first ] + subset]  + smaller[n+1:]
        # put `first` in its own subset 
        yield [ [ first ] ] + smaller

network = {   #defines placement of prosumers on feeders
0: 0,
1: 0,
2: 1,
3: 1,
4: 2,
5: 2,
6: 3,
7: 3,
8: 4,
9: 4
}
C_ext=[3.0,4.0,3.0,4.0,3.0] #constraints on each feeder
C_int=[3.0,4.0,3.0,4.0,3.0]

feeders=[0, 1, 2, 3, 4] #list of feeders in network
microgrid = Microgrid(interval_length=1.0, C_ext=C_ext, C_int=C_int, feeders=feeders, prosumer_feeder=network)
solver = MatchingSolver(microgrid)
buying_offers = [
Offer(0, 0, 1, 10, 45),
Offer(1, 2, 1, 10, 46),
Offer(2, 4, 1, 10, 45),
Offer(3, 6, 1, 10, 41),
Offer(4, 8, 1, 10, 43),
]
selling_offers = [
Offer(5, 1, 1, 10, 20),
Offer(6, 3, 1, 10, 20),
Offer(7, 5, 1, 10, 20),
Offer(8, 7, 1, 10, 20),
Offer(9, 9, 1, 10, 20),
]

(trades, objective) = solver.solve(buying_offers=buying_offers, selling_offers=selling_offers)
optimum_energy = objective

#feeders gives list of feeders
numf = len(feeders)
allgroups = list(partition(feeders))
allgroups = allgroups[:-1]

mincost = [10000]*(len(feeders)-1)
mincost.append(0.0)
bestgroup = [[0]]*(len(feeders)-1)

print (bestgroup)

for p in allgroups:
	network1 = network.copy()
	# prival = 0 #privacy value
	for group in p:
		# prival = prival + len(group) -1
		cint = []
		for i in group:
			cint.append(C_int[i])
		minf = group[cint.index(min(cint))]
		# print (group,minf)
		for key,value in network1.items():
			if (value in group):
				network1[key] = minf
	# print (group,network1)
	microgrid = Microgrid(interval_length=1.0, C_ext=C_ext, C_int=C_int, feeders=feeders, prosumer_feeder=network1)
	solver = MatchingSolver(microgrid)
	(trades, objective) = solver.solve(buying_offers=buying_offers, selling_offers=selling_offers)
	cost = optimum_energy - objective #- 5*(len(feeders) - len(p))
	print (p,cost)
	if (cost<mincost[len(p)-1]):
		mincost[len(p)-1] = cost
		bestgroup[len(p)-1] = p

print ("Best groups are:")

for i in range(len(feeders)-1):
	print ("Number of distinguishable groups: ",i+1," ","Group: ",bestgroup[i])

x = np.linspace(1,len(feeders),len(feeders))
plt.plot(x,np.array(mincost))
plt.xlabel("Number of distinguishable groups")
plt.ylabel("Energy to be purchased from DSO")
plt.xticks(np.arange(min(x), max(x)+1, 1.0))
plt.show()
# print (x)
