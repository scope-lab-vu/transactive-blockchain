import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import copy
import random 

from functions_auction import build_curves, find_equilibrium_auction, extract_bids, order_bids_descending, order_bids_ascending, find_market_equilibrium, surplus_f, ideal_eq_attack, maer, avg_total_surplus, stats

from functions_read_data import read_data, rolling_statistics, get_avg_data

#from parameters import attack_impact 

time_format = "%Y-%m-%d %H:%M:%S"
time_format_b = "%Y-%m-%d %H:%M:%S.%f"

# name of the model
model = 'R1_1247_3_t6_small'

folder_nom = '../simulations/' + model + '/nominal_1h_1month_b/'

# name of the data files
substation = 'total_power_network_node.csv'

market_bids_nom = 'log_file_nom.csv'

market_eq_nom = 'market_nom.csv'





# Check whether the bids are below the equilibrium price
def count(t, freq):
	bidders_t = bids[t].keys()
	for i in bidders_t:
		p, q = bids[t][i]

		# check if the bidder is a buyer
		if q<0:
			# get the market equilibrium
			p_eq = market_eq_nom['p'][t]

			freq[i].append( p < p_eq )
	return freq


def demand(t, bids_q):
	bidders_t = bids[t].keys()
	for i in bidders_t:
		if i in agents:
			p, q = bids[t][i]
			bids_q[i].append( q )
	return bids_q


# calculate the probability that a bid is below the equilibrium price
def stats_bidders(freq):
	stats = dict()
	for i in freq.keys():
		try:
			stats[i] = sum( freq[i] ) / len( freq[i] )
		except:
			stats[i] = 0
	return stats

# sort the bidders according to their prob of having bids below the equilibrium
def sort_bidders(stats):
	list_agents = []
	list_sorted = sorted(stats.items(), key=lambda kv:kv[1], reverse=True)
	for i in list_sorted:
		list_agents.append( i[0] )
	return list_agents


####################################
def select_agents(rank_agents, exp_impact, delta_q_a_avg):

	rho = []
	for tau in range(periods):


		desired_impact_tau = delta_q_a_avg[tau]
		rank_agents_tau = rank_agents[tau]
		exp_impact_tau = exp_impact[tau]

		impact = 0
		m = 0

		# dictionary with the selection probability of the targets
		rho_tau = dict()

		while m < len( rank_agents_tau ) and impact < desired_impact_tau:
			i = rank_agents_tau[m]

			#pdb.set_trace()

			# check if adding more agents increase the impact
			if exp_impact_tau[i] == 0:
				break

			# calculate the expected impact adding one more buyer
			impact_temp = impact + exp_impact_tau[i]

			# check the selection probability
			if impact_temp > desired_impact_tau:
				rho_tau[i] = (desired_impact_tau - impact) / exp_impact_tau[i]
			else:
				rho_tau[i] = 1

			impact += rho_tau[i] * exp_impact_tau[i]
			m += 1

			# check if we have enough agents
			if impact >= desired_impact_tau:
				break

		# save the selection probability for the current period
		rho.append( rho_tau )

	return rho



def select_targets(rank, exp_impact, goal):
	impact = 0
	m = 0

	while m < len( rank ):
		i = rank[m]

		# check if adding more agents increase the impact
		if exp_impact[i] == 0:
			break

		# calculate the expected impact adding one more buyer
		impact += exp_impact[i]
		m += 1

		# check if we have enough agents
		if impact >= delta_q_a_avg[t]:
			break

	return m, impact




# get the equilibrium and the bids in each time period
eq_time_nom, market_eq_nom, bids_nom, curves_nom = find_market_equilibrium(folder_nom + market_bids_nom)

time, bids = extract_bids(folder_nom + market_bids_nom)

# total samples
T = len(time)

# total number of periods in a day
periods = int(24*60/5)

total_periods = int(T/periods)

n_periods_train = int( total_periods * 0.9)
T_train = n_periods_train * periods




################# parameters of the attack

