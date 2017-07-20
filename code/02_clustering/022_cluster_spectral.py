import pickle
import sqlite3
import operator
import networkx as nx
from scipy import sparse
from itertools import compress
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
from sklearn import mixture
#from sklearn.cluster import SpectralClustering
from sklearn.manifold import spectral_embedding

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT uid1, uid2, weight from user_relationships;')
weights = c.fetchall()

df = pd.DataFrame(weights, columns = ['uid1', 'uid2', 'weight'])

G = nx.Graph()
users = set(pd.concat([df['uid1'], df['uid2']]))
print(len(users))
G.add_nodes_from(users)
weights_matrix = df.as_matrix(columns=['uid1', 'uid2', 'weight'])
G.add_weighted_edges_from(weights_matrix)
adj_matrix = nx.adjacency_matrix(G)


scores = []
my_range = range(3, 30)
spe = spectral_embedding(adj_matrix, random_state=0, drop_first=True, n_components=20)

'''
# Choose the best k(num_clusters) using AIC. Do not run it, soooooooo slow!
for num_clusters in my_range:
    spc = mixture.GaussianMixture(n_components=num_clusters, random_state=0, covariance_type='full')
    spc.fit(spe)
    scores.append(spc.bic(np.array(spe)))

plt.plot(my_range, scores,'r-o')
plt.xlabel("# clusters")
plt.ylabel("# BIC")
plt.show()
'''

num_clusters = 5
spc = mixture.GaussianMixture(n_components=num_clusters, random_state=0, covariance_type='full')
spc.fit(spe)
spc_labels = spc.predict(spe)

filename = 'D:/Workspace-Github/saproject/data/clustering_models/Spectral.sav'
pickle.dump(spc, open(filename, 'wb'))

spc_clusters = [list(compress(users, spc_labels == n)) for n in range(num_clusters)]
for i in range(num_clusters):
    print(len(spc_clusters[i]))
    for j in range(len(spc_clusters[i])):
        c.execute('UPDATE users SET spe_clus_id = ' + str(i) + ' WHERE uid= ' + str(spc_clusters[i][j]) + ';')
conn.commit()
conn.close()
