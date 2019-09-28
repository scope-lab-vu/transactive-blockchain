import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta

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

	#columns = [ data[:,i] for i in range(0, m) ]

	total_data = dict( [ ( labels[i], data[:,i] ) for i in range(m)] )
	total_data['time'] = date
	total_data['labels'] = labels
	
	return total_data





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



def rolling_statistics_b(x, number_samples):
	mean = []

	n = len(x)

	for i in range(n):
		k = max(0, i+1-number_samples)
		mean.append( np.mean(x[k:i+1]) )	
	return np.array( mean )



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

# name of the model
model = 'R1_1247_3_t6'

folder = './simulations/' + model + '/normal/'



time_format = "%Y-%m-%d %H:%M:%S"
time_format_b = "%Y-%m-%d %H:%M:%S.%f"



# name of the data files
load = 'total_power_network_node.csv'
hvac = 'hvac.csv'

# data with the normal simulations
data_substation = read_data( folder + load)
hourly_load = periodic_data(data_substation['time'], data_substation['measured_real_power'], 60)


#exit
#load_stats = rolling_statistics( data_substation['time'], data_substation['measured_real_power'], 60)


data_hvac = read_data( folder + hvac)
hourly_temp = periodic_data(data_hvac['time'], data_hvac['outdoor_temperature'], 60)

avg_dayly_temp = rolling_statistics_b( hourly_temp['data'], 24)



# get the hour and the day of the week of each sample
day_of_week = []
hour = []
samples_time = hourly_load['time']
for t in samples_time:
	day_of_week.append( t.weekday() )
	hour.append( t.hour )

day_of_week = np.array( day_of_week )
hour = np.array( hour )

timestamp = []
for t in samples_time:
	timestamp.append( str(t) )



np.savetxt('data_load.csv', np.column_stack((timestamp, day_of_week, hour, hourly_temp['data'], avg_dayly_temp, hourly_load['data'])), delimiter=',', fmt='%s')