# get the desired equilibrium quantity
#lambda_ = attack_impact
lambda_ = 0.5
q_op = market_eq_nom['q']
q_a = q_op * (1+lambda_) ** 0.5



# get the average demand in the equilibria for each time period and the attack's goal
q_avg = []
delta_q_a_avg = []
for t in range(periods):
	total_load = 0
	for k in range(n_periods_train):
		total_load += q_op[ k*periods + t ]

	# average load at time t
	q_avg.append( total_load / n_periods_train )

	# desired average load with an attack at time t
	total_load_a = total_load * ((1+lambda_)**.5 - 1)
	delta_q_a_avg.append( total_load_a / n_periods_train )


delta_q_a_avg = np.array(delta_q_a_avg)
q_avg = np.array( q_avg )
q_a_avg = q_avg * (1+lambda_)**0.5

np.save('../desired_q.npy', q_a_avg)


# get the list of buyers
buyers = set()
sellers = set()
for t in range(T):
	bidders_t = bids[t].keys()
	for i in bidders_t:
		p, q = bids[t][i]

		# check if the bidder is a buyer
		if q <= 0:
			if i not in buyers:
				buyers.add(i)
		else:
			if i not in sellers:
				sellers.add(i)

#agents = buyers.union( sellers )
agents = buyers

# construct an empty dictionary for the bid frquency of events
freq_void = dict()
for i in agents:
	freq_void[i] = []


# construct an empty dictionary for the bidder's state
state_void = dict()
for i in agents:
	state_void[i] = False


# construct an empty array to count events
count_void = dict()
for i in agents:
	count_void[i] = 0.0


# construct an empty dictionary for the count registers
count_events_void = []
for t in range(periods):
	count_t = copy.deepcopy( count_void )
	count_events_void.append( count_t )






# calculate the expected impact of an attack on each bidder

# Get the state of the bids: whether an attack would have any impact
state_buyer = []
for t in range(T_train):

	# get the market equilibrium
	p_eq = market_eq_nom['p'][t]

	state_t = copy.deepcopy( state_void )
	
	bidders_t = bids[t].keys()
	for i in bidders_t:
		p, q = bids[t][i]

		# check if the bidder is a buyer
		if q <= 0:
			# find the state of the bid
			state_t[i] =  p < p_eq

	state_buyer.append( state_t )


# calculate the expected impact of an attack in each time period
prob_submit_bid = copy.deepcopy( count_events_void ) 
exp_impact = copy.deepcopy( count_events_void ) 
for tau in range(periods):

	# number of times that we see a bid at a particular period
	count_events = copy.deepcopy( count_void  )

	# impact that we would observe if we delay a valid bid
	aggregate_impact = copy.deepcopy( count_void  )


	for k in range(n_periods_train):
		t = tau + periods*k

		bidders_t = bids[t].keys()
		for i in bidders_t:
			if i in agents:
				p, q = bids[t][i]
				x_t = state_buyer[t][i]

				aggregate_impact[i] += x_t * q * -1
				count_events[i] += 1.0

	# calculate the prob of sending a bid
	for i in agents:
		prob_submit_bid[tau][i] = count_events[i] / n_periods_train

	# calculate the average impact
	for i in agents:
		if count_events[i]>0:
			exp_impact[tau][i] = aggregate_impact[i] / count_events[i] * prob_submit_bid[tau][i]




# get list of bidders in each gateway
id_bidders = np.load('../id_bidders.npy').item()

# number of gateways 
n_gw = 3

bidders_gw = {}
for i in range(n_gw):
	bidders_gw[i] = set()

for bidder, id in id_bidders.items():
	gw = id % n_gw
	bidders_gw[gw].add( bidder )



# get the expected impact for the bids in each gw

exp_impact_gw = {}
for i in range(n_gw):
	set_bidders = bidders_gw[i]

	# create an empty data structure to store the expected impact
	exp_impact_i = []
	for tau in range(periods):
		exp_impact_i.append( {key: 0.0 for key in set_bidders} )

	exp_impact_gw[i] = copy.deepcopy( exp_impact_i ) 

