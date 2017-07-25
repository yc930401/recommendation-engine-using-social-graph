# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 21:42:46 2017

@author: hanying.ong.2015
"""

#### +Objective: sample size dataset for existing recommendation for visualization ###

########################### generate sample size data for visualization ###########

import pandas as pd

user_name_df = pd.read_csv('user_name.csv', sep = '\t').drop('Unnamed: 0', axis = 1)
recommendation_df = pd.read_csv('recom_for_existing_user.csv', sep = '\t').drop('Unnamed: 0', axis = 1)


dataset_for_existing_recommendation = recommendation_df.merge\
                                        (user_name_df , on = 'uid', how = 'left') 
                                        
dataset_for_existing_recommendation = dataset_for_existing_recommendation.drop\
                                        ('name_x', axis = 1)

dataset_for_existing_recommendation = \
                            dataset_for_existing_recommendation.rename\
                            (columns = {'name_y':'name'})
                            
dataset_for_existing_recommendation.to_csv\
('dataset_for_existing_recommendation.csv', header = True, index= True, sep='\t', encoding='utf-8')


dataset_existing_user = dataset_for_existing_recommendation[dataset_for_existing_recommendation['uid'].isin(user_name_df['uid'])]
                            
dataset_existing_user = dataset_existing_user[['name','senti_clus_id', 'venue_clus_id', 'mrt_loc_clus_id']]

dataset_existing_user= dataset_existing_user.applymap(str)


dataset_existing_user.to_csv\
('dataset_existing_user.csv', header = True, index= True, sep='\t', encoding='utf-8')
