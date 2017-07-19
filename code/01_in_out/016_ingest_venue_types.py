import sqlite3
import pandas as pd, numpy as np

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'
file_path = 'D:/Workspace-Github/saproject/data/Grouping.csv'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

lookup = pd.read_csv(file_path, low_memory=False, encoding = 'latin1')

with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
    print(lookup)


c.execute('select rid, venue_type from venues')
types = c.fetchall()
for rid, type in types:
    try:
        df = lookup.loc[lookup['hundred'] == type]
        new_type = df.iloc[0]['twenty']
        print(str(new_type))
        c.execute("""UPDATE venues SET new_type = ? WHERE rid = ?;""",(new_type, rid))
    except:
        print(type)
conn.commit()
conn.close()