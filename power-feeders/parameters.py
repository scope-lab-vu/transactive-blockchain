# parameters of the simulations
from datetime import datetime, date, time, timedelta

# define the time of the simulation
time_format = "%Y-%m-%d %H:%M:%S"

'''
# create historical data
# start time
start_t = '2009-06-01 00:00:00'

# finish time
finish_t = '2009-07-01 00:00:00'
'''

# Test data
# start time
start_t = '2009-07-01 00:00:00'

# finish time
finish_t = '2009-07-05 00:00:00'


# regular sims
# start time
#start_t = '2009-06-01 00:00:00'
#start_t = '2009-07-01 00:00:00'

# finish time
#finish_t = '2009-06-01 05:00:00'
#finish_t = '2009-06-01 20:00:00'
#finish_t = '2009-07-01 18:00:00'
#finish_t = '2009-06-10 00:00:00'
#finish_t = '2009-06-03 00:00:00'
#finish_t = '2009-06-06 00:00:00'
#finish_t = '2009-06-01 15:50:00'

t_0 = datetime.strptime( start_t, time_format)
t_f = datetime.strptime( finish_t, time_format)

# Period for the market and other elements
period_min = 5


# parameters of the generators
blocks = 25
max_capacity = 1500
#blocks = 50
#max_capacity = 1500
max_price = .63


dict_weather = {'AZ': 'AZ-Phoenix', 'CA': 'CA-San_francisco', 'FL': 'FL-Miami', 'HI': 'HI-Honolulu', 'IL': 'IL-Chicago', 'TN': 'TN-Nashville'}

weather = dict_weather['TN']



use_servermode = True

use_generator = False


attack_impact = 0.5

