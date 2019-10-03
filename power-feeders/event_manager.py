from datetime import datetime, date, timedelta
from time import sleep
import sys
import signal
import time
import pdb
import copy
import numpy as np
import re
import random
import csv 
import os
import importlib
from parameters import t_0, t_f

np.set_printoptions(threshold=np.inf)

version = sys.version
if version[0] == '2':
	import urllib
else:
	import urllib.request as urllib


# create an interruption to close the gridlab server needed
def signal_handler(sig, frame):
	read_server('control/shutdown')
	print('Closing the event manager')
	os._exit(0) 
	sys.exit(0)



# extract input arguments
i = 1
port = ''
while i < len(sys.argv):
	if sys.argv[i] == '--port':
		port = sys.argv[i+1]
		i += 1
	i += 1

if port == '':
	print('Using default port 6267')
	port = 6267

signal.signal(signal.SIGINT, signal_handler)

t_last_update = t_f + timedelta(minutes = 1)


# function that communicates with the server
def read_server(url):
	global address
	message = ''
	attempts = 10
	i = 0
	while i < attempts:
		try:
			url_  = address + url
			f = urllib.urlopen( url_.replace(' ', '%20') )

			message =  f.read().decode(encoding='UTF-8')
			return message
		except:
			i += 1
	#print('Time out reading server' )
	#sys.exit()
	return None


# function that saves some object's states 
def save_records():
	for obj in dict_records.keys():
		for attr in dict_records[obj].keys():
			try:
				os.makedirs('./records/')
			except:
				pass

			with open('./records/'+obj+'_'+attr+'.csv', 'w') as f:
				writer = csv.writer(f)
				try:
					writer.writerows( dict_records[obj][attr] )
				except:
					pdb.set_trace()
	return


# function that halts the event manager until it detects that GridLAB-D initialized
def wait_for_initialization():
	print('Wait initialization')
	waiting = True
	while waiting:
		s = read_server(state)
		if s != None:
			print('... initialized')
			return 
		sleep(1)
	

# function that halts the envent manager until it detects a pause in GridLAB-D
def wait_for_pause():
	global current_time
	waiting = True
	while waiting:
		s = read_server(state)
		if s == 'PAUSED':
			waiting = False
		elif s == 'DONE':
			print('Simulation finished')
			save_records()
			sys.exit()
			pdb.set_trace()
		elif s == None:
			print("The communication with the server finished")
			save_records()
			sys.exit()
		else:
			sleep(.06)
	# update the current time
	time_raw = read_server(clock).replace(zone, '')
	current_time = datetime.strptime( time_raw, time_format)
	return


# Function that schedules the next pause and continue the simulation
def continue_simulation():
	global list_future_events
	global next_pause
	global current_time
	
	next_pause = list_future_events[0][0]
	read_server(pauseat + str(next_pause) + zone)
	return




def code_attr(line):
	n = len(line)
	line_attr = []

	declared_func = 0
	j = 0
	for i in range(n):
		if line[i] == '(':
			declared_func += 1
		elif line[i] == ')':
			declared_func -= 1
		elif line[i] == ',' and declared_func == 0:
			line_attr.append( line[j:i] )
			j = i+1
	line_attr.append( line[j:n] )
	return line_attr
			

# function that determines whether the event uses a function in the object's attributes
def parse_value(line):
	# check if the string is a function
	m = re.search(r'\(.*\)', line)
	if m == None:
		return [line]
	else:
		match = m.group()

		# find the function used
		function = line.replace( match, '' ).strip()
		if function not in dict_functions.keys():
			# check if we use an external function
			if '.' in function:
				func_name = function.split('.')
				if len(func_name) > 2:
					function = None
				else:
					# try to open the file
					try:
						module = importlib.import_module(func_name[0])
						func = getattr(module, func_name[1])
						dict_functions[function] = func
					except:
						print('Error importing the function ' + function)
					

		arguments_raw = match[1:-1]

		# extract the arguments of the function
		list_args = []
		count_parenthesis = 0
		j = 0
		for i in range(len(arguments_raw)):
			if arguments_raw[i] == '(':
				count_parenthesis += 1
			elif arguments_raw[i] == ')':
				count_parenthesis -= 1
			elif arguments_raw[i] == ',' and count_parenthesis == 0:
				list_args.append( arguments_raw[j:i] )
				j = i + 1
		list_args.append( arguments_raw[j:i+1] )

		# extract other functions recursively
		list_inputs = [parse_value(x) for x in list_args]
		try:
			return [dict_functions[function], list_inputs]
		except:
			pdb.set_trace()


