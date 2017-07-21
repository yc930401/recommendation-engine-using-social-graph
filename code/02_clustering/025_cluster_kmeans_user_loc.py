import pickle
import sqlite3
import operator
import networkx as nx
from sklearn import metrics, decomposition, mixture
from itertools import compress
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
from sklearn import cluster
from sklearn.cluster import KMeans

######################################################
##### SQL Query for user visit count by Location #####
######################################################

# Set SQL Database file paths
db_path ='D:\MITB\Courses\B.8 - Social Analytics & Applications\Group Project/foursquare.db'

# Establish connection to SQL Database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Retrieve unipartite user relationship based on MRT location visits
c.execute('SELECT * from user_loc_proportion;')
records = c.fetchall()
user = [user_loc[0] for user_loc in records]
mrt = [user_loc[1:] for user_loc in records]


###########################################################
##### Determine optimal K / # of clusters for K-Means #####
###########################################################

max_cluster = 51

n_clus = np.arange(2, max_cluster)
AIC = [0.0] * len(n_clus)
BIC = [0.0] * len(n_clus)

for i in range(len(n_clus)):
    kmeans = cluster.KMeans(n_clusters=n_clus[i], random_state=2017)
    kmeans.fit(mrt)
    AIC[i] = 2*n_clus[i] + 24289 * 20 * np.log(2*np.pi)+ kmeans.inertia_
    BIC[i] = np.log(24289 * 20) * n_clus[i] + 24289 * 20 * np.log(2*np.pi) + kmeans.inertia_
    
#print('AIC:', AIC)    
#print('BIC:', BIC)  

plt.figure(figsize = (12, 12))
plt.grid(True)
plt.xticks(n_clus)
plt.title('AIC & BIC Plot by Cluster Count')
plt.xlabel('Number of Clusters')
plt.ylabel('Information Criterion')
plt.plot(n_clus, AIC, 'ro-', label='AIC')
plt.plot(n_clus, BIC, 'bo-', label='BIC')
plt.show()


##### Silhouette Score Analysis #####
from sklearn.metrics import silhouette_samples, silhouette_score

best_silhouette = -1
best_clusters = 0
silhouette_scores = []

for n_clusters in range(2, max_cluster):
    kmeans = cluster.KMeans(n_clusters, random_state=2017)
    kmeans.fit(mrt)
    
    silhouette = silhouette_score(mrt, kmeans.labels_)
    silhouette_scores.append(silhouette)

    if silhouette > best_silhouette:
        best_silhouette = silhouette
        best_clusters = n_clusters

print("Best Silhouette score: ", best_silhouette)
print("Best number of clusters: ", best_clusters)
print(" ")

xaxis_data = list(range(2,max_cluster))
plt.figure(figsize = (12, 12))
plt.grid(True)
plt.title('Silhouette Plot by Cluster Count')
plt.xlabel('Number of Clusters')
plt.ylabel('Silhouette Score')
plt.plot(xaxis_data, silhouette_scores, 'b-')
plt.show() 

 
##### Percentage of Variance Explained / Elbow Method #####
from scipy.spatial.distance import cdist, pdist

mrt_array = np.array(mrt)

clusters = range(2,max_cluster)
kMeansVar = [KMeans(n_clusters=k, init='k-means++', random_state=2017)
              .fit(mrt_array) for k in clusters]
centroids = [X.cluster_centers_ for X in kMeansVar]
label = [X.labels_ for X in kMeansVar]
k_euclid = [cdist(mrt_array, cent) for cent in centroids]
dist = [np.min(ke, axis=1) for ke in k_euclid]
wcss = [sum(d**2) for d in dist]
tss = sum(pdist(mrt_array)**2)/mrt_array.shape[0]
bss = tss - wcss

fig = plt.figure(figsize = (12, 12))
ax = fig.add_subplot(111)
ax.plot(clusters, bss/tss*100, 'b*-')
plt.grid(True)
plt.title('% of Variance Explained by Cluster Count')
plt.xlabel('Number of Clusters')
plt.ylabel('Percentage of Variance Explained')
plt.show() 