# fill the data structure with the expected impact
for tau in range(periods):
	for bidder in exp_impact[tau].keys():
		id = id_bidders[bidder]
		gw = id % n_gw
		if bidder in bidders_gw[gw]:
			exp_impact_gw[gw][tau][bidder] = exp_impact[tau][bidder]




def equilibria_delay_attacks(rho):
	p_eq_att = []
	q_eq_att = []
	bids_att = []
	for t in range(T):
		tau = t % periods
		rho_tau = rho[tau]

		victims = rho_tau.keys()

		# get the bids for this period
		bids_a_t = copy.deepcopy( bids[t] )

		for i in bids_a_t.keys():
			if i in victims:
				rand = random.random()
				if rand <= rho_tau[i]:
					# change the bids of the victims
					bids_a_t[i][0] = 0.63

		bids_att.append( bids_a_t )

		# calculate the equilibrium with the new bids
		# select bids of offer and demand
		offer = []
		asks = []
		for i in bids_a_t.keys():
			p, q = bids_a_t[i]
			if q > 0:
				offer.append( [p, q] )
			else:
				asks.append( [p, -q] )

		asks = order_bids_descending( np.array( asks ) )
		offer = order_bids_ascending( np.array( offer ) )

		number_offers = len(offer)
		number_demand = len(asks)

		if number_demand<=0 or number_offers<=0:
			q_eq = 0
			p_eq = 0
		else:
			# order the bids according to the price
			q_eq, p_eq = find_equilibrium_auction(offer, asks)

		q_eq_att.append( q_eq )
		p_eq_att.append( p_eq )

	return p_eq_att, q_eq_att, bids_att


def equilibria_delay_attacks_rand(rate, target_gw):
	p_eq_att = []
	q_eq_att = []
	bids_att = []
	for t in range(T):
		tau = t % periods
		rate_tau = rate[tau]

		# get the bids for this period
		bids_a_t = copy.deepcopy( bids[t] )

		for i in bids_a_t.keys():
			if i in buyers and i in bidders_gw[ target_gw ]:
				rand = random.random()
				if rand <= rate_tau:
					# change the bids of the victims
					bids_a_t[i][0] = 0.63

		bids_att.append( bids_a_t )

		# calculate the equilibrium with the new bids
		# select bids of offer and demand
		offer = []
		asks = []
		for i in bids_a_t.keys():
			p, q = bids_a_t[i]
			if q > 0:
				offer.append( [p, q] )
			else:
				asks.append( [p, -q] )

		asks = order_bids_descending( np.array( asks ) )
		offer = order_bids_ascending( np.array( offer ) )

		number_offers = len(offer)
		number_demand = len(asks)

		if number_demand<=0 or number_offers<=0:
			q_eq = 0
			p_eq = 0
		else:
			# order the bids according to the price
			q_eq, p_eq = find_equilibrium_auction(offer, asks)

		q_eq_att.append( q_eq )
		p_eq_att.append( p_eq )

	return p_eq_att, q_eq_att, bids_att






# find the impact's attack in each gateway
print('Case II')
rho_gw = []
error = []
for i in range(n_gw):

	rank_agents = []
	for tau in range(periods):
		stats_t = exp_impact_gw[i][tau]
		rank_agents_tau = sort_bidders( stats_t )
		rank_agents.append( rank_agents_tau )

	
	rho_i = select_agents(rank_agents, exp_impact_gw[i], delta_q_a_avg)
	rho_gw.append( rho_i )


	p_a_real, q_a_real, bids_att = equilibria_delay_attacks(rho_i)
	error_i = np.mean(q_a[T_train:T] - q_a_real[T_train:T])
	error.append( error_i )

	print('Error in the attack`s goal gw='+str(i))
	print(error_i)

target_gw = np.argmin( error )


# save the bids that we need to delay
np.save('../targets.npy', rho_gw[target_gw] )
np.save('../target_gw.npy', target_gw )


