import sqlite3
import re
import operator
import pandas as pd, numpy as np
import networkx as nx
from itertools import compress
import matplotlib.pyplot as plt
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.cluster import SpectralClustering

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('select uid, new_type, count(*) from venues inner join tips on venues.rid = tips.rid group by uid, venue_type;')
weights = c.fetchall()

df = pd.DataFrame(weights, columns = ['uid', 'venue_type', 'count'])
types = list(set(df['venue_type']))
uids = set(df['uid'])
columns = ['uid'] + list(types)
zeros = [0 for i in range(len(types))]
data = [[uid] + zeros for uid in uids]

df_ = pd.DataFrame(columns=columns, data = data)
for index, row in df.iterrows():
    row_index = df_[df_['uid'] == row['uid']].index.tolist()[0]
    original = df_.loc[df_['uid'] == row['uid']][row['venue_type']]
    df_.set_value(row_index, row['venue_type'], original + 1)
with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
    print(df_)

df_.columns = ['uid'] + ['_'.join(type.split(' ')) for type in types]

create = ', '.join(['_'.join(type.split(' ')) + ' number' for type in types])
print(create)

try:
    c.execute('CREATE TABLE user_venue_type( uid number, ' + create + ');')
    conn.commit()
except:
    print('Table user_venue_type exists!')

insert = []
df_.to_sql(name = 'user_venue_type', con = conn, flavor='sqlite', if_exists='replace', index=index)
conn.close()