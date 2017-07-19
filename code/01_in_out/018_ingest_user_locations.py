import sqlite3
import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite

######################################################
##### SQL Query for user visits by MRT locations #####
######################################################

# Set SQL Database file paths
db_path ='D:\MITB\Courses\B.8 - Social Analytics & Applications\Group Project/foursquare.db'

# Establish connection to SQL Database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create User MRT location Visit table
sql_str =   "SELECT u.uid, mrt, count(*) as visits " \
            "FROM users u, venues v, tips t " \
            "WHERE u.uid = t.uid AND t.rid = v.rid " \
            "GROUP BY u.uid, mrt " \
            "ORDER BY u.uid;" 

c.execute(sql_str)
user_mrt_visits = c.fetchall()


######################################################
##### Unipartite projections of bipartite graphs #####
######################################################

# User-defined weight functions for bipartite network projection
def jaccard(G, u, v):
    unbrs = set(G[u])
    vnbrs = set(G[v])
    return float(len(unbrs & vnbrs)) / len(unbrs | vnbrs)

def weight(G, u, v):
    w = 0
    for nbr in set(G[u]) & set(G[v]):
        w += (G.edge[u][nbr]['weight'] + G.edge[v][nbr]['weight'])/2
    return w

# Bipartite graph of user mrt locations visits
df = pd.DataFrame(user_mrt_visits, columns = ['uid', 'mrt', 'visits'])

B = nx.Graph()
B.add_nodes_from(df['uid'], bipartite=0)
B.add_nodes_from(df['mrt'], bipartite=1)
edges = [(i[0], i[1], i[2]) for i in df.as_matrix(columns=['uid', 'mrt', 'visits'])]
B.add_weighted_edges_from(edges)

# One-mode projections of bipartite graph
U = bipartite.projection.generic_weighted_projected_graph(B, df['uid'], weight_function=weight)


######################################################
##### Write one-mode projections to SQL database #####
######################################################

records = []
for edge in U.edges(data=True):
    record = (edge[0], edge[1], edge[2]['weight'])
    records.append(str(record))
query_str = 'INSERT INTO user_mrt_visits VALUES ' + ', '.join(records) + ';'
c.execute(query_str)
conn.commit()
conn.close()

# Save in database in steps of 5 million records
#records = []
#for edge in U.edges(data=True)[0:5000000]:
#    record = (edge[0], edge[1], edge[2]['weight'])
#    records.append(str(record))
#    
##for edge in U.edges(data=True)[5000000:10000000]:
##    record = (edge[0], edge[1], edge[2]['weight'])
##    records.append(str(record))
##
##for edge in U.edges(data=True)[10000000:15000000]:
##    record = (edge[0], edge[1], edge[2]['weight'])
##    records.append(str(record))
##
##for edge in U.edges(data=True)[15000000:18000000]:
##    record = (edge[0], edge[1], edge[2]['weight'])
##    records.append(str(record))
#    
#query_str = 'INSERT INTO user_mrt_visits VALUES ' + ', '.join(records) + ';'
#c.execute(query_str)
#conn.commit()
#conn.close()
