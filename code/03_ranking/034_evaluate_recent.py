import sqlite3
import pickle

g = pickle.load(open('data/graph_objects/g_recent.sav', 'rb'))
eval_records = pickle.load(open('data/graph_objects/eval_df_rh.sav', 'rb'))

recs_recent = {}
counter = 0

print('Recommendations (recent history) started at: ',getFormattedTime())
for uid,iteration in eval_records.items():

    for i, value in iteration.items():

        clus_id = value['clus_id']
        history = value['history']
        latest = value['latest']

        r = get_recommendations_using_history(g, uid, clus_id, history, top_n=200)
        recs_recent[uid] = (latest[1], r)

        counter += 1
        if counter % 100 == 0:
            print('Recommended records #', counter, 'at: ', getFormattedTime())

pickle.dump(recs_recent, open('data/rec_results/recs_recent.sav', 'wb'))

get_mrr(recs_recent)
print('Completed recommendations for recent history records')