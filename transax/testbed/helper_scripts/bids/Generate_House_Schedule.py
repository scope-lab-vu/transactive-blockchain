import pandas
import numpy as np
import csv
import sys

#mFile = sys.argv[1] + '\\house_output.csv'
mFile = '../../outputs/house_output.csv'

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
    name = ((nameParts[0])[1] if len(nameParts[0]) == 2 else (nameParts[0])[2]) + '0' + nameParts[1]
    print(name)
    filename = './profiles/prosumer_' + name + '.csv'
    with open(filename, 'w', newline='') as csvfile:
        outwriter = csv.writer(csvfile, delimiter=',')
        outwriter.writerow(['startTime','endTime','energy'])
        for val in avgSeries:
            outwriter.writerow([i, i, -val])
            i = i + 1
