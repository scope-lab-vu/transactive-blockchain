from transax.EthereumClient import EthereumClient
from transax.MatchingContract import MatchingContract
from transax.MatchingSolver import MatchingSolver, Offer
import config as cfg
import time
import numpy as np
import pdb
import random

import csv
import os
import sys 

from functions_auction import build_curves, find_equilibrium_auction, extract_bids, order_bids_descending, order_bids_ascending, find_market_equilibrium, surplus_f, ideal_eq_attack, maer, avg_total_surplus, stats
from functions_read_data import read_data, rolling_statistics, get_avg_data

gateways = None
# ethclient = None
# ethclient1 = None
# ethclient2 = None
gw_assignment = {}
account = None
contract = None
contract1 = None
contract2 = None
poll1 = None
target_gw = None
targets = {}
rate_delay = None

txHash = None
type_bid = None
last_bid = []

nextInterval = 1
periods = int(24*60/5)

def wait4receipt(ethclient,txHash,name,getReceipt=True):

	if not getReceipt:
		receipt = {}
		receipt['gasUsed'] = -1
		receipt['cumulativeGasUsed'] = -1
		print("Did not wait for receipt")
		return receipt

	if txHash.startswith("0x"): 

		receipt = ethclient.command("eth_getTransactionReceipt", params=[txHash])
		i = 0    
		k = 360
		while (receipt is None or "ERROR" in receipt) and i<=k:
			
			print("Waiting for tx {} to be mined... (block number: {})".format(txHash, ethclient.command("eth_blockNumber", params=[])))
			time.sleep(1) 
			i+=1

			receipt = ethclient.command("eth_getTransactionReceipt", params=[txHash])

		if i >= k:
			return None

		if receipt['gasUsed'] == cfg.TRANSACTION_GAS:
			print("Transaction may have failed. gasUsed = gasLimit")

		print("%s gasUsed: %s" %(name,receipt['gasUsed']))
		print("%s cumulativeGasUsed: %s" %(name,receipt['cumulativeGasUsed']))

		return receipt


def deploy_contract(BYTECODE, TXGAS):
	print("Deploying contract...")
	# use command function because we need to get the contract address later
	txHash = ethclient.command("eth_sendTransaction", params=[{'data': BYTECODE, 'from': account, 'gas': TXGAS}])
	print("Transaction hash: " + txHash)

	receipt = wait4receipt(ethclient, txHash, "deployContract")

	contract_address = receipt['contractAddress']

	return contract_address

def initialize(input_):
	global gateways
	global contract
	global contract1
	global contract2
	global ethclient
	global ethclient1
	global ethclient2
	global gw_assignment
	global account
	global poll1
	global nextInterval
	global target_gw
	global rate_delay

	try: 

		print('***initializing blockchain****')

		ethclient = EthereumClient(ip='localhost', port=10000, TXGAS=cfg.TRANSACTION_GAS)
		ethclient1 = EthereumClient(ip='localhost', port=10001, TXGAS=cfg.TRANSACTION_GAS)
		ethclient2 = EthereumClient(ip='localhost', port=10002, TXGAS=cfg.TRANSACTION_GAS)
		#print(ethclient)
		account = ethclient.accounts()[0] # use the first owned address


		HOME = os.path.expanduser('~')
		contractBYTECODE = '%s/projects/transactive-blockchain/transax/smartcontract/output/Matching.bin' %(HOME)
		with open(contractBYTECODE) as f:
			BYTECODE = "0x"+f.read()
			contract_address = deploy_contract(BYTECODE, cfg.TRANSACTION_GAS)
			contract = MatchingContract(ethclient, contract_address)
			contract1 = MatchingContract(ethclient1, contract_address)
			contract2 = MatchingContract(ethclient2, contract_address)

		txHash = contract.setup(account, cfg.MICROGRID.C_ext, cfg.MICROGRID.C_int, cfg.START_INTERVAL)
		receipt = wait4receipt(ethclient, txHash, "setup")
		#print("Contract address: " + contract_address)

		poll1 = contract.poll_events()
		for event in poll1:
			params = event['params']
			name = event['name']
			#print("{}({}).".format(name, params))

			if (name == "StartOffering"):
				nextInterval = params['interval']
				#print ("next interval: %s" %nextInterval)



		#################################################################
		# load the list of bidders
		file_bidders = './bidders'
		list_bidders = {}
		with open(file_bidders, 'r') as f_bidders:
			prosumer_id = 101
			for x in f_bidders:
				list_bidders[x.strip()]=prosumer_id
				prosumer_id = prosumer_id + 1

		# save the dictionary
		np.save('id_bidders.npy', list_bidders)


		# read targets
		# rate_delay = np.load('rate_delay.npy', allow_pickle=True)
		# target_gw = np.load('target_gw.npy', allow_pickle=True)



		# Assign prosumers to gateways
		for ix, bidder in enumerate(list_bidders):
			prosumer_id = list_bidders[bidder]

			if ix%3==0:
				gw_assignment[prosumer_id] = 0
			elif ix%3==1:
				gw_assignment[prosumer_id] = 1
			else:
				gw_assignment[prosumer_id] = 2

			txHash = contract.registerProsumer(account, prosumer_id, cfg.PROSUMER_FEEDER[prosumer_id])

		print('***initialized blockchain****')

		receipt = wait4receipt(ethclient, txHash, "registerProsumer")
		return 


	except Exception as err:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(err)
		pdb.set_trace()