# funciton that extracts a numerical value from the event specification
def get_number(x):
	m = re.search(r'[\+-]*[\d\.]+e*[\+\-\d]*', x)
	if m == None:
		print('Error: Did not find valid number:' + x)
		#pdb.set_trace()
		return 0
	else:
		try:
			return float( m.group() )
		except:
			print('Error reading the value ' + x)
			pdb.set_trace()
			return 0


# Boolean operation
def f_equal(inputs):
	values = [get_number(x) for x in inputs]
	return str( int(values[0] == values[1]) )

def f_or(inputs):
	values = [get_number(x) for x in inputs]
	val = values[-1]
	for i in range(len(values)-1):
		val = val or values[i]
	return str( int( val ) )


# function that computes the addition of two or more elements
def f_addition(inputs):
	values = [get_number(x) for x in inputs]
	return str( sum(values) )

# function that computes the subtraction of two elements
def f_subtract(inputs):
	values = [get_number(x) for x in inputs]
	if len(values) != 2:
		print('Error substracting ' + inputs)
		return 0
	else:
		return str( values[0] - values[1] )
	
# function that computes the product of two or more elements
def f_multiply(inputs):
	values = [get_number(x) for x in inputs]
	prod = values[0]
	for i in range(1, len(values)):
		prod = prod*values[i]
	return str( prod )
	
# function that chooses among two values
def f_select(inputs):
	if len(inputs) != 3:
		print("Error, the function 'select' needs 3 arguments")
		print("Inputs: " + str(inputs))
		return '0'
	values = [get_number(x) for x in inputs]
	if values[0] > 0.5:
		return inputs[1]
	else:
		return inputs[2]

def f_min(inputs):
	values = [get_number(x) for x in inputs]
	min_val = 0
	try:
		min_val = min(values)
	except:
		pdb.set_trace()
	return str( min_val )

def f_delay(inputs, attr, obj, event_id):
	global dict_events


	delay = inputs[1]
	if delay[-1] in time_conversion.keys():
		unit = delay[-1]
		delay = delay.replace(unit, '')
	else:
		unit = 's'

	time_delay = timedelta( seconds = int( float(delay) ) * time_conversion[unit] )

	value = inputs[0]
	wait_value = inputs[2]
	valid = get_number( inputs[3] ) > 0

	if int( float(delay) ) <= 0:
		return value

	if not valid:
		return wait_value



	event_name = 'delay_'+obj

	time_current_event = list_future_events[0][0]
	next_update = time_current_event + time_delay + timedelta( seconds = 0 )

	#print('next update:', next_update)

	values = {attr: [value]}

	# check if we need to create an event
	if event_name not in dict_events.keys():
		# define the event
		event = copy.deepcopy(event_layout)
		event['objects'] = set([obj])
		event['attribute'] = dict_events[event_id]['attribute']
		event['schedule'].append( {'type_time': "date", 'time': next_update, 'value': values } )
		event['next_update'] = {'time': next_update, 'index': 0}
		event['delay'] = timedelta( seconds = 0 ) 

		dict_events[event_name] = event

	else:
		# check if there is another event at the desired time
		m = len( dict_events[event_name]['schedule'] )
		found = False
		for i in range(m):
			if dict_events[event_name]['schedule'][i]['time'] == next_update:
				dict_events[event_name]['schedule'][i]['value'][attr] = [value]
				found = True
				break
		if not found:
			dict_events[event_name]['schedule'].append( {'type_time': "date", 'time': next_update, 'value': values } )


		# update the schedule
		if dict_events[event_name]['next_update']['index'] == -1:
			dict_events[event_name]['next_update']['time'] = next_update
			dict_events[event_name]['next_update']['index'] = len(dict_events[event_name]['schedule'])-1


	# update the list of events
	insert_event( next_update, event_name )

	return wait_value

def f_stats(inputs):
	values = [get_number(x) for x in inputs[0]]
	return str( sum(values) )


# functions accepted by the events
dict_functions = {'or': f_or, 'equal': f_equal, 'sum': f_addition, 'subtract': f_subtract, 'multiply': f_multiply, 'select': f_select, 'min': f_min, 'delay': f_delay, 'stats': f_stats}
#, 'divide': f_division, 'power': f_pow}

time_format = "%Y-%m-%d %H:%M:%S"

# parameters gridlbab server
address = 'http://localhost:'+str(port)+'/'
state = 'raw/mainloop_state'
pauseat = 'control/pauseat='
resume = 'control/resume'
clock = 'raw/clock'

# characters used in regular expresisons
re_metacharacters = set('^ $ * + ? { } [ ] \ | ( )')
re_metacharacters -= {' '}

