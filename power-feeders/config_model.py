import os
import sys
import copy
import pdb
import random
import numpy as np

from lib_parser_GLM.parser_GLM import parser_GLM

from parameters import t_0, t_f, period_min, max_capacity, max_price, blocks, weather, use_servermode, use_generator


pause_t = t_0

period = period_min * 60
total_time = (t_f - t_0).total_seconds()
loop = int(total_time/period)



model_input = ''
model_output = ''
# extract input arguments
i = 1
while i < len(sys.argv):
	if sys.argv[i] == '-i':
		model_input = sys.argv[i+1]
		i += 1
	elif sys.argv[i] == '-o':
		model_output = sys.argv[i+1]
		i += 1
	i += 1

if model_input == '':
	print('We need an input file!')
	sys.exit()

if model_output == '':
	model_output = model_input


# name of the files
model_output_tmp = model_output+'.tmp'
model_name = model_input.split('/')[-1].replace('.glm', '')






#####################################################################
# elements of the GLM file
clock='''
clock {
     timezone PST+8PDT;
     starttime 'start_t';
     stoptime 'finish_t';
}
'''
clock = clock.replace('start_t', str(t_0) )
clock = clock.replace('finish_t', str(t_f) )


# definition of global variables and libraries
header = '''
#include "appliance_schedules.glm";
#include "water_and_setpoint_schedule_v5.glm";
#include "commercial_schedules.glm";
#include "daily_elasticity_schedules.glm";

#set threadcount=1;
#set profiler=1;
#set relax_naming_rules=1;
#set suppress_repeat_messages=1

#set deltamode_maximumtime=1000000000
#set deltamode_iteration_limit=10

#set minimum_timestep=60

'''

# add interruption for the servermode
if use_servermode:
	header += "#set pauseat='pause_t'"
	header = header.replace('pause_t', str(pause_t))


# definition of modules
modules = '''
module tape;
module residential {
     implicit_enduses NONE;
	 //enable_subsecond_models true;
	 //all_house_delta true;
	 //deltamode_timestep 200.0 ms;
}
module powerflow {
    solver_method NR;
    NR_iteration_limit 50;
    enable_subsecond_models true;
    all_powerflow_delta true;
    enable_frequency_dependence true;
    deltamode_timestep 10.0 ms;
    default_maximum_voltage_error 1e-6;
};
module generators {
	enable_subsecond_models true;
	deltamode_timestep 10.0 ms;
}
module market;
module climate;
'''



weather_object = '''

object climate {
     name "weather**";
     tmyfile "weather**.tmy2";
     interpolate QUADRATIC;
};

'''.replace('weather**', weather)



# definition of the auction class
classes = '''
class auction {
     double current_price_mean_1h;
     double current_price_stdev_1h;
};
'''




# definition of the auction object
our_auction = '''
object auction {
     name Market_1;
     period period**;
     special_mode NONE;
     unit kW;

     price_cap max_price**;
     init_price 0.024;
     init_stdev 0.024;

     capacity_reference_object meter;
     capacity_reference_property measured_real_power;
     //capacity_reference_bid_price max_price**;
     //max_capacity_reference_bid_quantity 1000;

    warmup 0;
    verbose 1;

    transaction_log_file log_file.csv;
    curve_log_file bid_curve.csv;
 
}

'''.replace('loop*', str(loop)).replace('max_price**', str(max_price)).replace('period**', str(period))



# configure the Sellers
single_stub_bidder = '''
object stub_bidder{
	name block_x**;
	market Market_1;
	bid_period period**;
	count 32767;
	role SELLER;
	price price**;
	quantity quantity**;
}

'''.replace('loop*', str(loop)).replace('period**', str(period))

power_block = max_capacity/blocks
def cost(x):
	return max_price * x**2 / max_capacity**2

stub_bidders = []
for i in range(blocks):
	q = power_block * (i+1)
	p = cost( q )
	bidder = single_stub_bidder
	bidder = bidder.replace('price**', str(p))
	bidder = bidder.replace('quantity**', str(power_block))
	bidder = bidder.replace('x**', str(1+i))
	stub_bidders.append( bidder )






# create the parser of the GLM file
glm = parser_GLM()
glm.create_list_elements(model_input)

# remove elements
glm.find_and_remove([['class', ['auction', 'collector', 'billdump', 'player', 'recorder']]])
glm.find_and_remove([['type', ['class', 'clock']]])

passive_c = glm.find_objects([['class', 'passive_controller'], ['control_mode', 'ELASTICITY_MODEL']])
glm.remove_objects(passive_c)


# configure the network node
nn_id = glm.find_objects([['class', 'meter'], ['name', 'network_node']])
#print(nn_id)
#pdb.set_trace()
#glm.modify_attr( nn_id[0], 'nominal_voltage', str(7200) )
glm.modify_attr( nn_id[0], 'nominal_voltage', str(230000) )

