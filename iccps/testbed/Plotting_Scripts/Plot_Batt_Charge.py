import pandas
import numpy as np
import csv
import matplotlib.pyplot as plt
import sys
from pathlib import Path

mFile = Path(sys.argv[1] + "/battery_output.csv")

def strToComp(str):
    #print(type(row[1][1]))
    if str[0]=='+':
        return float(complex(str[1:]).real)
    else:
        return float(complex(str).real)

arr = pandas.read_csv(mFile, skiprows=7)
# print(arr)
# outSeries = arr[['# timestamp',10]]
outSeries = arr.iloc[:,range(10,19)]
rowAvg = outSeries.mean(axis=1)
# print(rowAvg)

#
avgSeries = rowAvg.groupby(np.arange(len(outSeries))//15).mean()
print(avgSeries)

#print(arr['network_node:distribution_load'])
print(avgSeries)
ax = avgSeries.plot(title='Average Battery Charge Level',legend=False, grid=True)
ax.set_xlabel('15 Minute Interval')
ax.set_ylabel('Charge Level (p.u.)')
ax.xaxis.set_ticks(np.arange(0,48,5))
# ax.yaxis.set_ticks(np.arange(-25000,25000,5000))
#arr.plot(y='network_node:distribution_load')
plt.show()