##### Gap Statistic Analysis #####
def optimalK(data, nrefs=3, maxClusters=15):
    """
    Calculates KMeans optimal K using Gap Statistic from Tibshirani, Walther, Hastie
    Params:
        data: ndarry of shape (n_samples, n_features)
        nrefs: number of sample reference datasets to create
        maxClusters: Maximum number of clusters to test for
    Returns: (gaps, optimalK)
    """
    gaps = np.zeros((len(range(1, maxClusters)),))
    resultsdf = pd.DataFrame({'clusterCount':[], 'gap':[]})
    for gap_index, k in enumerate(range(1, maxClusters)):

        # Holder for reference dispersion results
        refDisps = np.zeros(nrefs)

        # For n references, generate random sample and perform kmeans getting 
        #  resulting dispersion of each loop
        for i in range(nrefs):
            
            # Create new random reference set
            randomReference = np.random.random_sample(size=data.shape)
            
            # Fit to it
            km = KMeans(k)
            km.fit(randomReference)
            
            refDisp = km.inertia_
            refDisps[i] = refDisp

        # Fit cluster to original data and create dispersion
        km = KMeans(k)
        km.fit(data)
        origDisp = km.inertia_

        # Calculate gap statistic
        gap = np.log(np.mean(refDisps)) - np.log(origDisp)

        # Assign this loop's gap statistic to gaps
        gaps[gap_index] = gap
        resultsdf = resultsdf.append({'clusterCount':k, 'gap':gap}, ignore_index=True)

    return (gaps.argmax() + 1, resultsdf)  
    

# Find optimal K using Gap Statistics
k, gapdf = optimalK(mrt_array, nrefs=10, maxClusters=max_cluster)
print("Optimal K based on Gap Statistics: ", k)

# Plot of the Gap Statistic
plt.figure(figsize = (12, 12))
plt.plot(gapdf.clusterCount, gapdf.gap, linewidth=3)
plt.scatter(gapdf[gapdf.clusterCount == k].clusterCount, gapdf[gapdf.clusterCount == k].gap, s=250, c='r')
plt.grid(True)
plt.title('Gap Values by Cluster Count')
plt.xlabel('Number of Clusters')
plt.ylabel('Gap Value')
plt.show()
    

##### AIC Information Criterion using GMM #####
my_range = range(2, max_cluster)
scores = []
for num_clusters in my_range:
    em = mixture.GaussianMixture(n_components=num_clusters, random_state=2017, covariance_type='full')
    em.fit(mrt)
    scores.append(em.aic(np.array(mrt)))
   
plt.figure(figsize = (12, 12))
plt.plot(my_range, scores,'r-o')
plt.grid(True)
plt.title('GMM - AIC Plot by Cluster Count')
plt.xlabel('Number of Clusters')
plt.ylabel('Information Criterion')
plt.show()


######################################################
##### K-Means for User-Location Count Proportion #####
######################################################
num_clusters = 20

kmeans = KMeans(n_clusters=num_clusters, random_state=2017)
kmeans.fit(mrt)
kmeans_labels = kmeans.labels_ 


###################################################
##### Save User Cluster Label to SQL database #####
###################################################

filename = 'D:\MITB\Courses\B.8 - Social Analytics & Applications\Group Project/KMeans_Loc_Proportion.sav'
pickle.dump(kmeans, open(filename, 'wb'))

# Update K-Means cluster ID / label to database
kmeans_clusters = [list(compress(user, kmeans_labels == n)) for n in range(num_clusters)]
for i in range(num_clusters):
    print(len(kmeans_clusters[i]))
    for j in range(len(kmeans_clusters[i])):
        c.execute('UPDATE users SET kmn_loc_clus_id = ' + str(i) + ' WHERE uid= ' + str(kmeans_clusters[i][j]) + ';')
conn.commit()
conn.close()
