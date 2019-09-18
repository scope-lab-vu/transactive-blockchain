import pandas
import numpy as np
import csv
import sys

# mFile = sys.argv[1] + '\\solar_output.csv'
mFile = '../../outputs/solar_output.csv'

def strToComp(str):
    #print(type(row[1][1]))
    if str[0]=='+':
        return float(complex(str[1:]).real)
    else:
        return float(complex(str).real)

arr = pandas.read_csv(mFile, skiprows=7)
arr = arr.drop('# timestamp', axis=1)
# arr.applymap(lambda x: float(x))
# outSeries.resample('15m').mean()
# avgSeries = outSeries.groupby(np.arange(len(outSeries))//15).mean()
columns = list(arr)
for col in columns:
    i = 0
    avgSeries = arr[col].groupby(np.arange(len(arr[col]))//15).mean()
    nameParts= col.split('_')[0].split('m')
    name = (nameParts[0])[1:2] + '0' + nameParts[1]
    filename = './profiles/prosumer_' + name + '.csv'
    with open(filename, 'w', newline='') as csvfile:
        outwriter = csv.writer(csvfile, delimiter=',')
        outwriter.writerow(['startTime','endTime','energy'])
        for val in avgSeries:
            outwriter.writerow([i, i, -val/1000])
            i = i + 1
