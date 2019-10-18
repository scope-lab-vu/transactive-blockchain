import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import matplotlib.dates as mdates



from functions_auction import build_curves, find_equilibrium_auction, extract_bids, order_bids_descending, order_bids_ascending, find_market_equilibrium, surplus_f, ideal_eq_attack, maer, avg_total_surplus, stats

from functions_read_data import read_data, rolling_statistics, get_avg_data



time_format = "%Y-%m-%d %H:%M:%S"
time_format_b = "%Y-%m-%d %H:%M:%S.%f"

model = 'R1_1247_3_t6_small'
#folder = './simulations/' + model + '/nominal/'
#stats = 'current_price_mean_24h'


#folder = './simulations/' + model + '/nominal_24h_1month/'
#stats = 'current_price_mean_24h'

#folder = './simulations/' + model + '/nominal_1h_1month/'
#stats = 'current_price_mean_1h'


#folder_nom = '../simulations/' + model + '/nominal_test/'
#folder_att = '../simulations/' + model + '/delay_attack/'


case = 'ideal'
folder_nom = '../simulations/' + model + '/nominal_test_1h_b/'
folder_att = '../simulations/' + model + '/delay_attack_ideal/'
stats = 'current_price_mean_1h'




# name of the data files
load = 'total_power_network_node.csv'

market = 'market_ctrl.csv'

# extract the total load
data_substation = read_data( folder_nom + load)
data_market = read_data( folder_nom + market)


data_substation_att = read_data( folder_att + load)
data_market_att = read_data( folder_att + market)




plt.figure(1)
plt.clf()
plt.plot(data_market['time'], data_market['current_market.clearing_price'], label='clearing price')
plt.plot(data_market['time'], data_market[stats], '--', label='price stats')

plt.plot(data_market_att['time'], data_market_att['current_market.clearing_price'], label='clearing price att')
plt.plot(data_market_att['time'], data_market_att[stats], '--', label='price stats att')
plt.title('Price')

plt.legend()
plt.show()




plt.figure(2)
plt.clf()
plt.plot(data_substation['time'], data_substation['measured_real_power']/1000, label='Load')
plt.plot(data_substation_att['time'], data_substation_att['measured_real_power']/1000, label='Load att')
plt.legend()
plt.title('Total_load')
plt.show()





# get thre bids with and without attacks
eq_time, market_eq, bids, curves = find_market_equilibrium(folder_nom + 'bids_log.csv')

eq_time_nom, market_eq_nom, bids_nom, curves_nom = find_market_equilibrium(folder_att + 'bids_log_nom.csv')

eq_time_att, market_eq_att, bids_att, curves_att = find_market_equilibrium(folder_att + 'bids_log.csv')


price_stats = rolling_statistics(eq_time, market_eq['p'], 60)
price_stats_nom = rolling_statistics(eq_time_nom, market_eq_nom['p'], 60)
price_stats_att = rolling_statistics(eq_time_att, market_eq_att['p'], 60)

'''
plt.figure(3)
plt.clf()
plt.plot(eq_time, market_eq['p'], label='No attack')
plt.plot(eq_time_nom, market_eq_nom['p'], label='Nominal')
plt.plot(eq_time_att, market_eq_att['p'], label='Attack')
plt.title('Market Price')
plt.legend()
plt.show()
'''

plt.figure(3)
plt.clf()
plt.plot(price_stats['time'], price_stats['mean'], label='No attack')
plt.plot(price_stats_nom['time'], price_stats_nom['mean'], label='Nominal')
plt.plot(price_stats_att['time'], price_stats_att['mean'], label='Attack')
plt.title('Market Price')
plt.legend()
plt.show()





surplus = surplus_f(bids, market_eq)
surplus_nom = surplus_f(bids_nom, market_eq_nom)
surplus_att = surplus_f(bids_nom, market_eq_att)


# this is the cost of energy according to the market, not the real one!
def cost_users_a(market_eq):
	p_eq = market_eq['p']
	q_eq = market_eq['q']
	return p_eq * q_eq

def cost_users(market_eq, data_substation):
	p_eq = market_eq['p']
	q_eq = market_eq['q']
	load = data_substation['measured_real_power'][1:]/1000
	return p_eq * abs(load)


total_cost_energy = cost_users_a(market_eq)
total_cost_energy_nom = cost_users_a(market_eq_nom)
total_cost_energy_att = cost_users_a(market_eq_att)


'''
total_cost_energy = cost_users(market_eq, data_substation)
total_cost_energy_nom = cost_users(market_eq_nom, data_substation_att)
total_cost_energy_att = cost_users(market_eq_att, data_substation_att)
'''

