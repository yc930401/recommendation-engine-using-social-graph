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
        if counter % 500 == 0:
            print('Recommended records #', counter, 'at: ', getFormattedTime())

pickle.dump(recs_recent, open('data/rec_results/recs_recent.sav', 'wb'))


# fill recs up to 200
# ------------------------------------------------
recs_recent = pickle.load(open('./data/rec_results/recs_recent.sav', 'rb'))
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

pickle.dump(recs_recent, open('./data/rec_results/recs_recent.sav', 'wb'))

get_mrr(recs_recent)
print('Completed recommendations for recent history records')