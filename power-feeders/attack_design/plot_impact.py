import csv
import matplotlib.pyplot as plt
import numpy as np
import pdb
from datetime import datetime, date, time, timedelta
import matplotlib.dates as mdates

profit_seller_ideal = np.load('impact_ideal.npy')
profit_seller_targeted = np.load('impact_targeted.npy')
profit_seller_rand = np.load('impact_rand.npy')
time = np.load('time.npy')


m = len(time)

t1 = time[288*10]
t2 = time[-1]

plt.figure(9)
plt.clf()
plt.plot(time, profit_seller_ideal, label='Ideal case ')
plt.plot(time, profit_seller_targeted, label='Targeted selection')
plt.plot(time, profit_seller_rand, label='Random selection')

plt.plot(time, 0.5*np.ones(m),  label='Desired gains')
plt.title('Impact of an Attack')
plt.xlabel('time')
plt.ylabel('%')
#plt.xlim([t1, t2])
plt.legend()
plt.show()

plt.figure(8)
plt.clf()
plt.plot(time, profit_seller_ideal, label='Ideal case ')
plt.plot(time, profit_seller_targeted, label='Targeted selection')
plt.plot(time, profit_seller_rand, label='Random selection')

plt.plot(time, 0.5*np.ones(m),  label='Desired gains')
plt.title('Impact of an Attack')
plt.xlabel('time')
plt.ylabel('%')
plt.xlim([t1, t2])
plt.legend()
plt.show()

plt.savefig('attack_impact_cases.pgf', bbox_inches='tight')
