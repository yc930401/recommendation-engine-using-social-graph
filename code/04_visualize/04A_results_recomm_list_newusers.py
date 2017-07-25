# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 21:46:35 2017

@author: hanying.ong.2015
"""

##################### to generate sample dataset for recommending new users ##########

import pandas as pd

user_name_df = pd.read_csv('user_name.csv', sep = '\t').drop('Unnamed: 0', axis = 1)
recommendation_df = pd.read_csv('recom_for_new_user.csv', sep = '\t').drop('Unnamed: 0', axis = 1)
friend_list_df = pd.read_csv('friend_list.csv', sep = '\t').drop('Unnamed: 0', axis = 1)


################## count friend list ###########

top_N_friends = friend_list_df.groupby('users').agg(['count'])
top_N_friends['users'] = top_N_friends.index
top_N_friends['total_friends'] = top_N_friends.iloc[:,0]

top_N_friends = top_N_friends[['users', 'total_friends']]
top_N_friends.columns =['users', 'total_friends']
top_N_friends = top_N_friends.sort_values('total_friends', ascending = False).reset_index(drop=True)


top_N_friends= top_N_friends.applymap(str)
top_N_friends['total_friends'] = top_N_friends['total_friends'].convert_objects(convert_numeric=True)
#top_N_friends_selected = \
#        top_N_friends[(top_N_friends.total_friends <20) & \
#                      (top_N_friends.total_friends>15)]
        
top_N_friends_selected = \
       top_N_friends[(top_N_friends.total_friends >300)]
       
top_N_friends_selected_5 = top_N_friends_selected.iloc[0:1]

user_friends_selected = friend_list_df[friend_list_df['users'].\
                                       isin(top_N_friends_selected_5['users'])]

################################create node file ###############################

user_name_node = user_friends_selected[['uid', 'users']].drop_duplicates().reset_index(drop = True)
friend_node = user_friends_selected[['friend_uid', 'friend_name']].\
            drop_duplicates().reset_index(drop = True)
            
friend_node = friend_node.rename(columns = {'friend_uid':'uid'})  

friend_node = friend_node.merge(user_name_df, on = 'uid', how = 'left') 
    
top_N_friend_cluster = friend_node.groupby('combined_clus_id').agg(['count'])
top_N_friend_cluster['combined_clus_id'] = top_N_friend_cluster.index
top_N_friend_cluster['total_count'] = top_N_friend_cluster.iloc[:,0]
top_N_friend_cluster = top_N_friend_cluster.iloc[:,3:5]
top_N_friend_cluster.columns = ['combined_clus_id', 'count']
top_N_friend_cluster = top_N_friend_cluster.sort_values('count', ascending = False).reset_index(drop = True)

top_N_friend_cluster_selected = top_N_friend_cluster.iloc[0:5]
top_N_friend_cluster_selected['group'] = top_N_friend_cluster_selected.index
               
friend_node_selected =  friend_node[friend_node['combined_clus_id'].\
                                    isin(top_N_friend_cluster_selected['combined_clus_id'])]           
            
            
FORUSE_friend_list = user_friends_selected[user_friends_selected['friend_uid'].isin\
                                           (friend_node_selected['uid'])]  

friend_node = friend_node_selected.merge(top_N_friend_cluster_selected, on = 'combined_clus_id', how = 'left') 
            
node_group = friend_node[['name', 'group']]  
node_group_user = user_name_node.iloc[0:1]  
node_group_user['group'] = 1000    
node_group_user = node_group_user[['users', 'group']]       
node_group_user.columns = ['name', 'group']           

frames = [node_group , node_group_user] ## combine
nodes_final_df = pd.concat(frames).reset_index(drop = True) ## combine
nodes_final_df['source'] = nodes_final_df.index  ## main dataset, with source and id
nodes_final_df2 = nodes_final_df[['name', 'group']] ## for db only

nodes = []  #create dict for input later
for i in range (len(nodes_final_df2)):
    x = nodes_final_df2.iloc[i].to_dict()
    nodes.append(x)
            
#######################
FORUSE_friend_list.columns = ['uid','friend_uid', 'users', 'name']

FORUSE_friend_list_v1 = FORUSE_friend_list.merge(nodes_final_df, on = 'name', how = 'left')  
            
FORUSE_friend_list_v1.columns = ['uid','friend_uid','name', 'friend_name','group','target']           

FORUSE_friend_list_v2 = FORUSE_friend_list_v1.merge(nodes_final_df, on = 'name', how = 'left')

links_df = FORUSE_friend_list_v2[['source', 'target']]
links_df ['value'] = 1

links = []
for i in range (len(links_df)):
    y = links_df.iloc[i].to_dict()
    links.append(y)
    
#######################################################

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

with open('new_user_recommendation.json', 'w', encoding='utf-8') as outfile:  
    json.dump(dataset,outfile, default=default)
    outfile.close()

###################################################################

#### recommendation list

dataset_for_new_recommendation = recommendation_df[\
                                                   recommendation_df['name'].\
                                                   isin(node_group_user['name'])]

dataset_for_new_recommendation.to_csv\
('dataset_for_new_recommendation.csv', header = True, index= True, sep='\t', encoding='utf-8')
        