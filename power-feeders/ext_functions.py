import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import copy
import random 
import os
import sys

from functions_auction import build_curves, find_equilibrium_auction, extract_bids, order_bids_descending, order_bids_ascending, find_market_equilibrium, surplus_f, ideal_eq_attack, maer, avg_total_surplus, stats

from functions_read_data import read_data, rolling_statistics, get_avg_data

from parameters import attack_impact 


periods = int(24*60/5)
gamma = np.ones(periods)*0.2


def write_att(parameters):
	return write(parameters, True)

def write_nom(parameters):
	return write(parameters, False)

def write(parameters, attack_signal):
	#print(parameters)
	#parameters[1] = str(int(float(parameters[1])))
	file_name = parameters[0]


	counter = parameters[1]
	#if counter == '187.0' or counter == '188.0':
	#	print(counter)
	#	pdb.set_trace()



	t = int(float(parameters[1]))
	timestamp = parameters[2]
	bidder = parameters[3]
	p = float(parameters[4])
	q = float(parameters[5])
	state = parameters[6]

	data = [str(t), timestamp, bidder, str(p), str(q), state]


	try:
		# save the bids without an attack
		f = open('bids_log_nom.csv', 'a')
		f.write( ','.join(data) + '\n' )
		f.close()


		# total number of periods in a day


		#pdb.set_trace()


		# load the delay probability 
		rho = np.load('targets_rand.npy', allow_pickle=True)#.item()

		tau = t % periods

		rho_tau = rho[tau]
		victims = rho_tau.keys()

		# decide whether to delay a bid (equivalent to change the price)
		t0 = int(13*60/5)
		tf = int(17*60/5)
		enable_attack = False
		#if tau >= t0 and tau < tf and attack_signal:
		if attack_signal:
			enable_attack = True

		if enable_attack:
			if bidder in victims:
				rand = random.random()
				if rand <= rho_tau[bidder]:
					# change the bids of the victims
					p = 0.63


		data = [str(t), timestamp, bidder, str(p), str(q), state]

		# save the bids in a temporal file
		f = open(file_name, 'a')
		f.write( ','.join(data) + '\n' )
		f.close()

		# save the bids in a log
		f = open('bids_log.csv', 'a')
		f.write( ','.join(data) + '\n' )
		f.close()

	except Exception as err:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(err)
		pdb.set_trace()



	return '1'








def market_clearing(parameters):
	file_name = parameters[0]
	counter = parameters[1]

	# get the equilibrium and the bids in each time period
	try:
		#pdb.set_trace()
		eq_time_nom, market_eq_nom, bids_nom, curves_nom = find_market_equilibrium(file_name)

	except:
		print('error')
		pdb.set_trace()

	#print(counter)

	#if counter == '187.0' or counter == '186.0' or counter == '188.0':
	#	print(counter)
	#	pdb.set_trace()


	# rewrite the bid file
	try:
		os.remove(file_name)
	except:
		pass

	f = open(file_name, 'w')
	f.write( 'market_id,timestamp,bidder_name,bid_price,bid_quantity,bid_state\n' )
	f.close()

	return str(market_eq_nom['p'][0])





