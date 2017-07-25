######################### fro JQ to get ID for recommendations  ###########################

import pickle
import sqlite3

db_path = './data/foursquare.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

recs = pickle.load(open('./data/rec_results/recs_full_venue.sav', 'rb'))

# get top 10 recs
top_10_rec_dict = {}

for key,value in recs.items():
    uid = key
    top_10_rec = value[1][0:10]
    top_10_rec_dict[uid] = top_10_rec

# get recs using history
recs_using_self_history = {}
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) >= 3")
hist_recommend_users = c.fetchall()

for u in hist_recommend_users:
    uid = u[0]
    recs_using_self_history[uid] = recs[uid]

# get recs using friends
recs_using_friends = {}
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) < 3")
frd_recommend_users = c.fetchall()

for usr in frd_recommend_users:
    uid = usr[0]
    recs_using_friends[uid] = recs[uid]


# use
recs_using_friends
recs_using_self_history

###########################################################################################
######################### to get the dataset for visualization ############################
###########################################################################################

## objective 1 : to return 20 recommendations for eaach user from both tables

## objective 2 : to get friends' friend table - to plot network graph 

# objective 3 : to get users and its respective 3 cluster no, for parallel set

## step 1 - get IDs and Names

import pandas as pd

#################################### user name master db #############################

c.execute('SELECT uid, first_name,last_name, senti_clus_id, venue_clus_id, mrt_loc_clus_id from users')
user_id = c.fetchall()

user_id_df = pd.DataFrame(user_id)
user_id_df.columns = ['uid', 'first_name','last_name','senti_clus_id', 'venue_clus_id', 'mrt_loc_clys_id']

master_user_name = pd.DataFrame(user_id_df['uid'])
master_user_name['name'] = user_id_df.first_name + ' ' + user_id_df.last_name
master_user_name['senti_clus_id'] = user_id_df['senti_clus_id'] 
master_user_name['venue_clus_id'] = user_id_df['venue_clus_id'] 
master_user_name['mrt_loc_clus_id'] = user_id_df['mrt_loc_clys_id'] 
master_user_name = master_user_name.sort_values('uid').reset_index(drop = True)

#################################### resta name master db #############################
c.execute('SELECT rid, venue_name from venues')
resta_id = c.fetchall()

master_resta = pd.DataFrame(resta_id)
master_resta.columns = ['rid', 'venue_name']

######################## get friends' friends' list ###################################
c.execute('SELECT uid, friend_uid from user_friends')
user_friend_id = c.fetchall()

user_friend_id_df= pd.DataFrame(user_friend_id)
user_friend_id_df.columns = ['uid', 'friend_uid']

### df1.merge(df2[['MODEL', 'MAKE']], how = 'left')

user_friend = user_friend_id_df.merge(master_user_name[['uid','name']], how = 'left')
user_friend.columns = ['user_id', 'uid', 'user_name']

friend_list = user_friend.merge(master_user_name[['uid','name']], how = 'left')
friend_list.columns = ['uid', 'users', 'friend_uid', 'friend_name']

select_top_N = 20 ## can be modified 

top_N_friends = friend_list.groupby('users').agg(['count'])
top_N_friends['users'] = top_N_friends.index
top_N_friends['total_friends'] = top_N_friends.iloc[:,0]

master_top_N_friends_list = top_N_friends[['users', 'total_friends']]
master_top_N_friends_list.columns =['users', 'total_friends']
master_top_N_friends_list = master_top_N_friends_list.sort_values('total_friends', ascending = False).reset_index(drop=True)

######################## get existing users, recommendation ###################################

## recs_using_self_history

select_top_N_recommendation = 20

master_recom_list_existing = []

## for i in range(len(recs_using_self_history)):

for key in recs_using_self_history.items():
    temp_user_list =[]
    temp_user_id= key[0]
    temp_user_list.append(temp_user_id)
                
    temp_recent_visit = key[1][0]
    temp_user_list.append(temp_recent_visit)
            
    temp_recommendation_01 = key[1][1][0]
    temp_user_list.append(temp_recommendation_01)
    
    try:        
        temp_recommendation_02 = key[1][1][1]
        temp_user_list.append(temp_recommendation_02)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_03 = key[1][1][2]
        temp_user_list.append(temp_recommendation_03)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_04 = key[1][1][3]
        temp_user_list.append(temp_recommendation_04)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_05 = key[1][1][4]
        temp_user_list.append(temp_recommendation_05)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_06 = key[1][1][5]
        temp_user_list.append(temp_recommendation_06)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_07 = key[1][1][6]
        temp_user_list.append(temp_recommendation_07)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_08 = key[1][1][7]
        temp_user_list.append(temp_recommendation_08)
    except IndexError:
        temp_user_list.append("NA")
     
    try:
        temp_recommendation_09 = key[1][1][8]
        temp_user_list.append(temp_recommendation_09)
    except IndexError:
        temp_user_list.append("NA")
       
    try:
        temp_recommendation_10 = key[1][1][9]
        temp_user_list.append(temp_recommendation_10)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_11 = key[1][1][10]
        temp_user_list.append(temp_recommendation_11)
    except IndexError:
        temp_user_list.append("NA")

    try:
        temp_recommendation_12 = key[1][1][11]
        temp_user_list.append(temp_recommendation_12)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_13 = key[1][1][12]
        temp_user_list.append(temp_recommendation_13)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_14 = key[1][1][13]
        temp_user_list.append(temp_recommendation_14)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_15 = key[1][1][14]
        temp_user_list.append(temp_recommendation_15)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_16 = key[1][1][15]
        temp_user_list.append(temp_recommendation_16)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_17 = key[1][1][16]
        temp_user_list.append(temp_recommendation_17)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_18 = key[1][1][17]
        temp_user_list.append(temp_recommendation_18)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_19 = key[1][1][18]
        temp_user_list.append(temp_recommendation_19)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_20 = key[1][1][19]
        temp_user_list.append(temp_recommendation_20)
    except IndexError:
        temp_user_list.append("NA")
        
    master_recom_list_existing.append(temp_user_list  )
    