# define values for the time conversion
time_conversion = {'s': 1, 'm': 60, 'h': 60*60, 'd': 60*60*24}

# import the list of objects
list_gl_objects = []
objects_file = open('list_gl_objects', 'r')
for line in objects_file:
	list_gl_objects.append( line.strip() )
#list_gl_objects.append( 'raw' )
objects_file.close()

# dictionary of virtual objects
dict_virtual_objects = dict()

# dictionary with the events
dict_events = dict()

# dictionary with the object's states to record
dict_records = dict()

# dictionary that defines the layout of an event
event_layout = {'objects': set(), 'fraction': 1.0, 'attribute': [], 'schedule': [], 'next_update': None, 'options': set(), 'delay': timedelta(seconds = 0)}

event_id = 0
event = None
reading_event = False

events_file = open('events', 'r')
file_lines = events_file.readlines()

for i in range(len(file_lines)):
	line = file_lines[i].strip() # .replace(' ', '')


	# do not read lines that are coments
	if line.startswith('#'): 
		pass


	elif line.startswith('eventID:'): 
		pass
#		l = line.split()
#		event_id = l[1]
#		event = copy.deepcopy(event_layout)
#		reading_event = True


	elif line.startswith('object:'):
		reading_event = True
		event = copy.deepcopy(event_layout)
		event_id += 1

		l = line.replace(' ', '').split(':')
		objects_raw = l[1].split(',')
		objects_raw = [s.strip() for s in objects_raw]

		#print(objects_raw)
		objects = set()

		for obj in objects_raw:
			# check if the object's name has metacharacters
			re_obj = set( obj ).intersection( re_metacharacters )
			if len(re_obj) == 0:
				objects = objects.union( set( [ obj ] ) )
			else:
				# Check if the name match any object from gridlab
				for object_i in list_gl_objects:
					if re.search(obj, object_i) != None:
						objects = objects.union( [object_i] )
				if len(objects) == 0:
					print("Didn't find objects that match: "+ obj)
					pdb.set_trace()

		event['objects'] = event['objects'].union( objects )


	elif reading_event and line.startswith('fraction:'):
		l = line.replace(' ', '').split(':')
		try:
			event['fraction'] = float(l[1])
		except:
			print("Error defining the event's attribute 'fraction' as " + l[1])
			event['fraction'] = 1.0


	elif reading_event and line.startswith('attribute:'):
		l = line.replace(' ', '').split(':')
		event['attribute'] = l[1].split(',')


	elif reading_event and line.startswith('option:'):
		l = line.replace(' ', '').split(':')
		options_raw = l[1].strip().split(',')
		event['options'] = event['options'].union( set( options_raw ) )


	elif reading_event and line.startswith('delay:'):
		l = line.replace(' ', '').split(':')
		event['delay'] = timedelta( seconds =  int(l[1]) ) 


	elif reading_event and ';' in line:
		l = line.split(';')
		l = [s.strip() for s in l]

		action_obj = {'type_time': '', 'time': None, 'value': None}

		# check the type of time value
		if l[0].startswith('+'):
			period = l[0].replace('+', '')

			# identify the unit of the time period
			if l[0][-1] in time_conversion.keys():
				unit = l[0][-1]
				period = period.replace(unit, '')
			else:
				unit = 's'

			try:
				period = timedelta( seconds = int( period ) * time_conversion[unit] )
			except:
				print("Error converting " + l[0])

			action_obj['type_time'] = 'period'
			action_obj['time'] = period

		else:
			try:
				time = datetime.strptime( l[0], time_format)
			except:
				pdb.set_trace()
			action_obj['type_time'] = 'date'
			action_obj['time'] = time

		# create the object to obtain the value
		attr_val = code_attr( l[1].replace(' ', '') )
		actions = dict()
		for i in range( len(event['attribute']) ):
			attr = event['attribute'][i]
			actions[attr] =  parse_value( attr_val[i] ) 
		action_obj['value'] = actions

		event['schedule'].append( action_obj )


	elif reading_event and ( line == '' or i == len(file_lines)-1 ):

		if event['fraction'] < 1 and 'random' not in event['options']:
			size_set_obj = len( event['objects'] )
			number_final_set = int( size_set_obj * event['fraction'] )
			sample = random.sample( event['objects'], number_final_set)
			event['objects'] = sample

		# define the time for the first update
		if event['schedule'] == []:
			time_update =  t_last_update

		else:
			if event['schedule'][0]['type_time'] == 'date':
				time_update = event['schedule'][0]['time']
			else:
				time_update = event['schedule'][0]['time'] + t_0

		if 'virtual_object' in event['options']:
			# virtual objects must be updated at the begining of the simulation

			# change the name if it was assigned to a object in gridlab
			set_objects = set()
			for obj in event['objects']:
				if obj in list_gl_objects:
					set_objects.add( obj+'_virtual' )
				else:
					set_objects.add( obj )

			event['objects'] = set_objects

			# add the objects to the set of virtual elements
			for obj in event['objects']:
				for attr in event['attribute']:
					# check if the object has an entry
					if obj in dict_virtual_objects.keys():
						dict_virtual_objects[obj][attr] = ''
					else:
						dict_virtual_objects[obj] = {attr: '0'}

		event['next_update'] = {'time': time_update , 'index': 0} # + event['delay']

		dict_events[event_id] = dict(event)
		reading_event = False

		# print the set of objects for faults
		#if 'fault' in event_id:
		#	print(event['objects'])

		if 'save' in event['options']:
			for attr in event['attribute']:
				for obj in event['objects']:
					if obj in dict_records.keys():
						dict_virtual_objects[obj][attr] = []
					else:
						dict_records[obj] = {attr: []}

