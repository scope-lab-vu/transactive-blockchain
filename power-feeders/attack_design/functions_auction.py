import pdb
import csv
import copy
import numpy as np
from datetime import datetime, date, time, timedelta

time_format = "%Y-%m-%d %H:%M:%S"
time_format_b = "%Y-%m-%d %H:%M:%S.%f"


def build_curves(bids, order):
	delta = 0.1*-0

	curve_p = []
	curve_q = []

	total_q = 0

	for i in range(len(bids)):
		bid = bids[i]
		bid_p = bid[0]
		bid_q = bid[1]

		curve_p.append( bid_p )
		curve_q.append( total_q + delta )

		total_q += bid_q # * order

		curve_p.append(bid_p)
		curve_q.append( total_q - delta )

	if order == -1:
		curve_p.append( 0 )
		curve_q.append( total_q + delta )

	curve = dict()
	curve['p'] = curve_p
	curve['q'] = curve_q

	return curve




def find_equilibrium_auction(bids_offer, bids_demand):
	offers = len(bids_offer)
	demand = len(bids_demand)

	i = 0
	j = 0	

	try:
		p_i = bids_demand[i, 0]
		q_i = bids_demand[i, 1]

		p_j = bids_offer[j, 0]
		q_j = bids_offer[j, 1]
	except:
		pdb.set_trace()

	if p_i < p_j:
		return 0, (p_j-p_i)/2

	except_counter = 0
	k = 0
	while except_counter < 3:
		k += 1
		if k>100:
			print(k)
			pdb.set_trace()

		while (q_i >= q_j) and (p_i >= p_j) and (j+1 < offers):
			k=0

			if j+1 == offers:
				except_counter += 1
				break

			p_j_next = bids_offer[j+1, 0]
			if p_j_next < p_i:
				if j < offers:
					j += 1
					p_j = bids_offer[j, 0]
					q_j += bids_offer[j, 1]
			else:
				return q_j, p_i

		while q_i < q_j and p_i >= p_j and i+1 < demand:
			k=0

			if i+1 == demand:
				except_counter += 1
				break

			p_i_next = bids_demand[i+1, 0]
			if p_j < p_i_next:
				if i < demand:
					i += 1
					p_i = bids_demand[i, 0]
					q_i += bids_demand[i, 1]

			else:
				return q_i, p_j

		if i+1 == demand or j+1 == offers:
			except_counter += 1


	if i+1 == demand:
		return q_i, p_j

	#elif j+1 == offers:
	#	return q_j, p_j
	else:
		print('error finding the equilibrium')
		pdb.set_trace()


def extract_bids(file_bids):
	with open(file_bids) as csvf:
		readcsv = csv.reader(csvf, delimiter=',')
		# Skip the first lines of the files
		for row in readcsv:
			if 'timestamp' in row:
				break	
		m = len(row)

		current_market = 0

		market = []
		bids = dict()
		time = []

		timestamp = ''

		for row in readcsv:

			n = len(row[0])
		
			# check for incomplete data
			if len(row)< m:
				break

			#extract the bids
			if row[5] != 'off':

				# get the market_id
				market_id = int(float(row[0]))

				if current_market < market_id:

					current_market = market_id

					# store the bids and restart the list of bids
					time.append( timestamp )
					market.append( bids )

					bids = dict()

					# get the timestamp
					try:
						timestamp =  datetime.strptime(row[1].replace(' PDT', ''), time_format)
					except: 
						print('Error extracting the timestamp')
						pdb.set_trace()


				bidder_name = row[2]
				p = float( row[3] )
				q = float( row[4] )
				bids[ bidder_name ] = [p, q]

		# store the last bids 
		time.append( timestamp )
		market.append( bids )


	#pdb.set_trace()
	return time[1:], market[1:]


def order_bids_descending(bids):
	try:
		if len(bids) <= 1:
			return bids
		else:
			bids = bids[ bids[:, 0].argsort(axis=0) ]
			bids = bids[::-1]
	except:
		pdb.set_trace()
	return bids


def order_bids_ascending(bids):
	try:
		if len(bids) <= 1:
			return bids
		else:
			bids = bids[ bids[:, 0].argsort(axis=0) ]
	except:
		pdb.set_trace()
	return bids