master_recomm_list_existing = pd.DataFrame(master_recom_list_existing)
master_recomm_list_existing.columns =  ['uid', 'recent', \
                                      'R1','R2','R3','R4','R5', 'R6', 'R7','R8','R9','R10',\
                                      'R11','R12','R13','R14','R15', 'R16', 'R17','R18','R19','R20']


######################## get new users, recommendation ###################################

## recs_using_self_history

select_top_N_recommendation = 20

master_recom_list_new = []

## for i in range(len(recs_using_self_history)):

for key in recs_using_friends.items():
    temp_user_list =[]
    temp_user_id= key[0]
    temp_user_list.append(temp_user_id)
                
    temp_recent_visit = key[1][0]
    temp_user_list.append(temp_recent_visit)
            
    temp_recommendation_01 = key[1][1][0]
    temp_user_list.append(temp_recommendation_01)
    
    try:        
        temp_recommendation_02 = key[1][1][1]
        temp_user_list.append(temp_recommendation_02)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_03 = key[1][1][2]
        temp_user_list.append(temp_recommendation_03)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_04 = key[1][1][3]
        temp_user_list.append(temp_recommendation_04)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_05 = key[1][1][4]
        temp_user_list.append(temp_recommendation_05)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_06 = key[1][1][5]
        temp_user_list.append(temp_recommendation_06)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_07 = key[1][1][6]
        temp_user_list.append(temp_recommendation_07)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_08 = key[1][1][7]
        temp_user_list.append(temp_recommendation_08)
    except IndexError:
        temp_user_list.append("NA")
     
    try:
        temp_recommendation_09 = key[1][1][8]
        temp_user_list.append(temp_recommendation_09)
    except IndexError:
        temp_user_list.append("NA")
       
    try:
        temp_recommendation_10 = key[1][1][9]
        temp_user_list.append(temp_recommendation_10)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_11 = key[1][1][10]
        temp_user_list.append(temp_recommendation_11)
    except IndexError:
        temp_user_list.append("NA")

    try:
        temp_recommendation_12 = key[1][1][11]
        temp_user_list.append(temp_recommendation_12)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_13 = key[1][1][12]
        temp_user_list.append(temp_recommendation_13)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_14 = key[1][1][13]
        temp_user_list.append(temp_recommendation_14)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_15 = key[1][1][14]
        temp_user_list.append(temp_recommendation_15)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_16 = key[1][1][15]
        temp_user_list.append(temp_recommendation_16)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_17 = key[1][1][16]
        temp_user_list.append(temp_recommendation_17)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_18 = key[1][1][17]
        temp_user_list.append(temp_recommendation_18)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_19 = key[1][1][18]
        temp_user_list.append(temp_recommendation_19)
    except IndexError:
        temp_user_list.append("NA")
        
    try:
        temp_recommendation_20 = key[1][1][19]
        temp_user_list.append(temp_recommendation_20)
    except IndexError:
        temp_user_list.append("NA")
        
    master_recom_list_new.append(temp_user_list  )

master_recomm_list_new = pd.DataFrame(master_recom_list_new)
master_recomm_list_new.columns =  ['uid', 'recent', \
                                      'R1','R2','R3','R4','R5', 'R6', 'R7','R8','R9','R10',\
                                      'R11','R12','R13','R14','R15', 'R16', 'R17','R18','R19','R20']
    
############################### MAP ID with NAMES #########################

master_recomm_list_existing_original = master_recomm_list_existing

master_users_name_trimmed = master_user_name[['uid', 'name']]
master_users_name_trimmed.index = master_users_name_trimmed.uid
master_users_name_trimmed = master_users_name_trimmed.drop('uid', axis = 1)

master_users_dicts = master_users_name_trimmed.to_dict()
master_users_dicts = master_users_dicts['name']

master_resta.index = master_resta['rid']
master_resta = master_resta.drop('rid', axis = 1)

master_resta_dicts = master_resta.to_dict()
master_resta_dicts = master_resta_dicts['venue_name']

master_recomm_list_existing['name'] = master_recomm_list_existing['uid'].map(master_users_dicts)

