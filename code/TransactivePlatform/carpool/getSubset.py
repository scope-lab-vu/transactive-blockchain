#!/usr/bin/python3
import os
import pandas as pd
import numpy as np

#-----CHECK THAT FILES EXIST AND READ THEM------------
cwd = os.getcwd()
print(os.path.exists('data/Davidson_TAZ_full.csv'))
Davidson_TAZ_full_df = pd.read_csv("data/Davidson_TAZ_full.csv")
worker_flows_df = pd.read_csv("data/Worker_flows.csv")
#------------------------------------------------------

#----GET ALL ROUTES WITH RESIDENCE IN DAVIDSON -------
Davidson_GEOID_df = Davidson_TAZ_full_df.loc[:,'GEOID']
#print(Davidson_GEOID_df)
Davidson_TAZ_df = (Davidson_GEOID_df.iloc[0::10]).map(lambda GEOID: GEOID.split("_")[0])
#print(Davidson_TAZ_df)

work_flows_Davidson_df = worker_flows_df[worker_flows_df['Residence'].isin(Davidson_TAZ_df)]
print(work_flows_Davidson_df)
print(work_flows_Davidson_df.shape)
#-----------------------------------------------------


# departure time
# providing (true/false)
# seats available/required
# value = 0
