import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import matplotlib.dates as mdates


case = 'attack_1'
case = 'attack_2'

stats_exp = np.load('stats_'+case+'.npy')

mean_profit = [ exp['avg'] for exp in stats_exp ]
std_profit = [ exp['std'] for exp in stats_exp ]

# mitigation
x = [0, 0.2, 0.4, 0.6, 0.8]

plt.figure(9)
plt.clf()
plt.errorbar(x, mean_profit, std_profit, linestyle='None', marker='s')
plt.show()



