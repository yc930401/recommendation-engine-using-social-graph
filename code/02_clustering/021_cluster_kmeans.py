import pickle
import sqlite3
import operator
import networkx as nx
from itertools import compress
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
from sklearn.cluster import KMeans

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT * from user_venue_type;')
results = c.fetchall()
users = [result[0] for result in results]
x = [result[1:] for result in results]

num_clusters = 6
kmeans = KMeans(n_clusters=num_clusters, random_state=0)
kmeans.fit(x)
kmeans_labels = kmeans.labels_

filename = 'D:/Workspace-Github/saproject/data/clustering_models/KMeans.sav'
pickle.dump(kmeans, open(filename, 'wb'))

kmeans_clusters = [list(compress(users, kmeans_labels == n)) for n in range(num_clusters)]
for i in range(num_clusters):
    print(len(kmeans_clusters[i]))
    for j in range(len(kmeans_clusters[i])):
        c.execute('UPDATE users SET kmn_clus_id = ' + str(i) + ' WHERE uid= ' + str(kmeans_clusters[i][j]) + ';')
conn.commit()
conn.close()
