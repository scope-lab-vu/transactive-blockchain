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

folder = './simulations/' + model + '/normal/'


# name of the data files
load = 'total_power_network_node.csv'

market = 'market.csv'

hvac = 'hvac.csv'

# extract the total load
data_substation = read_data( folder + load)
hourly_load = rolling_statistics(data_substation['time'], data_substation['measured_real_power'], 60)

# data with the normal simulations
#data_substation = read_data( folder + load)
#hourly_load_b = periodic_data(data_substation['time'], data_substation['measured_real_power'], 60)
hourly_load = periodic_data(hourly_load['time'], hourly_load['mean'], 60)



data_market = read_data( folder + market)
hourly_prices = rolling_statistics(data_market['time'], data_market['current_market.clearing_price'], 60)
hourly_prices = periodic_data(hourly_prices['time'], hourly_prices['mean'], 60)

data_hvac = read_data( folder + hvac)

# calculate the reserves
reserves = hourly_load['data']*1.1



# define the time interval
t_1 = datetime.strptime( '2009-06-01 00:00:00', time_format)
t_2 = datetime.strptime( '2009-06-01 23:00:00', time_format)


n = len(reserves)
z1 = 0
z2 = 0
for i in range(n):
	if hourly_load['time'][i] == t_1:
		z1 = i
	if hourly_load['time'][i] == t_2:
		z2 = i

axis_time = hourly_load['time'][z1:z2+1]
axis_hour = []
for t in axis_time:
	axis_hour.append( t.strftime("%H") )

x = [i for i in range(len(axis_time))]




######################################################
# plot the total demand

days = mdates.DayLocator()
hours = mdates.HourLocator()
minute = mdates.MinuteLocator()
hoursFmt = mdates.DateFormatter('%H')

step = 6

#fig, ax = plt.subplots()
#fig, ax = plt.subplots()

plt.figure(1)
plt.clf()

#plt.plot(data_substation['time'], data_substation['measured_real_power'], label='Demand')
#ax.plot(hourly_load['time'], hourly_load['data']/1000, label='Demand')
#ax.plot(hourly_load['time'], reserves/1000, label='Total generation available')

plt.plot(x, hourly_load['data'][z1:z2+1]/1000, label='Total demand')
#plt.plot(x, hourly_load['data'][z1:z2+1]/1000, '.-', label='Estimated demand')
#plt.plot(x, reserves[z1:z2+1]/1000, '--', label='Available generation')

#ax.xaxis.set_major_locator(hours)
#ax.xaxis.set_major_formatter(hoursFmt)
#ax.xaxis.set_minor_locator(minutes)

#plt.title('Total Demand')
plt.xlabel('Time')
plt.ylabel('Load (kVA)')
plt.subplots_adjust(left=0.15)
#plt.legend()
plt.xticks(x[0::step], axis_hour[0::step])
#plt.xlim([t_1, t_2])
plt.show()
plt.savefig('load.png', bbox_inches='tight')


plt.figure(2)
plt.clf()

plt.plot(x, hourly_prices['data'][z1:z2+1]/1000, label='Prices')
plt.xlabel('Time')
plt.ylabel('Price')
plt.subplots_adjust(left=0.15)
#plt.legend()
plt.xticks(x[0::step], axis_hour[0::step])
#plt.xlim([t_1, t_2])
plt.show()
plt.savefig('prices.png', bbox_inches='tight')



samples = int(len(data_hvac['time'])/3)

plt.figure(3)
plt.clf()
plt.step(data_hvac['time'][0:samples], data_hvac['cooling_setpoint'][0:samples], label='Cooling setpoint')
plt.plot(data_hvac['time'][0:samples], data_hvac['air_temperature'][0:samples], label='Indoor Temp.')
plt.plot(data_hvac['time'][0:samples], data_hvac['outdoor_temperature'][0:samples], label='Outdoor Temp.')
plt.xlabel('Time')
plt.ylabel('Temperature (F)')
plt.legend()
plt.show()
plt.savefig('hvac.png', bbox_inches='tight')