#exit

print('\nCase III')
# define the rate of delay for the random attack
error = []
rate_gw = []
for i in range(n_gw):
	exp_impact_i = exp_impact_gw[gw]

	rate_delay = []
	for tau in range(periods):
		impact = 0
		bidders_tau = exp_impact_i[tau].keys()
		num_bidders = len(bidders_tau)
		num_bidders_gw = len(buyers)/3.0
		for bidder in bidders_tau:
			impact += exp_impact_i[tau][bidder]
		avg_impact = impact / num_bidders
		exp_impact = num_bidders_gw * avg_impact
		rate = min(1, delta_q_a_avg[tau] / exp_impact)
		rate_delay.append( rate )
	rate_gw.append( rate_delay )

	# evaluate impact
	p_a_real, q_a_real, bids_att = equilibria_delay_attacks_rand( rate_delay, i )
	error_i = np.mean(q_a[T_train:T] - q_a_real[T_train:T])
	error.append( error_i )

	print('Error in the attack`s goal gw='+str(i))
	print(error_i)

target_gw_rand = np.argmin( error )
	

np.save('../rate_delay.npy', rate_gw[target_gw_rand])
np.save('../target_gw_rand.npy', target_gw_rand )



exit

rho = rho_gw[target_gw]

# get the number of victims
n = []
for tau in range(periods):
	n.append( len(rho[tau]) )


# get the expected impac tof the attack
impact = []
for tau in range(periods):
	I = 0
	for i in rho[tau].keys():
		I += rho[tau][i] * exp_impact[tau][i]
	impact.append( I )

	
plt.figure(1)
plt.clf()
plt.plot(n, label='case 2')
plt.plot(num_victims, '--', label='case 3')
plt.title('Number of victims')
plt.legend()
plt.show()


plt.figure(2)
plt.clf()
#plt.plot(eq_time_nom[0:periods], delta_q_a_avg, label='')
#plt.plot(q_avg, label='q opt')
plt.plot(delta_q_a_avg, label='delta q')
plt.plot(impact, '--', label='impact')
plt.title('Impact')
plt.legend()
plt.show()



p_a_real, q_a_real, bids_att = equilibria_delay_attacks(rho)

plt.figure(3)
plt.clf()
plt.plot(q_op, label='q_op')
plt.plot(q_a, label='q_a ideal')
plt.plot(q_a_real, label='q_a real')
plt.legend()
plt.show()

exit

# approx cost function = 
blocks = 25
max_capacity = 1500
max_price = .63


def cost(x):
	beta = max_price / (2 * max_capacity)
	return beta * np.array(x)**2 

def dot_cost(x):
	beta = max_price / (2 * max_capacity)
	return 2 * beta * x

def f_profit_seller(load):
	load_b = np.array(load)
	price = dot_cost( load_b )
	profit = price * load_b - cost(load_b)
	#pdb.set_trace()
	return profit


load = q_op
price = dot_cost(load)
income = load * price
expenses = cost(load)


profit_seller_a = f_profit_seller(q_a)
profit_seller = f_profit_seller(q_op)
impact_ratio = profit_seller_a / profit_seller


#aa = f_profit_seller(q_a) - cost(q_a)
#exit

'''
profit_seller_a = cost(q_a)
profit_seller = cost(q_op)
impact_ratio = profit_seller_a / profit_seller
'''


plt.figure(3)
plt.clf()
plt.plot(impact_ratio[1:], label='impact ratio')
plt.legend()
plt.show()




plt.figure(4)
plt.clf()
plt.plot(eq_time_nom,  q_a / q_op, label='q ratio')
#plt.plot(eq_time_nom,  q_op, label='Nominal')
#plt.plot(eq_time_nom,  q_a, label='Attack (ideal)')

plt.title('Demand')
plt.show()





price = dot_cost(q_op)
p_op =  market_eq_nom['p']

plt.figure(5)
plt.clf()
plt.plot(p_op, label='price market')
plt.plot(price, label='price function')
plt.legend()
plt.show()



