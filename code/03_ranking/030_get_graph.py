import sqlite3
import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite
import pickle

# params
# ---------------------------------------------------------------
db_path = './data/foursquare.db'

# main code chunk
# ---------------------------------------------------------------
conn = sqlite3.connect(db_path)
c = conn.cursor()

# FULL HISTORY GRAPH
# -------------------
# get all ratings (implied check-in. except the last rating for evaluation)
c.execute('SELECT combined_clus_id as clus_id, t.uid, t.rid, avg(senti_score) as score FROM tips t '
          'LEFT JOIN users u ON t.uid = u.uid '
          'GROUP BY t.rid, t.uid, u.combined_clus_id')

scores = c.fetchall()

# get users-venue score matrix (long term). this is the global cluster graph
df = pd.DataFrame(scores)
df.columns = ['clus_id','uid','rid','score']

# create the graph
g = nx.Graph()

user_set = []
venue_set = []
edge_weights = []
node_clus = {}

for row in df.iterrows():
    index, data = row

    clus_id = data[0]
    uid = data[1]
    rid = data[2]
    score = data[3]

    node_clus[uid] = clus_id

    if uid not in user_set:
        user_set.append(uid)
    if rid not in venue_set:
        venue_set.append(rid)

    ew = [uid, rid, score]

    edge_weights.append(tuple(ew))

g.add_nodes_from(user_set,bipartite=0)
g.add_nodes_from(venue_set,bipartite=1)
g.add_weighted_edges_from(edge_weights)

nx.set_node_attributes(g,'clus_id',node_clus)
u_nodes,r_nodes = bipartite.sets(g)
print('Full History Graph is graph bipartite:', nx.is_bipartite(g))

pickle.dump(g, open('data/graph_objects/g.sav', 'wb'))

# RECENT HISTORY GRAPH
# ------------------------
# create user-restaurant matrix (short-term) 7 most recent restaurants in order
# creates the user data for evaluation
c.execute('SELECT u.combined_clus_id, t.uid,t.rid,t.created_at,senti_score FROM tips t '
          'LEFT JOIN users u ON t.uid = u.uid '
          'WHERE t.uid in'
          '(SELECT uid FROM (SELECT uid, count(uid) as cnt FROM tips GROUP BY uid) WHERE cnt > 6)'
          'ORDER BY t.uid, t.created_at ASC')

tips = c.fetchall()
t_df = pd.DataFrame(tips)
t_df.columns = ['clus_id','uid','rid','created_at','score']

gt_df = t_df.groupby('uid')

# create the graph
rhg = nx.Graph()

user_set = []
venue_set = []
edge_weights = []
node_clus = {}

for grp in gt_df.groups.items():

    reviews = t_df.iloc[grp[1]]
    num_iterate = len(reviews) - 6

    for i in range(num_iterate):

        for j in range(0,6):

            data_ind = j+i

            clus_id = reviews.iloc[data_ind,0]
            uid = reviews.iloc[data_ind,1]
            rid = reviews.iloc[data_ind,2]
            score = reviews.iloc[data_ind,4]

            node_clus[uid] = clus_id

            if uid not in user_set:
                user_set.append(uid)
            if rid not in venue_set:
                venue_set.append(rid)

            ew = [uid, rid, score]
            edge_weights.append(tuple(ew))

rhg.add_nodes_from(user_set,bipartite=0)
rhg.add_nodes_from(venue_set,bipartite=1)
rhg.add_weighted_edges_from(edge_weights)

nx.set_node_attributes(rhg,'clus_id',node_clus)
u_nodes,r_nodes = bipartite.sets(rhg)
print('Recent History Graph is graph bipartite:', nx.is_bipartite(rhg))

pickle.dump(g, open('data/graph_objects/g_recent.sav', 'wb'))