# insert auction and add recorder
auction_id, pos = glm.add_object(our_auction)
glm.add_recorder(auction_id, 'market.csv', period, ['current_market.clearing_price','current_market.clearing_quantity','current_price_mean_24h','current_price_stdev_24h', 'current_market.buyer_total_unrep', 'current_market.cap_ref_unrep', 'current_market.buyer_total_quantity'])

# insert bidders
for bidder in stub_bidders:
	bidder_id, pos = glm.add_object(bidder)



# find a meter to serve as reference for the market
id_meter = glm.find_neighbor(nn_id[0], 'class', 'meter')
#pdb.set_trace()
glm.add_recorder(id_meter, 'total_power_network_node.csv', period, ['measured_power','measured_real_power'])
name_meter = glm.read_attr( id_meter, 'name')

# modify the auction
#glm.modify_attr( auction_id, 'capacity_reference_object', name_meter )
glm.modify_attr( auction_id, 'capacity_reference_object',  'substation_transformer')
glm.modify_attr( auction_id, 'capacity_reference_property',  'power_out_real')

# remove regulator and the substation transformer
reg_id = glm.find_objects([['class', 'regulator']])
trans_id = glm.find_objects([['class', 'transformer'], ['name', 'substation_transformer']])

#pdb.set_trace()
glm.remove_link(reg_id)
#glm.remove_link(trans_id)



# Configure the controllers
controllers = glm.find_objects([['class', 'passive_controller']])
counter = 0
add_attr = True
for id in controllers:
	glm.modify_attr( id, 'name', 'passive_control_' + str(counter), add_attr )
	glm.modify_attr( id, 'period', str(period) )
	counter += 1

controllers = glm.find_objects([['class', 'controller']])
counter = 0
for id in controllers:
	glm.modify_attr( id, 'name', 'control_' + str(counter), add_attr )
	glm.modify_attr( id, 'period', str(period) )
	glm.modify_attr( id, 'bid_mode', 'ON' )
	glm.modify_attr( id, 'use_predictive_bidding', 'TRUE', add_attr )
	counter += 1

'''
# add recorders to the houses
houses = glm.find_objects([['class', 'house']])
for i in houses:
	parent_name = glm.read_attr(i, 'parent')[0]
	parent_id = glm.find_objects([['name', parent_name]])[0]
	#pdb.set_trace()
	glm.add_recorder(parent_id, 'meter_' + parent_name + '.csv', period, ['measured_power'])


# add recorder to the hvac
house_controller = -1
for i in houses:
	if house_controller >= 0:
		break
	child =  glm.read_attr(i, 'ID_child')
	if child == None:
		pdb.set_trace()
	for j in child:
		if glm.read_attr(j, 'class') == 'controller':
			house_controller = i
			break

#pdb.set_trace()

glm.add_recorder(house_controller, 'hvac.csv', period, ['hvac_load','hvac_duty_cycle','heating_setpoint','cooling_setpoint','air_temperature','outdoor_temperature'])
'''



'''
group_id = []
for i in houses:
	group_id.append( glm.read_attr(i, 'groupid') )

set_id = set(group_id)
elements = list(set_id)
count = np.zeros( len(elements) )

for i in range(len(group_id)):
	for j in range(len(elements)):
		count[j] += group_id[i] == elements[j]



pdb.set_trace()
'''


# collectors of values in the loads
collectors = '''
// commercial loads C1
object collector {
     group "class=meter AND groupid=Commercial_Meter";
     property avg(measured_power.mag);
     interval 300;
     file load_c1_p.csv;
}

object collector {
     group "class=meter AND groupid=Commercial_Meter";
     property avg(measured_voltage_A.mag),avg(measured_voltage_B.mag),avg(measured_voltage_C.mag),avg(nominal_voltage);
     interval 300;
     file load_c1_v.csv;
}


// Commercial loads C2
object collector {
     group "class=triplex_meter AND groupid=Commercial_Meter";
     property avg(measured_power.mag);
     interval 300;
     file load_c2_p.csv;
}

object collector {
     group "class=triplex_meter AND groupid=Commercial_Meter";
     property avg(measured_voltage_1.mag),avg(measured_voltage_2.mag),avg(nominal_voltage);
     interval 300;
     file load_c2_v.csv;
}


// Residential loads
object collector {
     group "class=triplex_meter AND groupid=Residential_Meter";
     property avg(measured_power.mag);
     interval 300;
     file load_r_p.csv;
}

object collector {
     group "class=triplex_meter AND groupid=Residential_Meter";
     property avg(measured_voltage_1.mag),avg(measured_voltage_2.mag),avg(nominal_voltage);
     interval 300;
     file load_r_v.csv;
}

'''





with open(model_output_tmp, 'w') as new_glm:
	new_glm.write(  header + clock + modules + weather_object + classes )
	
	glm.save_objects(new_glm)

	#new_glm.write( collectors )







#os.remove(model_output)
os.rename(model_output_tmp, model_output)


