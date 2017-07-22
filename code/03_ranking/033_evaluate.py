import sqlite3
import pandas as pd
import pickle

# params
# ---------------------------------------------------------------
db_path = './data/foursquare.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

eval_records = pickle.load(open('data/graph_objects/eval_df.sav', 'rb'))

# perform the evaluation (users with history of more than 3 tips)
# ----------------------------------------------------------------
# for users with visited count >= 3 use history to recommend
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) >= 3")
hist_recommend_users = c.fetchall()

recs = {}
counter = 0

print('Evaluation started at: ',getFormattedTime())
for u in hist_recommend_users:

    uid = u[0]
    clus_id = eval_records[uid]['clus_id']
    history = eval_records[uid]['history']
    latest = eval_records[uid]['latest']

    # gx = g.copy()

    r = get_recommendation_for_history_for_eval(g, uid, clus_id, history, top_n=200)

    recs[uid] = (latest[1],r)

    counter += 1
    if counter % 100 == 0:
        print('Evaluated records #',counter,'at: ', getFormattedTime())

    if counter == 1000:
        break

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


