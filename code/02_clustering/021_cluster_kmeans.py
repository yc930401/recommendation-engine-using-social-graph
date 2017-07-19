import pickle
import sqlite3
import operator
import networkx as nx
from sklearn import metrics, decomposition, mixture
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
'''
# Choose the best k(num_clusters) using AIC. Do not run it, soooooooo slow!
my_range = range(1, 30)
scores = []
for num_clusters in my_range:
    em = mixture.GaussianMixture(n_components=num_clusters, random_state=0, covariance_type='full')
    em.fit(x)
    scores.append(em.aic(np.array(x)))
    
print(scores)

plt.plot(my_range, scores,'r-o')
plt.xlabel("# clusters")
plt.ylabel("# AIC")
plt.show()
'''

# Train a model with the best k = 4
num_clusters = 4
kmeans = KMeans(n_clusters=num_clusters, random_state=0)
kmeans.fit(x)
kmeans_labels = kmeans.labels_ 

# Save the model
filename = 'D:/Workspace-Github/saproject/data/clustering_models/KMeans.sav'
pickle.dump(kmeans, open(filename, 'wb'))

# Update kmn_clus_id to database
kmeans_clusters = [list(compress(users, kmeans_labels == n)) for n in range(num_clusters)]
for i in range(num_clusters):
    print(len(kmeans_clusters[i]))
    for j in range(len(kmeans_clusters[i])):
        c.execute('UPDATE users SET kmn_clus_id = ' + str(i) + ' WHERE uid= ' + str(kmeans_clusters[i][j]) + ';')
conn.commit()
conn.close()
