

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 15:35:56 2017

@author: hanying.ong.2015
"""

import pandas as pd

import sqlite3


################### overview network graph - general ######################

## open database_v3
conn = sqlite3.connect('databases/foursquare_v3.db')
c = conn.cursor()

c.execute('SELECT * from venue_cluster_venuename')
results2 = c.fetchall()

df2 = pd.DataFrame(results2)

df2.columns = ['rid', 'uid', 'senti_score', 'senti_clus_id', 'name',
               'venue_type', 'venue_name']

df2 = df2.drop_duplicates()

## df2.to_csv('overview_networkgraph_v2_.csv', sep = ',')





















