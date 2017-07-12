import sqlite3
from sklearn.cluster import KMeans
from scipy.spatial.distance import pdist, squareform
import pandas as pd, numpy as np
import networkx as nx
from networkx.algorithms import bipartite

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('DELETE FROM user_relationships;')
conn.commit()

c.execute('SELECT uid, venues.rid, count(*) as count, avg(tips.rating) as rating FROM venues inner join tips on tips.rid = venues.rid group by uid, venues.rid order by uid;')
results = c.fetchall()
print(len(results))

def weight(G, u, v):
    w = 0
    for nbr in set(G[u]) & set(G[v]):
        w += (G.edge[u][nbr]['weight'] + G.edge[v][nbr]['weight'])/2
    return w

df = pd.DataFrame(results, columns = ['uid', 'rid', 'count', 'rating'])
user_relationship = {}
    
B = nx.Graph()
B.add_nodes_from(df['uid'], bipartite=0)
B.add_nodes_from(df['rid'], bipartite=1)
edges = [(i[0], i[1], i[2]*i[3]) for i in df.as_matrix(columns=['uid', 'rid', 'count', 'rating'])]
B.add_weighted_edges_from(edges)
U = bipartite.projection.generic_weighted_projected_graph(B, df['uid'], weight_function=weight)
print(U.edges(data=True))

records = []
for edge in U.edges(data=True):
    record = (edge[0], edge[1], edge[2]['weight'])
    records.append(str(record))
var_str = ', '.join('?' * len(edge))
query_str = 'INSERT INTO user_relationships VALUES ' + ', '.join(records) + ';'
print(query_str)
c.execute(query_str)
conn.commit()
conn.close()
