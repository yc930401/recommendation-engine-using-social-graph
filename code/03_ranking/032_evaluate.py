
import sqlite3
import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite

# params
# ---------------------------------------------------------------
db_path = './data/foursquare.db'

# main code chunk
# ---------------------------------------------------------------
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Evaluate FULL HISTORY recommendations
# ----------------------------------------------------------------


# get all users with visited count >= 3
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) >= 3")
hist_recommend_users = c.fetchall()

# get all users with visited count < 3
c.execute("SELECT DISTINCT uid FROM tips t GROUP BY uid HAVING COUNT(tid) < 3")
frd_recommend_users = c.fetchall()


#

# get all ratings (implied check-in. except the last rating for evaluation)
c.execute('SELECT kmn_clus_id as clus_id, t.uid, t.rid, avg(senti_score) as score FROM tips t '
          'LEFT JOIN users u ON t.uid = u.uid '
          'WHERE t.tid NOT IN (SELECT tid FROM tips GROUP BY uid HAVING MAX(created_at)) '
          'GROUP BY t.rid, t.uid, u.kmn_clus_id')
scores = c.fetchall()

# get users-venue score
df = pd.DataFrame(scores)
df.columns = ['clus_id','uid','rid','score']


# Get the uid, clus_id, history and the latest records


# based on the history propose venues


# check if proposed venues are correct