def find_market_equilibrium(data_bids):
	# extract bids
	time, market = extract_bids(data_bids)

	# get the number of auctions
	total_auctions = len(market)

	# compute the demand and offer curves
	eq_p = []
	eq_q = []

	#customer_surplus = []
	#seller_surplus = []

	ordered_market = []
	eq_curves = []
	for k in range(total_auctions):
		# get bids for the current period
		bids = market[k]

		# extract offers and demand
		bids_offer = []
		bids_demand = []
		for bidder in bids:
			p, q = bids[bidder]
			if q<0:
				bids_demand.append( [p, -q] )
			elif q>0:
				bids_offer.append( [p, q] )

		# transform into an array
		bids_demand = np.array(bids_demand)
		bids_offer = np.array(bids_offer)

		bids_demand = order_bids_descending(bids_demand)
		bids_offer = order_bids_ascending(bids_offer)

		number_offers = len(bids_offer)
		number_demand = len(bids_demand)


		if number_demand<=0 or number_offers<=0:
			q = 0
			p = 0
			#pdb.set_trace()
		else:
			# order the bids according to the price
			q, p = find_equilibrium_auction(bids_offer, bids_demand)

		eq_p.append( p )
		eq_q.append( q )


		total_val = val(bids_demand, q)
		total_cost = cost(bids_offer, q)

		#customer_surplus.append( total_val - q*p )
		#seller_surplus.append( p*q - total_cost )




		ordered_bids = dict()
		ordered_bids['demand'] = bids_demand
		ordered_bids['offer'] = bids_offer

		ordered_market.append( ordered_bids )

		curves = dict()
		curves['demand'] =  build_curves(bids_demand, -1)
		curves['offer'] = build_curves(bids_offer, 1)
		
		eq_curves.append(curves)

	#surplus = dict()
	#surplus['customer'] = np.array( customer_surplus )
	#surplus['seller'] = np.array( seller_surplus )

	equilibrium = dict()
	equilibrium['p'] = np.array(eq_p)
	equilibrium['q'] = np.array(eq_q)

	return np.array(time), equilibrium, ordered_market, eq_curves #, surplus



# get the bidders
def extract_bidders(file_bids):
	with open(file_bids) as csvf:
		readcsv = csv.reader(csvf, delimiter=',')

		# Skip the first lines of the files
		for row in readcsv:
			if 'timestamp' in row:
				break	

		m = len(row)
		current_market = 0

		bidders = []
		time = []

		timestamp = ''
		bidders_k = set()

		for row in readcsv:

			n = len(row[0])
		
			# check for incomplete data
			if len(row)< m:
				break

			#extract the bids
			if row[5] != 'off':

				# get the market_id
				market_id = int(row[0])

				if current_market < market_id:

					current_market = market_id

					# store the bids and restart the list of bids
					time.append( timestamp )
					bidders.append( bidders_k )

					bidders_k = set()

					# get the timestamp
					try:
						timestamp =  datetime.strptime(row[1].replace(' PDT', ''), time_format)
					except: 
						print('Error extracting the timestamp')
						pdb.set_trace()

				bidder_name = row[2]
				p = float( row[3] )
				q = float( row[4] )
				if q < 0:
					bidders_k.add( bidder_name.replace('att_', '').replace('_nom', '').replace('_att', '') )

		# store the last bids 
		time.append( timestamp )
		bidders.append( bidders_k )


	#pdb.set_trace()
	return time[1:], bidders[1:]




def surplus_f(bids, eq):
	n = len(bids)

	customer_surplus = []
	seller_surplus = []
	for k in range(n):
		offer = bids[k]['offer']
		asks = bids[k]['demand']

		p_eq = eq['p'][k]
		q_eq = eq['q'][k]

		total_val = val(asks, q_eq)
		total_cost = cost(offer, q_eq)

		customer_surplus.append( total_val - q_eq * p_eq )
		seller_surplus.append( p_eq * q_eq - total_cost )

	surplus = dict()
	surplus['customer'] = np.array( customer_surplus )
	surplus['seller'] = np.array( seller_surplus )
	return surplus