master_recomm_list_existing['recent'] = master_recomm_list_existing['recent'].map(master_resta_dicts)
master_recomm_list_existing['R1'] = master_recomm_list_existing['R1'].map(master_resta_dicts)
master_recomm_list_existing['R2'] = master_recomm_list_existing['R2'].map(master_resta_dicts)
master_recomm_list_existing['R3'] = master_recomm_list_existing['R3'].map(master_resta_dicts)
master_recomm_list_existing['R4'] = master_recomm_list_existing['R4'].map(master_resta_dicts)
master_recomm_list_existing['R5'] = master_recomm_list_existing['R5'].map(master_resta_dicts)
master_recomm_list_existing['R6'] = master_recomm_list_existing['R6'].map(master_resta_dicts)
master_recomm_list_existing['R7'] = master_recomm_list_existing['R7'].map(master_resta_dicts)
master_recomm_list_existing['R8'] = master_recomm_list_existing['R8'].map(master_resta_dicts)
master_recomm_list_existing['R9'] = master_recomm_list_existing['R9'].map(master_resta_dicts)
master_recomm_list_existing['R10'] = master_recomm_list_existing['R10'].map(master_resta_dicts)
master_recomm_list_existing['R11'] = master_recomm_list_existing['R11'].map(master_resta_dicts)
master_recomm_list_existing['R12'] = master_recomm_list_existing['R12'].map(master_resta_dicts)
master_recomm_list_existing['R13'] = master_recomm_list_existing['R13'].map(master_resta_dicts)
master_recomm_list_existing['R14'] = master_recomm_list_existing['R14'].map(master_resta_dicts)
master_recomm_list_existing['R15'] = master_recomm_list_existing['R15'].map(master_resta_dicts)
master_recomm_list_existing['R16'] = master_recomm_list_existing['R16'].map(master_resta_dicts)
master_recomm_list_existing['R17'] = master_recomm_list_existing['R17'].map(master_resta_dicts)
master_recomm_list_existing['R18'] = master_recomm_list_existing['R18'].map(master_resta_dicts)
master_recomm_list_existing['R19'] = master_recomm_list_existing['R19'].map(master_resta_dicts)
master_recomm_list_existing['R20'] = master_recomm_list_existing['R20'].map(master_resta_dicts)


##master_recomm_list_new
    
master_recomm_list_new['name'] = master_recomm_list_new['uid'].map(master_users_dicts)
master_recomm_list_new['recent'] = master_recomm_list_new['recent'].map(master_resta_dicts)
master_recomm_list_new['R1'] = master_recomm_list_new['R1'].map(master_resta_dicts)
master_recomm_list_new['R2'] = master_recomm_list_new['R2'].map(master_resta_dicts)
master_recomm_list_new['R3'] = master_recomm_list_new['R3'].map(master_resta_dicts)
master_recomm_list_new['R4'] = master_recomm_list_new['R4'].map(master_resta_dicts)
master_recomm_list_new['R5'] = master_recomm_list_new['R5'].map(master_resta_dicts)
master_recomm_list_new['R6'] = master_recomm_list_new['R6'].map(master_resta_dicts)
master_recomm_list_new['R7'] = master_recomm_list_new['R7'].map(master_resta_dicts)
master_recomm_list_new['R8'] = master_recomm_list_new['R8'].map(master_resta_dicts)
master_recomm_list_new['R9'] = master_recomm_list_new['R9'].map(master_resta_dicts)
master_recomm_list_new['R10'] = master_recomm_list_new['R10'].map(master_resta_dicts)
master_recomm_list_new['R11'] = master_recomm_list_new['R11'].map(master_resta_dicts)
master_recomm_list_new['R12'] = master_recomm_list_new['R12'].map(master_resta_dicts)
master_recomm_list_new['R13'] = master_recomm_list_new['R13'].map(master_resta_dicts)
master_recomm_list_new['R14'] = master_recomm_list_new['R14'].map(master_resta_dicts)
master_recomm_list_new['R15'] = master_recomm_list_new['R15'].map(master_resta_dicts)
master_recomm_list_new['R16'] = master_recomm_list_new['R16'].map(master_resta_dicts)
master_recomm_list_new['R17'] = master_recomm_list_new['R17'].map(master_resta_dicts)
master_recomm_list_new['R18'] = master_recomm_list_new['R18'].map(master_resta_dicts)
master_recomm_list_new['R19'] = master_recomm_list_new['R19'].map(master_resta_dicts)
master_recomm_list_new['R20'] = master_recomm_list_new['R20'].map(master_resta_dicts)


#############################Export file out to .csv #############################

master_recomm_list_existing.to_csv\
('recom_for_existing_user.csv', header = True, index= True, sep='\t', encoding='utf-8')

master_recomm_list_new.to_csv\
('recom_for_new_user.csv', header = True, index= True, sep='\t', encoding='utf-8')

friend_list.to_csv\
('friend_list.csv', header = True, index= True, sep='\t', encoding='utf-8')

master_user_name.to_csv\
('user_name.csv', header = True, index= True, sep='\t', encoding='utf-8')



