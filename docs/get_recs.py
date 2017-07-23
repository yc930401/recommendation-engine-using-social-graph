import pickle

recs = pickle.load(open('./data/rec_results/recs_full_venue.sav', 'rb'))

top_10_rec_dict = {}

for key,value in recs.items():
    uid = key
    top_10_rec = value[1][0:10]
    top_10_rec_dict[uid] = top_10_rec
