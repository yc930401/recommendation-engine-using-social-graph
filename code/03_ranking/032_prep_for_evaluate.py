import sqlite3
import pandas as pd
import pickle

# params
# ---------------------------------------------------------------
db_path = './data/foursquare.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

g = pickle.load(open('data/graph_objects/g.sav', 'rb'))

# prepare the data for evaluation
# ----------------------------------------------------------------
# get all ratings (implied check-in. except the last rating for evaluation)
c.execute('SELECT u.combined_clus_id, t.uid,t.rid,t.created_at,senti_score FROM tips t '
          'LEFT JOIN users u ON t.uid = u.uid '
          'ORDER BY t.uid, t.created_at ASC')

scores = c.fetchall()

# get users-venue score
df = pd.DataFrame(scores)
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
        created_at = reviews.iloc[i,3]
        score = reviews.iloc[i,4]

        if i < len(reviews) - 1:
            history.append([uid,rid,score])
        else:
            latest = [uid,rid,score]

    usr_dict['history'] = history
    usr_dict['latest'] = latest
    usr_dict['clus_id'] = clus_id

    eval_records[uid] = usr_dict

pickle.dump(eval_records, open('data/graph_objects/eval_df.sav', 'wb'))