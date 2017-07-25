# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 05:33:04 2017

@author: hanying.ong.2015
"""

import pandas as pd

import sqlite3

#### +Objective: sample size dataset for location clustering  for visualization ###


################### overview network graph ######################

## output to json 

############### create generate dataset in dataframe #############

conn = sqlite3.connect('databases/foursquare_v4.db')
c = conn.cursor()

c.execute('SELECT uid, mrt_loc_clus_id from users')
results2 = c.fetchall()

df = pd.DataFrame(results2)

df.columns = ['uid', 'loc_clus_id']

df.to_csv('user_location_clus.csv', sep = ',')
