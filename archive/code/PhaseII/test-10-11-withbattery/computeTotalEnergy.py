#!/usr/bin/python3
import os
import pandas as pd

# This script reads the data csv and scales the values so we can use them in the
# opal rt simualtion.

PATH=os.getcwd()+"/all_data/"
PATH2=os.getcwd()
producers = 0
production = 0
consumers = 0
consumption = 0
for filename in os.listdir(PATH):
    #print(filename)
    with open(PATH+filename) as f:
        df = pd.read_csv(f)
        print(df)
        break
        energy = df.loc[:,'energy'].sum()
        #print(energy)
        if energy >= 0 :
            production += energy
            producers += 1
        else:
            consumption += energy
            consumers +=1
print("production, {}".format(production))
print("producers %s" %(producers))
print("consumption, {}".format(consumption))
print("consumers, %s" %(consumers))
print(production)
print(producers)
print(consumption)
print(consumers)

filename = "output.csv"
print(df)
df.to_csv(filename, index=False)
