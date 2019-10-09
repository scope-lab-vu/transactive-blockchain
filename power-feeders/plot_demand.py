import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import matplotlib.dates as mdates

#from parameters import attack, gamma, lambda_, time_att, time_prelude, time_end_att, max_price

#from functions_auction import build_curves, find_equilibrium_auction, extract_bids, order_bids_descending, order_bids_ascending, find_market_equilibrium


# function to extract the data fromm the CSV files
def read_data(csv_file):
	global time_format

	# read the data from the transformer
	with open(csv_file) as csvf:
		readcsv = csv.reader(csvf, delimiter=',')
		row = []
		last_row=[]
		# Skip the first lines of the files
		for row in readcsv:
			if 'timestamp' in row[0]:
				last_row = row
				break

		try:
			m = len(row)-1
			labels = last_row[1:]
		except:
			print('Error extracting the data')
			pdb.set_trace()

		date = []
		data = []
		for row in readcsv:
			n = len(row[0])

			# check if the data row is complete
			if len(row)< m+1:
				break

			# extract the date
			try:
				if n > 23:
					timestamp = datetime.strptime(row[0].replace(' PDT', ''), time_format_b)
				else:
					timestamp =  datetime.strptime(row[0].replace(' PDT', ''), time_format)
			except:
				print('Error extracting the date')
				pdb.set_trace()
				timestamp = ''

			# extract the data
			vec = []
			for col in row[1:]:
				try:
					if 'd' in col:
						val = col.replace('d', 'j')
						#trick to obtain the magnitude of the element
						val = complex(val).real
					elif 'i' in col:
						val = col.replace('i', 'j')
						val =  complex(val)
					elif 'j' in col:
						val = complex(col)
					else:
						val = float(col)

					vec.append( val )
				except:
					print('Error extracting the data')
					pdb.set_trace()
					vec = []
					#break
			if len(vec) > 0:
				data.append( vec )
				date.append( timestamp )

	# case when the file doesn't have information
	if len(data) == 0:
		vec = []
		[vec.append(0) for i in range(0, m)]
		data.append(vec)
		date = [0]

	data = np.array( data )
	date = np.array( date )

	total_data = dict( [ ( labels[i], data[:,i] ) for i in range(m)] )
	total_data['time'] = date
	total_data['labels'] = labels

	return total_data



# function tha calculates the mean and std of a time series in a fixed window interval
def rolling_statistics(t, x, period):
	t_stats = []
	mean = []
	std = []

	n = len(x)

	t0 = t[0]
	delta_t =  timedelta( minutes=period )

	# determine the right position of the sampling window
	i = 0
	j=0
	while t[i+1] <= t0 + delta_t and i<n:
		i += 1

	while i < n:
		# determine the left position of the sampling window
		while t[j] < t[i] - delta_t:
			j += 1

		t_stats.append( t[i] )
		mean.append( np.mean( x[j:i] ) )
		std.append( np.std( x[j:i] ) )

		i += 1

	stats = dict( [ ('time', np.array(t_stats) ) ] )
	stats['mean'] = np.array(mean)
	stats['std'] = np.array(std)

	return stats



# find the index of 'time' in a vector 'date'. If the value is not exact, then return the closest i such that date[i]<time
def find_index(date, time):
	# period of samples
	d0 = date[0]
	d1 = date[1]
	delta = (d1-d0).total_seconds()

	index = (time-d0).total_seconds() / delta
	index = int( np.floor( index ) )

	n = len(date)

	if date[index] == time:
		return index
	elif date[index] > time:
		while index > 0 and date[index] > time:
			index -= 1
		return index
	elif date[index] < time:
		while index < n and date[index] < time:
			index += 1
		return index-1



def measure_peak(date_normal, normal_p, date_attack, attack_p, time):
	offset1 = 2
	offset2 = 3
	index = find_index(date_normal, time)
	demand = np.mean( normal_p[index+offset1 : index + offset2] )

	index_att = find_index(date_attack, time)
	demand_att = np.mean( attack_p[index_att+offset1 : index_att + offset2] )

	peak = demand_att
	diff = demand_att - demand
	ratio = demand_att / demand

	return peak, diff, ratio


def periodic_data(time, data, period):

	current_t = time[0]
	delta_t =  timedelta( minutes=period ) 
	next_sample = current_t + delta_t

	n = len(data)
	i = 0

	time_samples = []
	samples = []

	while i < n:
		try:
			current_t = time[i]
		except:
			pdb.set_trace()
		if current_t == next_sample:
			time_samples.append( current_t )
			samples.append( data[i] )
			next_sample = current_t + delta_t

		elif current_t > next_sample:
			time_samples.append( next_sample )
			samples.append( data[i] )
			next_sample = next_sample + delta_t
		i += 1


	sampled_data = dict( [ ('time', np.array( time_samples )) ] )
	sampled_data['data'] = np.array( samples )
	return sampled_data

time_format = "%Y-%m-%d %H:%M:%S"
time_format_b = "%Y-%m-%d %H:%M:%S.%f"

# name of the model
model = 'R1_1247_3_t6'


model = 'R1_1247_3_t6_small'
#folder = './simulations/' + model + '/nominal/'
#stats = 'current_price_mean_24h'


folder = './simulations/' + model + '/nominal_24h/'
stats = 'current_price_mean_24h'

#folder = './simulations/' + model + '/nominal_1h/'
#stats = 'current_price_mean_1h'





# name of the data files
load = 'total_power_network_node.csv'

market = 'market_nom.csv'

# extract the total load
data_substation = read_data( folder + load)

data_market = read_data( folder + market)



plt.figure(1)
plt.clf()
plt.plot(data_market['time'], data_market['current_market.clearing_price'], label='clearing price')
plt.plot(data_market['time'], data_market[stats], label='mean price')
plt.legend()
plt.show()




plt.figure(2)
plt.clf()
plt.plot(data_market['time'], data_market['current_market.clearing_quantity'], label='clearing quantity')
plt.plot(data_substation['time'], data_substation['measured_real_power']/1000, label='Real load')
plt.legend()
plt.show()


