import sqlite3
import operator
import pandas as pd, numpy as np
import networkx as nx
from itertools import compress
import matplotlib.pyplot as plt
from sklearn.cluster import SpectralClustering

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT uid1, uid2, weight, kmeans from user_relationships;')
weights = c.fetchall()

df = pd.DataFrame(weights, columns = ['uid1', 'uid2', 'weight', 'kmeans'])
num_clusters = 4
for kmeans in range(len(set(df['kmeans']))):
    sub_df = df.loc[df['kmeans'] == kmeans]
    G = nx.Graph()
    users = set(pd.concat([sub_df['uid1'], sub_df['uid2']]))
    print(len(users))
    G.add_nodes_from(users)
    weights_matrix = sub_df.as_matrix(columns=['uid1', 'uid2', 'weight'])
    G.add_weighted_edges_from(weights_matrix)
    adj_matrix = nx.adjacency_matrix(G)
    
    clustering = SpectralClustering(num_clusters, affinity='precomputed', eigen_solver='arpack', assign_labels='discretize')#kmeans
    clustering.fit(adj_matrix)
    cluster_labels = clustering.labels_
    
    #nx.draw_networkx(G)
    #plt.show()
    clusters = [list(compress(users, cluster_labels == n)) for n in range(num_clusters)]
    for i in range(num_clusters):
        print(len(clusters[i]))
        for j in range(len(clusters[i])):
            c.execute('UPDATE users SET loc_clus_id = ' + str(kmeans) + ', res_clus_id = ' + str(i) + ' WHERE uid= ' + str(clusters[i][j]) + ';')
    conn.commit()
    
    for j in range(len(clusters)):
        cluster = clusters[j]
        G_sub = G.subgraph(cluster)
        degree_centrality = nx.degree_centrality(G_sub)
        file = open('D:/Workspace-Github/saproject/data/degree_centrality/kmeans_id_' + str(kmeans) + '_spectral_' + str(j) + '_centrality.txt', 'w', encoding = 'utf-8')
        centralities = sorted(degree_centrality.items(), key = operator.itemgetter(1), reverse = True)
        file.write('\n'.join('\t'.join([str(item) for item in centrality]) for centrality in centralities))
conn.close()