'''
plt.figure(4)
plt.clf()
#plt.plot(eq_time, surplus['customer'], label='No attack')
#plt.plot(eq_time_nom, surplus_nom['customer'], label='Nominal')
#plt.plot(eq_time_att, surplus_att['customer'], label='Attack')

plt.plot(eq_time, total_cost_energy, label='No attack')
plt.plot(eq_time, total_cost_energy_nom, label='nominal')
plt.plot(eq_time, total_cost_energy_att, label='attack')

plt.title('Customer cost')
plt.legend()
plt.show()

plt.figure(5)
plt.clf()
plt.plot(eq_time, surplus['seller'], label='No attack')
plt.plot(eq_time_nom, surplus_nom['seller'], label='Nominal')
plt.plot(eq_time_att, surplus_att['seller'], label='Attack')
plt.title('Seller surplus')
plt.legend()
plt.show()
'''
'''
for k in range(len(eq_time_att)):
	if eq_time[k] != eq_time_nom[k]:
		print(k)
		print(eq_time[k])
		print(eq_time_nom[k])
		print()
		pdb.set_trace()
'''


profit_buyer = (surplus_att['customer'] - surplus['customer']) /  surplus['customer']
avg_profit_buyer = np.mean(profit_buyer)

cost_buyer = ( total_cost_energy_att - total_cost_energy ) / total_cost_energy
avg_cost_buyer = np.mean( cost_buyer )


profit_seller_a = ( surplus_att['seller'] - surplus['seller'] ) / surplus['seller']
rolling_stats_seller = rolling_statistics(eq_time, profit_seller_a, 60)

profit_seller = rolling_stats_seller['mean']
time_stats = rolling_stats_seller['time']

avg_profit_seller = np.mean(profit_seller)
std_profit_seller = np.std(profit_seller)
max_profit_seller = np.max(profit_seller)
min_profit_seller = np.min(profit_seller)

# 
np.save('impact_'+case+'.npy', profit_seller)
np.save('time.npy', time_stats)



print('avg profit buyer: ' + str(avg_profit_buyer ))
print('avg cost buyer: ' + str(avg_cost_buyer ))
print('avg profit seller: ' + str(avg_profit_seller ))


print('std profit seller: '+ str(std_profit_seller) )
print('max profit seller: '+ str(max_profit_seller) )
print('min profit seller: '+ str(min_profit_seller) )




'''
plt.figure(6)
plt.clf()
#plt.plot(eq_time, profit_buyer, label='profit buyer')
plt.plot(eq_time, cost_buyer, label='cost buyer')
plt.plot(eq_time, profit_seller, label='profit seller')
plt.title('Impact an attack')
plt.legend()
plt.show()
'''



# rolling statistics
stats_seller = rolling_statistics(eq_time, profit_seller, 60)
stats_buyer = rolling_statistics(eq_time, cost_buyer, 60)

plt.figure(7)
plt.clf()
plt.plot(stats_seller['time'], stats_seller['mean'], label='profit seller')
plt.plot(stats_buyer['time'], stats_buyer['mean'], label='cost buyer')
plt.title('Impact an attack (rolling stats)')
plt.legend()
plt.show()



###################################################################################
# profit increment
profit_ratio = surplus_att['seller'] / surplus['seller']
profit_ratio_stats = rolling_statistics(eq_time, profit_ratio, 60)
avg_profit_ratio = np.mean( profit_ratio )

print('Profit ratio: ' + str(avg_profit_ratio))

m = len(profit_ratio_stats['time'])

plt.figure(8)
plt.clf()
#plt.plot(eq_time, profit_ratio, label='profit ratio')
plt.plot(profit_ratio_stats['time'], profit_ratio_stats['mean'] - 1, label='Profit increment')

plt.plot(profit_ratio_stats['time'], 0.5*np.ones(m),  label='Desired increment')
plt.title('Impact of an attack')
plt.xlabel('time')
plt.ylabel('%')
plt.legend()
plt.show()



###################################################################
# profit increment
profit_ratio_rel = surplus_att['seller'] / surplus_nom['seller']
profit_ratio_rel_stats = rolling_statistics(eq_time, profit_ratio_rel, 60)
avg_profit_ratio = np.mean( profit_ratio_rel )

print('Profit ratio relative: ' + str(avg_profit_ratio))

m = len(profit_ratio_stats['time'])

plt.figure(9)
plt.clf()
#plt.plot(eq_time, profit_ratio, label='profit ratio')
plt.plot(profit_ratio_rel_stats['time'], profit_ratio_rel_stats['mean'] - 1, label='Profit increment')

plt.plot(profit_ratio_stats['time'], 0.5*np.ones(m),  label='Desired increment')
plt.title('Impact of an attack relative')
plt.xlabel('time')
plt.ylabel('%')
plt.legend()
plt.show()




############################################
# error in the attack

periods = int(24*60/5)

# load desired impact
q_a_op = np.load('../desired_q.npy', allow_pickle=True)
q_a = market_eq_att['q']

error_q = []
for k in range(len(q_a)):
	tau = k % periods
	error_q.append( q_a_op[tau] - q_a[k] )
error_q = np.array(error_q)

plt.figure(10)
plt.clf()
plt.plot(error_q/10.0)
plt.show()