t = 10

# get the bids for this period
bids_t = bids[t]

# calculate the equilibrium with the new bids
# select bids of offer and demand
offer = []
asks = []
for i in bids_t.keys():
	p, q = bids_t[i]
	if q > 0:
		offer.append( [p, q] )
	else:
		asks.append( [p, -q] )

asks = order_bids_descending( np.array( asks ) )
offer = order_bids_ascending( np.array( offer ) )

number_offers = len(offer)
number_demand = len(asks)

curves = dict()
curves['demand'] =  build_curves(asks, -1)
curves['offer'] = build_curves(offer, 1)

if number_demand<=0 or number_offers<=0:
	q = 0
	p = 0
else:
	# order the bids according to the price
	q_eq, p_eq = find_equilibrium_auction(offer, asks)

x = np.linspace(0, max_capacity, blocks)
price_x = dot_cost(x)

plt.figure(11)
plt.clf()
plt.plot(curves['demand']['q'], curves['demand']['p'], '--',label='Demand curve')
plt.plot(curves['offer']['q'], curves['offer']['p'], 'r', label='Supply curve')
plt.plot(x, price_x, '-r')
plt.plot([q_eq], [p_eq], marker='D', markersize=5.5, label='Normal equilibria')
#plt.plot([q_eq_a], [p_eq_a], marker='o', markersize=6, label = 'Equilibria with an attack')
plt.title('Market Equilibrium with an Attack')
plt.xlabel('Quantity (kWh)')
plt.ylabel('Price')
plt.legend()
#scale = 0.2
#plt.xlim((q_eq*(1-scale), q_eq*(1+scale)))
plt.show()




# check equations
g = market_eq_nom['q']
p = market_eq_nom['p']
#p = dot_cost(g)

a  = p * g - cost( g )
b = cost( g ) 

plt.figure(6)
plt.clf()
plt.plot(a, label='a')
plt.plot(b, label='b')
plt.legend()
plt.show()



exit


def equilibria_delay_attacks(rho):
	p_eq_att = []
	q_eq_att = []
	bids_att = []
	for t in range(T):
		tau = t % periods
		rho_tau = rho[tau]

		victims = rho_tau.keys()

		# get the bids for this period
		bids_a_t = copy.deepcopy( bids[t] )

		for i in bids_a_t.keys():
			if i in victims:
				rand = random.random()
				if rand <= rho_tau[i]:
					# change the bids of the victims
					bids_a_t[i][0] = 0.63

					'''
					if tau == 150:
						print( bids[tau][i][0] )
						print( bids_tau[i][0] )
						print()
					'''

		bids_att.append( bids_a_t )
		#if tau == 150:
		#	pdb.set_trace()


		# calculate the equilibrium with the new bids
		# select bids of offer and demand
		offer = []
		asks = []
		for i in bids_a_t.keys():
			p, q = bids_a_t[i]
			if q > 0:
				offer.append( [p, q] )
			else:
				asks.append( [p, -q] )

		asks = order_bids_descending( np.array( asks ) )
		offer = order_bids_ascending( np.array( offer ) )

		number_offers = len(offer)
		number_demand = len(asks)

		if number_demand<=0 or number_offers<=0:
			q_eq = 0
			p_eq = 0
		else:
			# order the bids according to the price
			q_eq, p_eq = find_equilibrium_auction(offer, asks)

		q_eq_att.append( q_eq )
		p_eq_att.append( p_eq )

	return p_eq_att, q_eq_att, bids_att



p_a_real, q_a_real, bids_att = equilibria_delay_attacks(rho)
error = np.mean(q_a[T_train:T] - q_a_real[T_train:T])

print('Error in the attack`s goal')
print(error)


plt.figure(5)
plt.clf()
plt.plot(q_op, label='Nominal demand')
plt.plot(q_a, '-.', label='Demand with an impact (ideal)')
plt.plot(q_a_real, '--', label='Demand with an impact (real)')
plt.title('Real Impact of the Attack')
plt.legend()
plt.show()