class prosumer():
	def __init__(self):
		self.bids = {}
		

def mitigate(attacked_bids):
	global gw_assignment

	for bidder_id in target_gw:
		data = attacked_bids[bidder_id]
		
		choice = random.randint(0,1)

		# if (gw_attacked == 0 && choice == 0) or 
		#    (gw_attacked == 2 && choice == 1):
		#    gw_assignment[bidder_id] = contract1

		# gw_assignment[bidder_id] = contract
		# gw_assignment[bidder_id] = contract1
		# gw_assignment[bidder_id] = contract2
		gw_assignment[bidder_id] = 0



# send the bids to the block chain
#def post(bidder_name, price, quantity, period, time):
def post(parameters):
	global txHash
	global type_bid
	global last_bid
	#global rate_delay
	
	try :
		bidder_name, price, quantity, period, time = parameters

		t = int(float(period))
		tau = t % periods

		data = [period, time, bidder_name, price, quantity, 'unknown']
		f = open('bids_log_nom.csv', 'a')
		f.write( ','.join(data) + '\n' )
		f.close()

		# get list of bidders
		list_bidders = np.load('id_bidders.npy', allow_pickle=True).item()

		bidder_id = int(list_bidders[bidder_name])
		try:
			start_time = nextInterval
		except:
			pdb.set_trace()
		end_time = start_time+1

		# send the bids
		bid_quantity = int(float(quantity)*1000)
		bid_price = int(float(price)*1000)


		# ATTACK GOES HERE
		# rate_delay_tau = rate_delay[tau]
		is_targeted = False
		# check if the bidder is in the right gw
		# if gw_assignment[bidder_id] == target_gw:
		# 	rand = random.random()
		# 	if rand <= rate_delay_tau:
		# 		#change the bids of the victims
		# 		is_targeted = True 


		is_detected = random.random() <= 0
		bidder_is_seller = bid_quantity > 0
		# sellers (attackers always detect the attack)
		if is_targeted and not (is_detected or bidder_is_seller):
			pass
			# attacked_bids[bidder_id] = data #Make this global # don't need it if we use is_detected
		else:
			if gw_assignment[bidder_id] == 0 : 
				c = contract
			elif gw_assignment[bidder_id] == 1 : 
				c = contract1
			elif gw_assignment[bidder_id] == 2 : 
				c = contract2

			if bid_quantity < 0:
				# last_bid = [bidder_id, start_time, end_time, bid_quantity, bid_price]
				last_bid.append(bidder_id)
				txHash = c.postBuyingOffer(account, bidder_id, start_time, end_time, -bid_quantity, bid_price)
				# receipt = wait4receipt(ethclient, txHash, "postBuyingOffer")
				type_bid = "postBuyingOffer"
			else:
				# last_bid = [bidder_id, start_time, end_time, bid_quantity, bid_price]
				last_bid.append(bidder_id)
				txHash = c.postSellingOffer(account, bidder_id, start_time, end_time, bid_quantity, bid_price)
				# receipt = wait4receipt(ethclient, txHash, "postSellingOffer")
				type_bid = "postSellingOffer"

			#pdb.set_trace()
			# write bids in the log that we use to cumpute the equilibria
			#
			f = open('bids.csv', 'a')
			f.write( ','.join(data) + '\n' )
			f.close()

			f = open('bids_log_att.csv', 'a')
			f.write( ','.join(data) + '\n' )
			f.close()





		return '1'

	except Exception as err:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(err)
		pdb.set_trace()




