# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 15:35:56 2017

@author: hanying.ong.2015
"""

import pandas as pd

import sqlite3

#### +Objective: sample size dataset for clustering #####################

################### overview network graph ######################

## output to json 

############### create generate dataset in dataframe #############

conn = sqlite3.connect('databases/foursquare_v3.db')
c = conn.cursor()

c.execute('SELECT * from venue_cluster_venuename')
results2 = c.fetchall()

df2 = pd.DataFrame(results2)

df2.columns = ['rid', 'uid', 'senti_score', 'senti_clus_id', 'name',
               'venue_type', 'venue_name']

df2 = df2.drop_duplicates() ## comment this line if there is no duplicate 

####################### create NODE DATASET ########################

nodes_df =  df2[['uid', 'name', 'senti_clus_id']].\
                drop_duplicates().reset_index(drop = True) ## user name and cluster

nodes_df2 = df2[['rid','venue_name']].drop_duplicates()\
                                      .reset_index(drop = True) ## restaurant name
nodes_df2['cluster_id'] = 100 ## restaurant cluster no. fixed at 100

nodes_df.columns = ['id', 'name', 'group'] #rename to have same name to combine
nodes_df2.columns = ['id', 'name', 'group'] #rename to have same name to combine

frames = [nodes_df , nodes_df2] ## combine
nodes_final_df = pd.concat(frames).reset_index(drop = True) ## combine
nodes_final_df['source'] = nodes_final_df.index  ## main dataset, with source and id

nodes_final_df2 = nodes_final_df[['name', 'group']] ## for db only
nodes_final_df2= nodes_final_df2.applymap(str)


nodes = []  #create dict for input later
for i in range (len(nodes_final_df2)):
    x = nodes_final_df2.iloc[i].to_dict()
    nodes.append(x)

####################### create Link DATAFRAME ########################

link_df =  df2[['uid', 'rid','name', 'venue_name', 'senti_score']].\
                drop_duplicates().reset_index(drop = True) ## relationship in names

nodes_user_df = nodes_final_df
nodes_user_df.columns = ['uid', 'name', 'group', 'source'] ## to merge with user id

link_df2 = link_df.merge(nodes_user_df, on = 'uid', how = 'left')                

nodes_resta_df = nodes_final_df
nodes_resta_df.columns = ['rid', 'name', 'group', 'source'] ## to merge with venue id

link_df3 = link_df2.merge(nodes_resta_df, on = 'rid', how = 'left')                

link_final_df = link_df3[['source_x', 'source_y', 'senti_score']]
link_final_df.columns = ['source', 'target', 'value']
link_final_df= link_final_df.applymap(str)

links = []
for i in range (len(link_final_df)):
    y = link_final_df.iloc[i].to_dict()
    links.append(y)
    
####################### combine both nto dataset ########################

dataset = {}
dataset[0] = nodes
dataset[1] = links

dataset['nodes'] = dataset.pop(0)
dataset['links'] = dataset.pop(1)

#################### export to json ##############################

import json

with open('overview_graph_dataset.json', 'w', encoding='utf-8') as outfile:  
    json.dump(dataset,outfile)
    outfile.close()










