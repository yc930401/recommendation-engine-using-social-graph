import sqlite3
import pandas as pd
import pickle

# params
# ---------------------------------------------------------------
db_path = './data/foursquare.db'
g = pickle.load(open('data/graph_objects/g.sav', 'rb'))

# main code chunk
# ---------------------------------------------------------------
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Evaluate FULL HISTORY recommendations
# ----------------------------------------------------------------
# get all ratings (implied check-in. except the last rating for evaluation)
c.execute('SELECT u.kmn_clus_id, t.uid,t.rid,t.created_at,senti_score FROM tips t '
          'LEFT JOIN users u ON t.uid = u.uid '
          'ORDER BY t.uid, t.created_at ASC')

scores = c.fetchall()

# get users-venue score
df = pd.DataFrame(scores)
df.columns = ['clus_id','uid','rid','created_at','score']

# construct the dictionary for evaluation in the format:
# key = uid
# ['key']['history'] = history
# ['key']['next_visit'] = latest tip

eval_records = {}

gt_df = df.groupby('uid')

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

# get all users with visited count >= 3
# use history to recommend
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) >= 3")
hist_recommend_users = c.fetchall()

recs = {}
counter = 0
print(Timer.getFormattedTime())
for u in hist_recommend_users:

    uid = u[0]
    clus_id = eval_records[uid]['clus_id']
    history = eval_records[uid]['history']
    latest = eval_records[uid]['latest']

    # gx = g.copy()

    r = get_recommendation_for_history(gx, uid, clus_id, history, top_n=20)

    recs[uid] = (latest[1],r)

    counter += 1
    if counter % 100 == 0:
        print(counter)
    if counter == 5000:
        break

print(Timer.getFormattedTime())

# evaluation
rr = 0

for ks,vs in recs.items():

    visited = vs[0]
    recommended = vs[1]


    for i in range(len(recommended)):
        if visited == recommended[i]:
            rr += 1/(i+1)

mrr = rr / len(recs.items())

print(mrr)

# get all users with visited count < 3
# use friends to recommend
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) < 3")
frd_recommend_users = c.fetchall()

# check if proposed venues are correct


