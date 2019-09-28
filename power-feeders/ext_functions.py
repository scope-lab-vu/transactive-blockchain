import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import copy
import random 
import os

from functions_auction import build_curves, find_equilibrium_auction, extract_bids, order_bids_descending, order_bids_ascending, find_market_equilibrium, surplus_f, ideal_eq_attack, maer, avg_total_surplus, stats

from functions_read_data import read_data, rolling_statistics, get_avg_data


def write(parameters):
	#print(parameters)
	#parameters[1] = str(int(float(parameters[1])))
	file_name = parameters[0]
	f = open(file_name, 'a')
	f.write( ','.join(parameters[1:]) + '\n' )
	f.close()

	f = open('bids_log.csv', 'a')
	f.write( ','.join(parameters[1:]) + '\n' )
	f.close()

	return '1'




def market_clearing(parameters):
	file_name = parameters[0]
	
	# get the equilibrium and the bids in each time period
	try:
		#pdb.set_trace()
		eq_time_nom, market_eq_nom, bids_nom, curves_nom = find_market_equilibrium(file_name)

	except:
		print('error')
		pdb.set_trace()


	# rewrite the bid file
	try:
		os.remove(file_name)
	except:
		pass

	f = open(file_name, 'w')
	f.write( 'market_id,timestamp,bidder_name,bid_price,bid_quantity,bid_state\n' )
	f.close()

	return str(market_eq_nom['p'][0])
	
