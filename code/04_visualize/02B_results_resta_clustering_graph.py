# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 15:35:56 2017

@author: hanying.ong.2015
"""

import pandas as pd

import sqlite3


#### +Objective: to generate dataset for sample size - clustering  #######

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

g99 = df2[(df2.senti_clus_id == 99)]
g99_10records  = g99.iloc[0:25]

df2 = df2.drop_duplicates() ## comment this line if there is no duplicate 

#df3 = df2[(df2.senti_clus_id == 0)] #cluster 0
#df3 = df3.iloc[0:25]
#
#df4 = df2[(df2.senti_clus_id == 2)] #cluster 2
#df4 = df4.iloc[0:25]
#
df5 = df2[(df2.senti_clus_id == 3)] #cluster 3

df5_count  = df5.groupby(['venue_name']).agg(['count'])
df5_count = pd.DataFrame(df5_count.iloc[:,0])
df5_count['venue_name'] = df5_count.index
df5_count['total_count'] = df5_count.iloc[:,0]
df5_count.columns = ['temp', 'venue_name', 'total_count']
df5_count =df5_count.drop('temp', axis = 1).\
                    sort_values('total_count', ascending = False).\
                    reset_index(drop = True)
df5_top15 = df5_count.iloc[0:15,]          

df5 = df5[df5['venue_name'].isin(df5_top15['venue_name'])].\
                                sort_values('name').\
                                reset_index(drop = True)

df5_user_count =  df5.groupby(['name']).agg(['count'])   
df5_user_count =  pd.DataFrame(df5_user_count.iloc[:,0])
df5_user_count['name'] = df5_user_count.index
df5_user_count['total_count'] = df5_user_count.iloc[:,0]
df5_user_count.columns = ['temp', 'name', 'total_count']
df5_user_count =df5_user_count.drop('temp', axis = 1).\
                    sort_values('total_count', ascending = False).\
                    reset_index(drop = True)
df5_top20 = df5_user_count.iloc[0:20,]   

df5 = df5[df5['name'].isin(df5_top20['name'])].\
                                reset_index(drop = True)
       
################################################################

df6 = df2[(df2.senti_clus_id == 4)] #cluster 3

df6_count  = df6.groupby(['venue_name']).agg(['count'])
df6_count = pd.DataFrame(df6_count.iloc[:,0])
df6_count['venue_name'] = df6_count.index
df6_count['total_count'] = df6_count.iloc[:,0]
df6_count.columns = ['temp', 'venue_name', 'total_count']
df6_count =df6_count.drop('temp', axis = 1).\
                    sort_values('total_count', ascending = False).\
                    reset_index(drop = True)
df6_top15 = df6_count.iloc[0:15,]          

df6 = df6[df6['venue_name'].isin(df6_top15['venue_name'])].\
                                sort_values('name').\
                                reset_index(drop = True)

df6_user_count =  df6.groupby(['name']).agg(['count'])   
df6_user_count =  pd.DataFrame(df6_user_count.iloc[:,0])
df6_user_count['name'] = df6_user_count.index
df6_user_count['total_count'] = df6_user_count.iloc[:,0]
df6_user_count.columns = ['temp', 'name', 'total_count']
df6_user_count =df6_user_count.drop('temp', axis = 1).\
                    sort_values('total_count', ascending = False).\
                    reset_index(drop = True)
df6_top20 = df6_user_count.iloc[0:20,]   

df6 = df6[df6['name'].isin(df6_top20['name'])].\
                                reset_index(drop = True)


frames = [g99_10records,df5,df6] ## combine
df2 = pd.concat(frames).reset_index(drop = True) ## combine
           

####################### create NODE DATASET ########################
import numpy as np

nodes_df =  df2[['uid', 'name', 'senti_clus_id']].\
                drop_duplicates().reset_index(drop = True) ## user name and cluster

nodes_df2 = df2[['rid','venue_name']].drop_duplicates()\
                                      .reset_index(drop = True) ## restaurant name
nodes_df2['cluster_id'] = np.arange(1000,1000+len(nodes_df2),1)
##nodes_df2['cluster_id'] = 1000


nodes_df.columns = ['id', 'name', 'group'] #rename to have same name to combine
nodes_df2.columns = ['id', 'name', 'group'] #rename to have same name to combine

frames = [nodes_df , nodes_df2] ## combine
nodes_final_df = pd.concat(frames).reset_index(drop = True) ## combine
nodes_final_df['source'] = nodes_final_df.index  ## main dataset, with source and id

nodes_final_df2 = nodes_final_df[['name', 'group']] ## for db only
##nodes_final_df2= nodes_final_df2.applymap(str)


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
##link_final_df= link_final_df.applymap(str)
##link_final_df['value'] = 1

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
import numpy as np

def default(o):

    if isinstance(o, np.integer): return int(o)
    raise TypeError

with open('overview_graph_dataset_sample.json', 'w', encoding='utf-8') as outfile:  
    json.dump(dataset,outfile, default=default)
    outfile.close()