# example of the attacks
k = 0
def plot_eq(k):
	t = T_train + k

	print(time[t])


	# get the current period
	tau = t%periods

	# get the bids for this period
	bids_t = bids[t]

	# calculate the bids of victims
	bids_t_a = bids_att[t]


	# calculate the equilibrium with the new bids
	# select bids of offer and demand
	offer = []
	asks = []
	asks_a = []
	for i in bids_t.keys():
		p, q = bids_t[i]
		p_a, q_a = bids_t_a[i]
		if q > 0:
			offer.append( [p, q] )
		else:
			asks.append( [p, -q] )
			asks_a.append( [p_a, -q_a] )

	asks = order_bids_descending( np.array( asks ) )
	asks_a = order_bids_descending( np.array( asks_a ) )
	offer = order_bids_ascending( np.array( offer ) )

	number_offers = len(offer)
	number_demand = len(asks)
	number_demand_a = len(asks_a)

	curves = dict()
	curves['demand'] =  build_curves(asks, -1)
	curves['demand_a'] =  build_curves(asks_a, -1)
	curves['offer'] = build_curves(offer, 1)

	if number_demand<=0 or number_offers<=0:
		q = 0
		p = 0
	else:
		# order the bids according to the price
		q_eq, p_eq = find_equilibrium_auction(offer, asks)
		q_eq_a, p_eq_a = find_equilibrium_auction(offer, asks_a)


	plt.figure(10)
	plt.clf()
	plt.plot(curves['demand']['q'], curves['demand']['p'], '--',label='Demand curve')
	plt.plot(curves['demand_a']['q'], curves['demand_a']['p'], ':', label='Demand curve with an attack')
	plt.plot(curves['offer']['q'], curves['offer']['p'], 'r', label='Supply curve')
	plt.plot([q_eq], [p_eq], marker='D', markersize=5.5, label='Normal equilibria')
	plt.plot([q_eq_a], [p_eq_a], marker='o', markersize=6, label = 'Equilibria with an attack')
	plt.title('Market Equilibrium with an Attack')
	plt.xlabel('Quantity (kWh)')
	plt.ylabel('Price')
	plt.legend()
	scale = 0.2
	plt.xlim((q_eq*(1-scale), q_eq*(1+scale)))
	plt.show()










def plot_eq_b(k):
	t = T_train + k

	print(time[t])

	# get the current period
	tau = t%periods

	# get the victims for this period
	victims = set_victims[tau]

	# get the bids for this period
	bids_t = bids[t]

	# calculate the bids of victims
	bids_t_a = copy.deepcopy( bids_t )

	# select victims
	p_eq = market_eq_nom['p'][t]

	bidders_t = bids[t].keys()
	feasible_victims = set()
	for i in bidders_t:
		p, q = bids[t][i]
		if q > 0 and p < p_eq and p > 0.26 :
			feasible_victims.add(i)
	n = len( feasible_victims )
	victims = random.sample( feasible_victims, int(1 * n))

	# change the bids of the victims
	
	for i in victims:
		try:
			bids_t_a[i][0] = 0.63
		except:
			pass
	

	# calculate the equilibrium with the new bids
	# select bids of offer and demand
	offer = []
	asks = []
	offer_a = []
	for i in bids_t.keys():
		p, q = bids_t[i]
		p_a, q_a = bids_t_a[i]
		if q > 0:
			offer.append( [p, q] )
			offer_a.append( [p_a, q_a] )
		else:
			asks.append( [p, -q] )


	asks = order_bids_descending( np.array( asks ) )
	offer_a = order_bids_ascending( np.array( offer_a ) )
	offer = order_bids_ascending( np.array( offer ) )

	number_offers = len(offer)
	number_demand = len(asks)
	number_offers_a = len(offer_a)

	curves = dict()
	curves['demand'] =  build_curves(asks, -1)
	curves['offer_a'] =  build_curves(offer_a, -1)
	curves['offer'] = build_curves(offer, 1)

	if number_demand<=0 or number_offers<=0:
		q = 0
		p = 0
	else:
		# order the bids according to the price
		q_eq, p_eq = find_equilibrium_auction(offer, asks)
		q_eq_a, p_eq_a = find_equilibrium_auction(offer_a, asks)



	plt.figure(11)
	plt.clf()
	plt.plot(curves['demand']['q'], curves['demand']['p'], '--',label='Demand curve')
	plt.plot(curves['offer_a']['q'], curves['offer_a']['p'], ':', label='Supply curve with an attack')
	plt.plot(curves['offer']['q'], curves['offer']['p'], 'r', label='Supply curve')
	plt.plot([q_eq], [p_eq], marker='D', markersize=5.5, label='Normal equilibria')
	plt.plot([q_eq_a], [p_eq_a], marker='o', markersize=6, label = 'Equilibria with an attack')
	plt.title('Market Equilibrium with an Attack')
	plt.xlabel('Quantity (kWh)')
	plt.ylabel('Price')
	plt.legend()
	scale = 0.2
	plt.xlim((q_eq*(1-scale), q_eq*(1+scale)))
	plt.show()


