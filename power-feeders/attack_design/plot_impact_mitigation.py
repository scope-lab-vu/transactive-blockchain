import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import matplotlib.dates as mdates


# case = 'attack_1'
case = 'attack_2'

stats_exp = np.load('stats_'+case+'.npy', allow_pickle=True)

mean_profit = [ exp['avg']*100 for exp in stats_exp ]
std_profit = [ exp['std']*100 for exp in stats_exp ]

# mitigation
x = [0, 20, 40, 60, 80]



plt.figure(9)
plt.clf()
plt.errorbar(x, mean_profit, std_profit, linestyle='None', marker='s')
plt.xlabel('Mitigation Rate [%]')
plt.ylabel('Profit [%]') 
plt.ylim(-15,40)
plt.show()



plt.savefig('%s.pgf'%case, bbox_inches='tight')

