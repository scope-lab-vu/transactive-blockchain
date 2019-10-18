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







# definition of the auxiliar auction object
auction_att = '''
object auction {
     name Market_att;
     period period**;
     special_mode NONE;
     unit kW;

     price_cap max_price**;
     init_price 0.15;
     init_stdev 0.05;

     //capacity_reference_object meter;
     //capacity_reference_property measured_real_power;

    warmup 0;
    //verbose 1;

    transaction_log_file log_file_att.csv;
    curve_log_file bid_curve_att.csv;
}
'''.replace('loop*', str(loop)).replace('max_price**', str(max_price)).replace('period**', str(period))


auction_ctrl = '''
object auction {
     name Market_ctrl;
     period period**;
     special_mode NONE;
     unit kW;

     //latency 10;

     price_cap max_price**;
     init_price 0.15;
     init_stdev 0.05;


     capacity_reference_object meter;
     capacity_reference_property measured_real_power;

    warmup 0;
    //verbose 1;

    transaction_log_file log_file_ctrl.csv;
    curve_log_file bid_curve_ctrl.csv;
}
'''.replace('loop*', str(loop)).replace('max_price**', str(max_price)).replace('period**', str(period))


auction_nominal = '''
object auction {
     name Market_nom;
     period period**;
     special_mode NONE;
     unit kW;

     //latency 10;

     price_cap max_price**;
     init_price 0.15;
     init_stdev 0.05;


     //capacity_reference_object meter;
     //capacity_reference_property measured_real_power;

    warmup 0;
    //verbose 1;

    transaction_log_file log_file_nom.csv;
    curve_log_file bid_curve_nom.csv;
}
'''.replace('loop*', str(loop)).replace('max_price**', str(max_price)).replace('period**', str(period))




# configure the Sellers
single_stub_bidder = '''
object stub_bidder{
	name block_x**;
	market market**;
	bid_period period**;
	count 32767;
	role SELLER;
	price price**;
	quantity quantity**;
}

'''.replace('loop*', str(loop)).replace('period**', str(period))


power_block = max_capacity/blocks
def cost(x):
	beta = max_price / (2 * max_capacity)
	return beta * x**2 

def dot_cost(x):
	beta = max_price / (2 * max_capacity)
	return 2 * beta * x



seller_bidders_att = []
seller_bidders_nom = []
for i in range(blocks):
	q = power_block * (i+1)
	p = dot_cost( q )
	bidder = single_stub_bidder
	bidder = bidder.replace('price**', str(p))
	bidder = bidder.replace('quantity**', str(power_block))

	bidder_a = bidder.replace('x**', 'att_' + str(1+i))
	bidder_a = bidder_a.replace('market**', 'Market_att')

	bidder_b = bidder.replace('x**', 'nom_' + str(1+i))
	bidder_b = bidder_b.replace('market**', 'Market_nom')

	seller_bidders_att.append( bidder_a )
	seller_bidders_nom.append( bidder_b )







# create the parser of the GLM file
glm = parser_GLM()
glm.create_list_elements(model_input)


####################################################
# reconfigure the market

# remove auctions and stub_bidders
#pdb.set_trace()
glm.find_and_remove([['type', 'object'], ['class', ['stub_bidder', 'auction', 'recorder'] ]])



# add auctions
attr_recorder = ['current_market.clearing_price','current_market.clearing_quantity','current_price_mean_1h','current_price_stdev_1h', 'current_market.buyer_total_unrep', 'current_market.cap_ref_unrep']


auction_att_id, pos = glm.add_object(auction_att)
glm.add_recorder(auction_att_id, 'market_att.csv', period, attr_recorder)


auction_ctrl_id, pos = glm.add_object(auction_ctrl)
glm.add_recorder(auction_ctrl_id, 'market_ctrl.csv', period, attr_recorder)

auction_nom_id, pos = glm.add_object(auction_nominal)
glm.add_recorder(auction_nom_id, 'market_nom.csv', period, attr_recorder)


glm.modify_attr( auction_ctrl_id, 'capacity_reference_object',  'substation_transformer')
glm.modify_attr( auction_ctrl_id, 'capacity_reference_property',  'power_out_real')




# find a meter to serve as reference for the market
nn_id = glm.find_objects([['class', 'meter'], ['name', 'network_node']])
id_meter = glm.find_neighbor(nn_id[0], 'class', 'meter')
name_meter = glm.read_attr( id_meter, 'name')

glm.add_recorder(id_meter, 'total_power_network_node.csv', period, ['measured_power','measured_real_power'])

# added this to force updates every minute
glm.add_recorder(id_meter, 'total_load.csv', '60', ['measured_real_power'])



# configure the controllers
controllers = glm.find_objects([ ['class', 'controller'] ])
for ctrl in controllers:
	try:
		glm.modify_attr(ctrl, 'use_predictive_bidding', 'False')
	except:
		pdb.set_trace()



