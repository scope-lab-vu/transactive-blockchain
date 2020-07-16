import csv
# import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import copy
import random 
import os

from functions_auction import build_curves, find_equilibrium_auction, extract_bids, order_bids_descending, order_bids_ascending, find_market_equilibrium, surplus_f, ideal_eq_attack, maer, avg_total_surplus, stats

from functions_read_data import read_data, rolling_statistics, get_avg_data

from transax.EthereumClient import EthereumClient
from transax.MatchingContract import MatchingContract
from transax.MatchingSolver import MatchingSolver, Offer
import config as cfg
import time


ethclient = EthereumClient(ip='localhost', port=10000, TXGAS=cfg.TRANSACTION_GAS)

account = ethclient.accounts()[0] # use the first owned address

# get the contract address
with open('contract_address', 'r') as f:
	contract_address = f.readline()

# define the contract
contract = MatchingContract(ethclient, contract_address)

code = '1234321'

txHash = None
type_bid = None



def encode(price, quantity):
	bid_price = int(float(price)*1000)
	bid_quantity = int(abs(float(quantity)*1000))
	return str(bid_price) + code + str(bid_quantity)

def decode(n1):
	parameters = str(n1).split(code)
	bid_price = float(parameters[0])/1000
	bid_quantity = float(parameters[1])/1000
	return bid_price, bid_quantity





# send the bids to the block chain
def post(parameters):
#def post(bidder_name, price, quantity, period, time):
	global txHash
	global type_bid

	bidder_name, price, quantity, period, time = parameters

	# write the bids in logs
	data = [period, time, bidder_name, price, quantity, 'unknown']
	f = open('bids.csv', 'a')
	f.write( ','.join(data) + '\n' )
	f.close()

	f = open('bids_log.csv', 'a')
	f.write( ','.join(data) + '\n' )
	f.close()

	# get list of bidders
	list_bidders = np.load('id_bidders.npy', allow_pickle=True).item()

	# get the current period
	for event in contract.poll_events():
		name = event['name']
		if (name == "StartOffering"):
			nextInterval = params['interval']
			
	bidder_id = list_bidders[bidder_name]
	try:
		start_time = nextInterval
	except:
		pdb.set_trace()
	end_time = start_time+1

	# send the bids
	bid_quantity = float(quantity)
	bid_price = float(price)

	# energy = encode(price, quantity)

	if bid_quantity < 0:
		txHash = contract.postBuyingOffer(account, bidder_id, start_time, end_time, -bid_quantity, bid_price)
		# receipt = wait4receipt(ethclient, txHash, "postBuyingOffer")
		type_bid = "postBuyingOffer"
	else:
		txHash = contract.postSellingOffer(account, bidder_id, start_time, end_time, bid_quantity, bid_price)
		# receipt = wait4receipt(ethclient, txHash, "postSellingOffer")
		type_bid = "postSellingOffer"

	return '1'




def get_solution(parameters):

	receipt = wait4receipt(ethclient, txHash, type_bid)
	
	# get the bids
	bids = dict()
	bids_demand = []
	bids_offer = []

	for event in contract.poll_events():
		params = event['params']
		name = event['name']
		interval = event['startTime']

		if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
			new_offers = True

		q = params['energy']
		p = params['value']
		# p, q = decode(energy)
		bidder = params['prosumer'] 

		bids[bidder] = [p, q]

		if name == "BuyingOfferPosted":
			bids_offer.append( [p, q] )
		else:
			bids_demand.append( [p, q] )


		# transform into an array
		bids_demand = np.array(bids_demand)
		bids_offer = np.array(bids_offer)

		# order the bids
		bids_demand = order_bids_descending(bids_demand)
		bids_offer = order_bids_ascending(bids_offer)

		# find the equilibria
		number_offers = len(bids_offer)
		number_demand = len(bids_demand)

		if number_demand<=0 or number_offers<=0:
			q_eq = 0
			p_eq = 0

		else:
			q_eq, p_eq = find_equilibrium_auction(bids_offer, bids_demand)

	

	# get the equilibrium and the bids in each time period
	file_name = 'bids.csv'
	try:
		eq_time_nom, market_eq_nom, bids_nom, curves_nom = find_market_equilibrium(file_name)
	except:
		print('error')
		pdb.set_trace()

	# rewrite the bid file
	try:
		os.remove(file_name)
	except:
		pass

	# initialize the file for the bids of the next period
	f = open(file_name, 'w')
	f.write( 'market_id,timestamp,bidder_name,bid_price,bid_quantity,bid_state\n' )
	f.close()


	# write the equilibria price
	prices = [str(market_eq_nom['p'][0]), str(p_eq)]
	f = open('eq_price.csv', 'a')
	f.write( ','.join(prices) + '\n' )
	f.close()

	#return str(market_eq_nom['p'][0])
	
	txHash = contract.submitClearingPrice(account, interval, price=p_eq)

	return str(p_eq)
	
