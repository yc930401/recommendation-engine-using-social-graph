import sqlite3
import pickle

# params
# ---------------------------------------------------------------
db_path = './data/foursquare.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

eval_graph = 'g.sav'
eval_df = 'eval_df_all.sav'
save_recs_path = 'recs_full.sav'

# eval_graph = 'g_venue.sav'
# eval_df = 'eval_df_venue.sav'
# save_recs_path = 'recs_full_venue.sav'

g = pickle.load(open('data/graph_objects/' + eval_graph, 'rb'))
eval_records = pickle.load(open('data/graph_objects/' + eval_df, 'rb'))

# perform the evaluation (users with history of more than 3 tips)
# ----------------------------------------------------------------
# dictionary to store the recommendations
recs = {}

# for users with visited count >= 3 use history to recommend
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) >= 3")
hist_recommend_users = c.fetchall()

counter = 0

print('Recommendations (history) started at: ',getFormattedTime())
for u in hist_recommend_users:

    uid = u[0]
    clus_id = eval_records[uid]['clus_id']
    history = eval_records[uid]['history']
    latest = eval_records[uid]['latest']

    r = get_recommendations_using_history(g, uid, clus_id, history, top_n=200)
    recs[uid] = (latest[1],r)

    counter += 1
    if counter % 1000 == 0:
        print('Recommended records #',counter,'at: ', getFormattedTime())

    # if counter == 500:
    #     break

print('Completed recommendations for history records')

# get all users with visited count < 3 use friends to recommend
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) < 3")
frd_recommend_users = c.fetchall()

counter = 0

print('Recommendations (friends) started at: ',getFormattedTime())
for u in frd_recommend_users:

    uid = u[0]
    latest = eval_records[uid]['latest']

    c.execute('SELECT friend_uid FROM user_friends WHERE uid =' + str(uid))
    frd_uids = c.fetchall()

    frd_uid_list = []
    for f in frd_uids:
        frd_uid_list.append(f[0])

    if len(frd_uid_list) > 0:
        r = get_recommendations_using_friends(g, frd_uid_list, uid, top_n=200)
    else:
        r = get_global_recommendation(g, top_n=200)

    recs[uid] = (latest[1],r)

    counter += 1
    if counter % 1000 == 0:
        print('Recommended records #',counter,'at: ', getFormattedTime())

    # if counter == 500:
    #     break


pickle.dump(recs, open('data/rec_results/' + save_recs_path, 'wb'))

# fill recs up to 200
# ------------------------------------------------
recs = pickle.load(open('./data/rec_results/recs_full_venue.sav', 'rb'))
global_rec = get_global_recommendation(g, top_n=200)

filled_recs = {}

for key, value in recs.items():
    uid = key
    latest = value[0]
    rec = value[1]
    if len(rec) < 200:
        num_to_append = 200 - len(rec)
        rec_to_append = global_rec[0:num_to_append]
        rec.extend(rec_to_append)

    filled_recs[uid] = (latest,rec)

pickle.dump(recs, open('./data/rec_results/recs_full_venue.sav', 'wb'))
get_mrr(recs)

recs = pickle.load(open('./data/rec_results/recs_full.sav', 'rb'))
global_rec = get_global_recommendation(g, top_n=200)

filled_recs = {}

for key, value in recs.items():
    uid = key
    latest = value[0]
    rec = value[1]
    if len(rec) < 200:
        num_to_append = 200 - len(rec)
        rec_to_append = global_rec[0:num_to_append]
        rec.extend(rec_to_append)

    filled_recs[uid] = (latest,rec)

pickle.dump(recs, open('./data/rec_results/recs_full.sav', 'wb'))
get_mrr(recs)
