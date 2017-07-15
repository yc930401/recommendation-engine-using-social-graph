import pickle
import sqlite3
import operator
import networkx as nx
from scipy import sparse
from itertools import compress
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
from sklearn.cluster import SpectralClustering

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
spc = SpectralClustering(num_clusters, affinity='precomputed', eigen_solver='arpack', assign_labels='kmeans', random_state=0)#kmeans
spc.fit(adj_matrix)
spc_labels = spc.labels_

filename = 'D:/Workspace-Github/saproject/data/clustering_models/Spectral.sav'
pickle.dump(spc, open(filename, 'wb'))

spc_clusters = [list(compress(users, spc_labels == n)) for n in range(num_clusters)]
for i in range(num_clusters):
    print(len(spc_clusters[i]))
    for j in range(len(spc_clusters[i])):
        c.execute('UPDATE users SET spe_clus_id = ' + str(i) + ' WHERE uid= ' + str(spc_clusters[i][j]) + ';')
conn.commit()
conn.close()
