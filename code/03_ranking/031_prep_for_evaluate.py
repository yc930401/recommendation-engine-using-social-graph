import sqlite3
import pandas as pd
import pickle

# params
# ---------------------------------------------------------------
db_path = './data/foursquare.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# prepare the data for evaluation (ALL)
# ----------------------------------------------------------------
# get all ratings (implied check-in. except the last rating for evaluation)
c.execute('SELECT u.combined_clus_id, t.uid,t.rid,t.created_at,senti_score FROM tips t '
          'LEFT JOIN users u ON t.uid = u.uid '
          'ORDER BY t.uid, t.created_at ASC')

result = c.fetchall()

# get users-venue score
df = pd.DataFrame(result)
df.columns = ['clus_id','uid','rid','created_at','score']
gt_df = df.groupby('uid')

# construct the dictionary for evaluation in the format:
# key = uid
# ['key']['history'] = history
# ['key']['next_visit'] = latest tip

eval_records = {}

for grp in gt_df.groups.items():

    reviews = df.iloc[grp[1]]

    usr_dict = {}
    history = []
    latest = []

    for i in range(len(reviews)):

        clus_id = reviews.iloc[i,0]
        uid = reviews.iloc[i,1]
        rid = reviews.iloc[i,2]
        score = reviews.iloc[i,4]

        if i < len(reviews) - 1:
            history.append([uid,rid,score])
        else:
            latest = [uid,rid,score]

    usr_dict['history'] = history
    usr_dict['latest'] = latest
    usr_dict['clus_id'] = clus_id

    eval_records[uid] = usr_dict

pickle.dump(eval_records, open('data/graph_objects/eval_df_all.sav', 'wb'))


# prepare the data for evaluation (ALL)
# ----------------------------------------------------------------
# get all ratings (implied check-in. except the last rating for evaluation)
c.execute('SELECT u.senti_clus_id, t.uid,t.rid,t.created_at,senti_score FROM tips t '
          'LEFT JOIN users u ON t.uid = u.uid '
          'ORDER BY t.uid, t.created_at ASC')

result = c.fetchall()

# get users-venue score
df = pd.DataFrame(result)
df.columns = ['clus_id','uid','rid','created_at','score']
gt_df = df.groupby('uid')

# construct the dictionary for evaluation in the format:
# key = uid
# ['key']['history'] = history
# ['key']['next_visit'] = latest tip

eval_records = {}

for grp in gt_df.groups.items():

    reviews = df.iloc[grp[1]]

    usr_dict = {}
    history = []
    latest = []

    for i in range(len(reviews)):

        clus_id = reviews.iloc[i,0]
        uid = reviews.iloc[i,1]
        rid = reviews.iloc[i,2]
        score = reviews.iloc[i,4]

        if i < len(reviews) - 1:
            history.append([uid,rid,score])
        else:
            latest = [uid,rid,score]

    usr_dict['history'] = history
    usr_dict['latest'] = latest
    usr_dict['clus_id'] = clus_id

    eval_records[uid] = usr_dict

pickle.dump(eval_records, open('data/graph_objects/eval_df_venue.sav', 'wb'))


# prepare the data for evaluation (RECENT HISTORY)
# ----------------------------------------------------------------
# get all ratings (implied check-in. except the last rating for evaluation)
c.execute('SELECT u.combined_clus_id, t.uid,t.rid,t.created_at,senti_score FROM tips t '
          'LEFT JOIN users u ON t.uid = u.uid '
          'WHERE t.uid in'
          '(SELECT uid FROM (SELECT uid, count(uid) as cnt FROM tips GROUP BY uid) WHERE cnt > 6)'
          'ORDER BY t.uid, t.created_at ASC')

result = c.fetchall()
rh_df = pd.DataFrame(result)
rh_df.columns = ['clus_id','uid','rid','created_at','score']
grh_df = rh_df.groupby('uid')

# construct the dictionary for evaluation in the format:
# key = uid
# ['key']['history'] = history
# ['key']['next_visit'] = latest tip

eval_records_rh = {}

for grp in grh_df.groups.items():

    reviews = rh_df.iloc[grp[1]]
    num_iterate = len(reviews) - 5

    grp_dict = {}

    for i in range(num_iterate):

        usr_dict = {}
        history = []
        latest = []

        for j in range(0,6):

            data_ind = j+i

            clus_id = reviews.iloc[data_ind,0]
            uid = reviews.iloc[data_ind,1]
            rid = reviews.iloc[data_ind,2]
            score = reviews.iloc[data_ind,4]

            if j < 5:
                history.append([uid, rid, score])
            else:
                latest = [uid, rid, score]

        usr_dict['history'] = history
        usr_dict['latest'] = latest
        usr_dict['clus_id'] = clus_id

        grp_dict[i] = usr_dict

    eval_records_rh[uid] = grp_dict

pickle.dump(eval_records_rh, open('data/graph_objects/eval_df_rh.sav', 'wb'))
