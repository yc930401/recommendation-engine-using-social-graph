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