def ideal_eq_attack(bids, lambda_):
	bids_ideal = []
	n = len(bids)

	eq_p = []
	eq_q = []

	eq_curves=[]
	for k in range(n):
		# original bids
		offer = bids[k]['offer']
		asks = bids[k]['demand']

		asks = order_bids_descending(asks)
		offer = order_bids_ascending(offer)

		# modified bids
		new_bids = dict()
		new_offer = copy.deepcopy(offer)
		new_offer[:, 0] = new_offer[:, 0]  * (2-lambda_)
		new_bids['offer'] = new_offer
		new_bids['demand'] = asks

		bids_ideal.append(new_bids)

		number_offers = len(new_bids['offer'])
		number_demand = len(new_bids['demand'])

		if number_demand<=0 or number_offers<=0:
			q = 0
			p = 0
		else:
			# order the bids according to the price
			q, p = find_equilibrium_auction(new_bids['offer'], new_bids['demand'])

		# find the real price
		#pdb.set_trace()
		k=0
		total_q = offer[k, 1]
		while total_q <= q:
			k+=1
			total_q += offer[k, 1]
		p_real = offer[k][0]

		eq_p.append( p_real )
		eq_q.append( q )


		curves = dict()
		curves['demand'] = build_curves(new_bids['demand'], -1)
		curves['offer'] = build_curves(new_bids['offer'], 1)
		
		eq_curves.append(curves)


	equilibrium = dict()
	equilibrium['p'] = np.array(eq_p)
	equilibrium['q'] = np.array(eq_q)

	return equilibrium, bids_ideal, eq_curves


def v_i(mar_val, q_max, x):
	if x > q_max:
		return q_max * mar_val 
	else:
		return x * mar_val



def c_i(mar_cost, power_block, x):
	if x > power_block:
		return power_block * mar_cost
	else: 
		return x * mar_cost



def val(bids_demand, eq_q):
	total_val = 0
	total_q = eq_q
	for bid in bids_demand:
		p = bid[0]
		q = abs(bid[1])
		x = min(total_q, q)
		total_val += v_i(p, q, x)
		total_q -= x
		if total_q <= 0 :
			break
	return total_val


def cost(bids_offer, eq_q):
	total_cost = 0
	total_q = eq_q
	for bid in bids_offer:
		p = bid[0]
		q = abs(bid[1])
		x = min(total_q, q)
		total_cost += c_i(p, q, x)
		total_q -= x
		if total_q <= 0 :
			break
	return total_cost



def avg_total_surplus(surplus, k_a):
	return np.mean( surplus['customer'][k_a:-1] + surplus['seller'][k_a:-1] )


def maer(x, y, k_a):
	diff = (x[k_a:-1] - y[k_a:-1]) #/ x[k_a:-1]
	return np.mean( diff )
#	return np.mean( abs(diff) )



def stats(a, b, k_a):
	diff = a[k_a:-1] - b[k_a:-1]
	avg_diff = np.mean(diff)
	max_diff = max(diff)
	min_diff = min(diff)
	return avg_diff, max_diff, min_diff
	




def select_bids(bids, eq, gamma):
	T = len(bids)

	new_bids = []
	for k in range(T):
		eq_q = eq['q'][k]

		q = bids[k]['demand'][:, 1]
		avg_q = np.mean( q )
		q_max = sum(q)

		n = len( q )
		n_a = gamma * n

		small_q = []
		for j in range(n):
			if q[j] < avg_q:
				small_q.append( q[j] )

		num_small_q = len( small_q )
		if num_small_q > 0:
			avg_small_q = np.mean(small_q)

			exp_q = gamma * n * avg_small_q

			q_min = q_max - sum(small_q)

			delta_q = q_max - q_min
			num = delta_q * eq_q - q_max * exp_q
			den = delta_q - exp_q
			q_op = num/den
			
			# number of bids to drop
			try:
				n_d = int((eq_q - q_op) / avg_small_q)
			except:
				n_d = 0
			if n_d >= 0 and n_d*avg_small_q < q_min:
				
				new_bid_k = dict()
				new_bid_k['offer'] = bids[k]['offer']
				
				# make zero some bids
				bids_demand = bids[k]['demand']
				l = 0
				c = 0
				while c < n_d and l<n:
					if bids_demand[l, 1] < avg_q:
						bids_demand[l, 0] = 0
						c += 1
					l += 1

				new_bid_k['demand'] = bids_demand
				new_bids.append( new_bid_k )

				#if k == 716:
				#	pdb.set_trace()


			else:
				new_bids.append( bids[k] )
		
		else:
			new_bids.append( bids[k] )

	return new_bids