# insert bidders of sellers

for bidder in seller_bidders_att:
	bidder_id, pos = glm.add_object(bidder)


for bidder in seller_bidders_nom:
	bidder_id, pos = glm.add_object(bidder)


# single bidder for the ctrl market
sell_bidder = '''
object stub_bidder{
	name seller_bid;
	market Market_ctrl;
	bid_period period**;
	count 32767;
	role SELLER;
	price 0;
	quantity 3000;
}
'''.replace('loop*', str(loop)).replace('period**', str(int(period/2)))

bidder_id, pos = glm.add_object(sell_bidder)

glm.add_recorder(bidder_id, 'price_offer.csv', '-1', ['price'])



# reconfigure passive controllers
id_passive_controllers = glm.find_objects([ ['class', 'passive_controller'] ])
for id_c in id_passive_controllers:
	glm.modify_attr(id_c, 'expectation_object', 'Market_nom')
	glm.modify_attr(id_c, 'observation_object', 'Market_nom')



# reconfigure controllers
id_controllers = glm.find_objects([ ['class', ['controller']] ])
for id_c in id_controllers:
	glm.modify_attr(id_c, 'market', 'Market_ctrl')




controller_bidders_att = []
controller_bidders_nom = []
for id_c in id_controllers:
	c_name = glm.read_attr( id_c, 'name')
	bidder = single_stub_bidder
	bidder = bidder.replace('price**', str(0))
	bidder = bidder.replace('quantity**', str(0))
	bidder = bidder.replace('SELLER', 'BUYER')

	bidder_a = bidder.replace('block_x**', 'att_bidder_' + c_name[0])
	bidder_a = bidder_a.replace('market**', 'Market_att')

	bidder_b = bidder.replace('block_x**', 'bidder_' + c_name[0])
	bidder_b = bidder_b.replace('market**', 'Market_nom')

	controller_bidders_att.append( bidder_a )
	controller_bidders_nom.append( bidder_b )



# insert bidders of the controllers

for bidder in controller_bidders_att:
	bidder_id, pos = glm.add_object(bidder)




for bidder in controller_bidders_nom:
	bidder_id, pos = glm.add_object(bidder)






# single bidder for the unresponsive loads
unresp_bidder = '''
object stub_bidder{
	name unresp_bidder_type**;
	market Market_type**;
	bid_period period**;
	count 32767;
	role BUYER;
	price 0;
	quantity 0;
}
'''.replace('loop*', str(loop)).replace('period**', str(int(period/2)))

unresp_bidder_att = unresp_bidder.replace('type**', 'att')
unresp_bidder_nom = unresp_bidder.replace('type**', 'nom')

#unresp_bidder_att_id, pos = glm.add_object(unresp_bidder_att)
unresp_bidder_nom_id, pos = glm.add_object(unresp_bidder_nom)






# add recorders to some objects
'''
id_bidder_att = glm.find_objects([ ['class', ['stub_bidder']], ['name', 'att_bidder_control_2'] ])
id_bidder_nom = glm.find_objects([ ['class', ['stub_bidder']], ['name', 'bidder_control_2'] ])

glm.add_recorder(id_bidder_att[0], 'ctrl_bidder_att.csv', -1, ['price', 'quantity'])
glm.add_recorder(id_bidder_nom[0], 'ctrl_bidder_nom.csv', -1, ['price', 'quantity'])


id_ctrl = glm.find_objects([ ['class', ['controller']], ['name', 'control_2'] ])
glm.add_recorder(id_ctrl[0], 'ctrl.csv', -1, ['bid_price', 'bid_quantity', 'state'])



sub_tr_id = glm.find_objects([['name', 'substation_transformer']])
glm.add_recorder(sub_tr_id, 'sub_tr.csv', period, ['power_out_real'])


glm.add_recorder(unresp_bidder_att_id, 'unresp_bidder_att.csv', period, ['price', 'quantity'])
glm.add_recorder(unresp_bidder_nom_id, 'unresp_bidder_nom.csv', period, ['price', 'quantity'])
'''


# reconfigure the  meters
id_meters = glm.find_objects([ [ 'class', ['meter', 'triplex_meter'] ] ])
for id_m in id_meters:
	glm.modify_attr(id_m, 'power_market', 'Market_nom')





with open(model_output_tmp, 'w') as new_glm:

 
	glm.save_directives(new_glm)

	# insert the clock
	id_clock = glm.find_objects([['type', 'clock']])
	n = len(glm.list_objects)
	set_elements = set( range(n) )
	raw_clock, set_elements = glm.read_object( id_clock[0], set_elements )
	#pdb.set_trace()

	new_glm.write( raw_clock )

	glm.remove_objects(id_clock)


	glm.save_modules(new_glm)
	glm.save_objects(new_glm)






#os.remove(model_output)
os.rename(model_output_tmp, model_output)


