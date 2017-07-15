import pickle
import sqlite3
import operator
import networkx as nx
from itertools import compress
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
from sklearn.cluster import AgglomerativeClustering

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT uid1, uid2, weight from user_relationships;')
weights = c.fetchall()

df = pd.DataFrame(weights, columns = ['uid1', 'uid2', 'weight'])
num_clusters = 6

G = nx.Graph()
users = set(pd.concat([df['uid1'], df['uid2']]))
print(len(users))
G.add_nodes_from(users)
weights_matrix = df.as_matrix(columns=['uid1', 'uid2', 'weight'])
G.add_weighted_edges_from(weights_matrix)
adj_matrix = nx.adjacency_matrix(G)

# Spectral Clustering
num_clusters = 6
hierarchical = AgglomerativeClustering(n_clusters=num_clusters, affinity='precomputed', linkage='average')
hierarchical.fit(adj_matrix.todense())
hie_labels = hierarchical.labels_

filename = 'D:/Workspace-Github/saproject/data/clustering_models/Hierarchical.sav'
pickle.dump(hierarchical, open(filename, 'wb'))

hie_clusters = [list(compress(users, hie_labels == n)) for n in range(num_clusters)]
for i in range(num_clusters):
    print(len(hie_clusters[i]))
    for j in range(len(hie_clusters[i])):
        c.execute('UPDATE users SET hie_clus_id = ' + str(i) + ' WHERE uid= ' + str(hie_clusters[i][j]) + ';')
conn.commit()
conn.close()