def get_solution(parameters):
	global txHash
	global type_bid
	global contract
	global poll

	
	# receipt = wait4receipt(ethclient, txHash, type_bid)


	# if receipt == None:
	# 	print('Failed check transaction')
	# 	print("last_bid: %s" %last_bid)

	# 	if type_bid == "postBuyingOffer":
	# 		bidder_id, start_time, end_time, bid_quantity, bid_price = last_bid
	# 		txHash = contract.postBuyingOffer(account, bidder_id, start_time, end_time, -bid_quantity, bid_price)
	# 		receipt = wait4receipt(ethclient, txHash, "postBuyingOffer")
	# 		type_bid = "postBuyingOffer"
	# 	elif type_bid == "postSellingOffer":
	# 		bidder_id, start_time, end_time, bid_quantity, bid_price = last_bid
	# 		txHash = contract.postSellingOffer(account, bidder_id, start_time, end_time, bid_quantity, bid_price)
	# 		receipt = wait4receipt(ethclient, txHash, "postSellingOffer")
	# 		type_bid = "postSellingOffer"
	# 	else:
	# 		print("Then what is it?")
	# 		print(type_bid)

	# 	pdb.set_trace()
		

	try:
		# input data
		total_load, period, time = parameters

		# calculate the current period
		t = int(float(period))
		tau = t % periods

		# extract the bids of responsive loads
		bids = dict()
		bids_demand = []
		bids_offer = []

		total_demand = 0

		
		while last_bid: 
			poll = contract.poll_events()
			for event in poll:
				params = event['params']
				name = event['name']
				#print("{}({}).".format(name, params))

				if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):

					bidder = params['prosumer']
					last_bid.remove(int(bidder))
					# print(len(last_bid))

					interval = params['startTime']

					q = params['energy']/1000.0
					p = params['value']/1000.0
					# p, q = decode(energy)
					
					bids[bidder] = [p, q]

					if name == "BuyingOfferPosted":
						bids_demand.append( [p, q] )
						total_demand += q
					else:
						bids_offer.append( [p, q] )



		# calculate unresponsive load
		quantity_unresponsive = -1 * (float(total_load) - total_demand)
		bidder_name = 'unresp_bidder_nom'
		price_cap = '0.63'
	
		# write the bid unresponsive load in logs
		data = [period, time, bidder_name, price_cap, str(quantity_unresponsive), 'unknown']
		f = open('bids.csv', 'a')
		f.write( ','.join(data) + '\n' )
		f.close()

		f = open('bids_log_nom.csv', 'a')
		f.write( ','.join(data) + '\n' )
		f.close()

		f = open('bids_log_att.csv', 'a')
		f.write( ','.join(data) + '\n' )
		f.close()


		# add bid unresopnsive loads
		bids_demand.append( [float(price_cap), -1*quantity_unresponsive] ) 

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

	
		# the following is only necessary to verify that the market works well
		'''
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


		# write the equilibria price
		prices = [str(market_eq_nom['p'][0]), str(p_eq)]
		f = open('eq_price.csv', 'a')
		f.write( ','.join(prices) + '\n' )
		f.close()


		'''

		# initialize the file for the bids of the next period
		f = open('bids.csv', 'w')
		f.write( 'market_id,timestamp,bidder_name,bid_price,bid_quantity,bid_state\n' )
		f.close()


	except Exception as err:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(err)
		pdb.set_trace()

	#return str(market_eq_nom['p'][0])
	
	txHash = contract.submitClearingPrice(account, interval, price=int(p_eq*1000))

	for event in contract.poll_events():
		params = event['params']
		name = event['name']
		#print("{}({}).".format(name, params))

		if (name == "ClearingPrice"):
			interval = params['interval']
			price = params['price']
			#print ("price in interval %s = %s" %(interval, price))

		if (name == "StartOffering"):
			nextInterval = params['interval']
			#print ("next interval: %s" %nextInterval)

	print("period: {}".format(period))
	print("price: {}".format(p_eq))

	return str(p_eq)
	