def market_clearing_ideal_att(parameters):
	file_name = parameters[0]
	counter = parameters[1]
	timestamp = parameters[2]

	# get the equilibrium and the bids in each time period
	try:
		#pdb.set_trace()
		eq_time_nom, market_eq_nom, bids_nom, curves_nom = find_market_equilibrium(file_name)
		time, bids = extract_bids(file_name)
	except:
		print('error')
		pdb.set_trace()

	try:

		# find the market equilibria
		p_eq = market_eq_nom['p'][0]
		q_eq = market_eq_nom['q'][0]

		# desired impact 
		q_a = q_eq * (1 + attack_impact)**0.5
		delta_q_a = q_a - q_eq

		bids_t = bids[0]

		# max possible impact
		max_impact = 0
		set_feasible_targets = set()
		for x in bids_t.keys():
			p, q = bids_t[x]
			if p <= p_eq and q < 0:
				max_impact += -1 * q
				set_feasible_targets.add( x )

		# select the victims
		rho = dict()
		exp_impact = 0
		for x in set_feasible_targets:
			p, q = bids_t[x]
			if q+exp_impact < delta_q_a:
				rho[x] = 1
				exp_impact += -1 * q
			else:
				rho[x] = (delta_q_a - exp_impact) / (-1 * q)
				exp_impact += rho[x] * -1 * q


		# implement the attack
		bids_a = copy.deepcopy(bids_t)
		for x in rho.keys():
			rand = random.random()
			if rand <= rho[x]:
				# change the bids of the victims
				bids_a[x][0] = 0.63

		# find the new equilibria
		offer = []
		asks = []
		for i in bids_a.keys():
			p, q = bids_a[i]
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
			q_eq_a, p_eq_a = find_equilibrium_auction(offer, asks)


		
		# save the bids in a log
		f = open('bids_log_att.csv', 'a')
		for bidder in bids_a.keys():
			p, q = bids_a[bidder]
			data = [counter, timestamp, bidder, str(p), str(q), 'unknown']
			f.write( ','.join(data) + '\n' )
		f.close()


	except Exception as err:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(err)
		pdb.set_trace()


	#if counter == '187.0':
	#	print(counter)
	#	pdb.set_trace()


	# rewrite the bid file
	try:
		os.remove(file_name)
	except:
		pass

	f = open(file_name, 'w')
	f.write( 'market_id,timestamp,bidder_name,bid_price,bid_quantity,bid_state\n' )
	f.close()

	return str(p_eq_a)










def write_dyn(parameters):
	global gamma
	global periods
	file_name = parameters[0]

	counter = parameters[1]

	t = int(float(parameters[1]))
	timestamp = parameters[2]
	bidder = parameters[3]
	p = float(parameters[4])
	q = float(parameters[5])
	state = parameters[6]

	data = [str(t), timestamp, bidder, str(p), str(q), state]


	tau = int(float(counter)) % periods

	try:
		# save the bids without an attack
		f = open('bids_log_nom.csv', 'a')
		f.write( ','.join(data) + '\n' )
		f.close()


		# total number of periods in a day
		periods = int(24*60/5)


		t0 = int(9*60/5)
		tf = int(18*60/5)
		if tau >= t0 and tau < tf:

			rand = random.random()
			if rand <= gamma[tau]:
				# change the bids of the victims
				p = 0.63


		data = [str(t), timestamp, bidder, str(p), str(q), state]

		# save the bids in a temporal file
		f = open(file_name, 'a')
		f.write( ','.join(data) + '\n' )
		f.close()

		# save the bids in a log
		f = open('bids_log.csv', 'a')
		f.write( ','.join(data) + '\n' )
		f.close()

	except Exception as err:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(err)
		pdb.set_trace()

	return '1'









def market_clearing_dyn_att(parameters):
	global gamma
	file_name = parameters[0]
	counter = parameters[1]
	timestamp = parameters[2]

	periods = int(24*60/5)
	tau = int(float(counter)) % periods

	# get the equilibrium and the bids in each time period
	try:
		#pdb.set_trace()
		eq_time_nom, market_eq_nom, bids_nom, curves_nom = find_market_equilibrium(file_name)
		time, bids = extract_bids(file_name)

		# load desired impact
		q_a = np.load('desired_q.npy', allow_pickle=True)#.item()

	except:
		print('error')
		pdb.set_trace()



	try:

		# find the market equilibria
		p_eq = market_eq_nom['p'][0]
		q_eq = market_eq_nom['q'][0]


		# update the delay
		error = q_a[tau] - q_eq

		k_i = 0
		k_p = 0.1 * 0.01 * 0.1

		#gamma[tau] += min(max(k_p * error, 0), 1)

		t0 = int(9*60/5)
		tf = int(18*60/5)
		if tau >= t0 and tau < tf:

			if error > 0:
				gamma[tau] = min(1.0, gamma[tau] + 0.02) 
			elif error < 0:
				gamma[tau] = max(0.0, gamma[tau] - 0.02) 

		


		# save the bids in a log
		f = open('gamma.csv', 'a')
		data = [counter, timestamp, str(gamma)]
		f.write( ','.join(data) + '\n' )
		f.close()


	except Exception as err:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(err)
		pdb.set_trace()







	# rewrite the bid file
	try:
		os.remove(file_name)
	except:
		pass

	f = open(file_name, 'w')
	f.write( 'market_id,timestamp,bidder_name,bid_price,bid_quantity,bid_state\n' )
	f.close()

	return str(p_eq)


	
