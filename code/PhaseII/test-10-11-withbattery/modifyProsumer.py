#!/usr/bin/python3
import os
import pandas as pd

# This script reads the data csv and scales the values so we can use them in the
# opal rt simualtion.

PATH=os.getcwd()+"/opal-data/"
PATH2=os.getcwd()+"/opal-data10x/"
for filename in os.listdir(PATH):
    print(filename)
    with open(PATH+filename) as f:
        df = pd.read_csv(f)
        print(df)
        df.loc[:,'energy'] *= 100
        print(df)
        df.to_csv(PATH2+filename, index=False)