events_file.close() 


# function that gets the time of the next event
def get_time_next_event(event_id):
	global current_time
	global dict_events
	event_obj = dict_events[event_id]
	scheduled_update = event_obj['next_update']

	delay = event_obj['delay']
	
	# check if we need to update the time of the next action
	if scheduled_update['time'] > current_time:
		return scheduled_update['time'] + delay

	elif scheduled_update['time'] <= current_time:
		schedule = event_obj['schedule']
		index = scheduled_update['index']
		n = len(schedule)

		new_update = ''
		next_time = scheduled_update['time']
		next_index = index

		while next_time <= current_time:
			next_index += 1

			# check if we reached the end of the schedule
			if next_index >= n:
				# check if we need to repeat the schedule
				if 'repeat' in event_obj['options']:
					# get the index of schedule to repeat
					while next_index-1 >= 0:
						if schedule[next_index-1]['type_time'] == 'period':
							next_index -= 1
						else:
							break
					next_time += schedule[next_index]['time']

				else:
					next_time = t_last_update
					next_index = -1

			# change the next update time
			else:
				if schedule[next_index]['type_time'] == 'date':
					next_time = schedule[next_index]['time']
				else:
					next_time += schedule[next_index]['time']

		# update the events
		new_update = {'time': next_time, 'index': next_index}
		event_obj['next_update'] = new_update 
		dict_events[event_id] = event_obj
		return next_time + delay


# function that carries out the event (read or write the attribute's values)
def execute_action(event_id):
	global current_time
	global dict_events
	global prior_obj_values

	event_obj = dict_events[event_id]
	scheduled_update = event_obj['next_update']

	if scheduled_update['time'] <= current_time:

		# select the objects to read/write
		if event_obj['fraction'] < 1 and 'random' in event_obj['options']:
			size_set_obj = len( event_obj['objects'] )
			number_final_set = int( size_set_obj * event_obj['fraction'] )
			sample = random.sample( event_obj['objects'], number_final_set)
		else:
			sample = event_obj['objects']

		for obj in sample:

			# get the value that we need to write
			index = scheduled_update['index']
			schedule = event_obj['schedule'][index]


			virtual_obj = 'virtual_object' in event_obj['options']

			for attr in schedule['value'].keys():
				#try:
				#	attr = schedule['value'].keys()[i]
				#except:
				#	pdb.set_trace()
				# store the attribute's value before the modifications
				if prior_obj_values[obj] == None:
					if not virtual_obj:
						prior_obj_values[obj] = read_attr_obj(obj, attr)
					else:
						prior_obj_values[obj] = read_attr_virtual_obj(obj, attr)


				#print(schedule['value'])
				try:
					value = get_value(schedule['value'][attr], attr, obj, event_id)
				except:
					pdb.set_trace()
					value = get_value(schedule['value'][attr], attr, obj, event_id)
				
				#if 'virtual' in obj:
				#	pdb.set_trace()
				



				if not virtual_obj:
					write_attr_obj(obj, attr, value)

				else:
					try:
						write_attr_virtual_obj(obj, attr, value)
					except:
						pdb.set_trace()

				#if 'save' in event_obj['options']:
				if obj in dict_records.keys():
					dict_records[obj][attr].append( [str(current_time),  str(value)] )

	return


# function that reads the attribute of an object in GridLAB-D
def read_attr_obj(target, attr):
	if attr == 'name':
		return target
	else:
		return str(read_server('raw/' + target + '/' + attr))