#exit
'''
plot_eq(150)
exit
pdb.set_trace()


plot_eq(1005)
plt.savefig('eq_att_bids_demand.pgf', bbox_inches='tight')

plot_eq_b(1005)
plt.savefig('eq_att_bids_offer.pgf', bbox_inches='tight')
'''








######################################################
# define the events to implement the attack

attack_signal = '''
object: attack_signal
option: virtual_object, save
delay: 0
attribute: val
+0; 0
+11h; 1
+4h; 0
'''

counter_obj = '''
object: counter_period
option: virtual_object, save, repeat
delay: 0
attribute: val
+5m; sum(counter_period/val, 1)
'''

flag_periods = '''
object: delay_k**
option: virtual_object, repeat, save
delay: 0
attribute: state
+5m; select(attack_signal/val, equal(val**, counter_period/val), 0)
'''

flags = ''
for k in range(periods):
	flags += flag_periods.replace('val**', str(max(0,k-1))).replace('k**', str(k))


# find list of periods to attack each bidder
def find_attack_periods(list_victims):
	attack_periods = copy.deepcopy( freq_void )
	for i in agents:
		for tau in range(periods):
			if i in list_victims[tau]:
				attack_periods[i].append( tau )

	return attack_periods


selector_obj = '''
object: select_name**
option: virtual_object, repeat
delay: 0
attribute: val
+5m; or( list_periods** )
'''


list_victims = []
for tau in range(periods):
	list_victims.append( rho[tau].keys() )



attack_periods = find_attack_periods(list_victims)

selectors = ''
for i in agents:
	if len(attack_periods[i]) > 0:
		periods_att_i = ', '.join([ 'delay_'+str(j)+'/state' for j in attack_periods[i] ])
		selectors += selector_obj.replace('name**', i).replace('list_periods**', periods_att_i)







delay_obj = '''
object: att_name**
option: repeat, random
delay: 60
attribute: price, quantity
+5m; select(select_name**/val, 0, att_name**/price), select(select_name**/val, 0, att_name**/quantity)
'''

bidders_att = ''
for i in agents:
	if len(attack_periods[i]) > 0:
		bidders_att += delay_obj.replace('name**', i).replace('list_periods**', periods_att_i)




# recorder for bids
recorder_obj = '''
object: recorder
option: repeat, random, save
delay: 240
attribute: val
+5m; att_bidder_control_54/quantity

'''





events_file = open('events_delay_att', 'w')

events_file.write(attack_signal)
events_file.write(counter_obj)
events_file.write(flags)
events_file.write(selectors)
events_file.write(bidders_att)

events_file.write(recorder_obj)

events_file.close()



#np.savez('impact.npz', arr_0=eff_loss, arr_1=gain_seller, arr_2=loss_buyer)





