import sqlite3
import pandas as pd

##################################################
##### SQL Query for user visits by locations #####
##################################################

# Set SQL Database file paths
db_path ='D:\MITB\Courses\B.8 - Social Analytics & Applications\Group Project/foursquare.db'
#db_path ='C:/Users\Wesley Chan\Documents\GitHub\saproject\data/foursquare.db'

# Establish connection to SQL Database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create MRT station to area location table
mrt_mapping = pd.read_csv('D:\MITB\Courses\B.8 - Social Analytics & Applications\Group Project/mrt_mapping.csv')
mrt_mapping.to_sql(name='mrt_table', con=conn, if_exists='replace', index=False)

# Create User MRT location Visit using comment count as a proxy for visit count
sql_str =   "SELECT u.uid, loc, count(*) as visits " \
            "FROM users u, venues v, mrt_table m, tips t " \
            "WHERE u.uid = t.uid AND t.rid = v.rid AND v.mrt = m.stn_no " \
            "GROUP BY u.uid, loc " \
            "ORDER BY u.uid;" 

c.execute(sql_str)
user_loc = c.fetchall()


####################################################
##### Save User Location Visit to SQL database #####
####################################################

df = pd.DataFrame(user_loc, columns = ['uid', 'loc', 'visits'])
df_pivot = df.pivot_table(index='uid', columns='loc', values='visits', fill_value=0)
df_proportion = df_pivot.div(df_pivot.sum(axis=1), axis=0)

df_pivot.to_sql(name='user_loc', con=conn, if_exists='replace', index=True)
df_proportion.to_sql(name='user_loc_proportion', con=conn, if_exists='replace', index=True)

conn.commit()
conn.close()