# function that modifies the attributes of objects in GridLAB-D
def write_attr_obj(target, attr, val):
	#print('raw/' + target + '/' + attr + '=' + val)
	try:
		message = read_server('raw/' + target + '/' + attr + '=' + val)
	except:
		pdb.set_trace()
	#print(message)
	return 


# function that reads the attribute of a virtual object
def read_attr_virtual_obj(target, attr):
	return dict_virtual_objects[target][attr]


# function that writes the attribute of a virtual object
def write_attr_virtual_obj(target, attr, val):
	dict_virtual_objects[target][attr] = val
	return


# function that gets recursively the value of an attribute. It gathers values from different objects and computes functions if necessary
def get_value(op_tree, attr, obj, event_id):
	if len(op_tree) == 1:
		return read_data( op_tree[0].strip(), obj)
	else:
		func = op_tree[0]
		arguments = [get_value(x, attr, obj, event_id) for x in op_tree[1]]

		try:
			if func == f_delay:
				val = func ( arguments, attr, obj, event_id )
			else:
				val = func ( arguments )
		except:
			pdb.set_trace()
			val = func ( arguments, attr, obj, event_id )
		return val


# Function that reads the attribute of objects (virtual or from GridLAB-D)
def read_data(line, obj):
	# determine the type of operation for the system
	if 'default' == line:
		return prior_obj_values[obj]

	elif '/' in line:
		components = line.split('/')

		# check if the source is a regular expression
		re_obj = set( line ).intersection( re_metacharacters )
		if len(re_obj) != 0:
			# check if the virtual object has a twin in gridlab
			obj_temp = obj.replace('_virtual', '')
			if obj not in dict_virtual_objects.keys() or obj_temp not in list_gl_objects:
				obj_temp = obj

			m = re.search(components[0], obj_temp)
			if m == None:
				objects=set()
				for object_i in list_gl_objects:
					if re.search(components[0], object_i) != None:
						objects = objects.union( [object_i] )
				if len(objects) == 0:
					print("Didn't find objects that match: "+ components[0])
					pdb.set_trace()
				source = list(objects)
				source_attr = components[1]
			else:
				source = [m.group()]
				source_attr = components[1]

		else:
			source = [components[0]]
			source_attr = components[1]


		value = []
		for s in source:
			if s in dict_virtual_objects.keys():
				value.append( read_attr_virtual_obj(s, source_attr) )
			else:
				value.append( read_attr_obj(s, source_attr) )

		#if 'timer' in obj:
		#	pdb.set_trace()

		if len(value) == 1:
			return value[0]
		else:
			return value

	else:
		return line


# Function that updates the list of future events
def insert_event(time, event_id):
	global list_future_events

	m = len(list_future_events)
	for i in range(m):
		event = list_future_events[i]
		if event[0] == time:
			list_future_events[i][1].update( [event_id] )
			return
		elif event[0] > time:
			list_future_events.insert( i, [time, set( [event_id] ) ] )
			return
	list_future_events.append( [time, set( [event_id] ) ] )
	return




# define the initial value of the conponents
set_events = set(dict_events.keys())

set_objects = set()
prior_obj_values = dict()
for event_id in set_events:
	set_objects = set_objects.union( dict_events[event_id]['objects'] )

for obj in set_objects:
	prior_obj_values[obj] = None


# define the list of next events
list_future_events = []
for event_id in set_events:
	time = dict_events[event_id]['next_update']['time']
	insert_event(time, event_id)


# wait for the initialization of gridlab
wait_for_initialization()


# check if we need the timezone
time_raw = read_server(clock)
time_parts = time_raw.split()
zone = ''
if len(time_parts) > 2:
	zone = ' ' + time_parts[-1]


# check all the events and determine the next interruptions
current_time = t_0
next_pause = current_time

#pdb.set_trace()



simulation_runs = True
while simulation_runs:
	# check that the system reaches a pause

	#pdb.set_trace()
	wait_for_pause()

	# execute all the relevant actions 
	updating = True
	while updating and len(list_future_events) > 0:
		event_time = list_future_events[0][0]
		events = list_future_events[0][1]
		if event_time <= current_time:
			'''
			if current_time > t_0 +  timedelta( hours = 11 ): 
				print(np.array(list_future_events))
				pdb.set_trace()
			'''
			for event_id in events:
				execute_action(event_id)

			list_future_events.pop(0)
			for event_id in events:
				next_update = get_time_next_event(event_id)
				insert_event( next_update, event_id )

		else:
			updating=False
	
	continue_simulation()






