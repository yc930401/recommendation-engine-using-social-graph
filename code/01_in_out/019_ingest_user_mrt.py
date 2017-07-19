import sqlite3
import pandas as pd

######################################################
##### SQL Query for user visits by MRT locations #####
######################################################

# Set SQL Database file paths
db_path ='D:\MITB\Courses\B.8 - Social Analytics & Applications\Group Project/foursquare.db'
#db_path ='C:/Users\Wesley Chan\Documents\GitHub\saproject\data/foursquare.db'

# Establish connection to SQL Database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create User MRT location Visit using comment count as a proxy for visit count
sql_str =   "SELECT u.uid, mrt, count(*) as visits " \
            "FROM users u, venues v, tips t " \
            "WHERE u.uid = t.uid AND t.rid = v.rid " \
            "GROUP BY u.uid, mrt " \
            "ORDER BY u.uid;" 

c.execute(sql_str)
user_mrt = c.fetchall()


########################################################
##### Save User MRT Location Visit to SQL database #####
########################################################

df = pd.DataFrame(user_mrt, columns = ['uid', 'mrt', 'visits'])
df_pivot = df.pivot_table(index='uid', columns='mrt', values='visits', fill_value=0)
df_proportion = df_pivot.div(df_pivot.sum(axis=1), axis=0)

df_pivot.to_sql(name='user_mrt', con=conn, if_exists='replace', index=True)
df_proportion.to_sql(name='user_mrt_proportion', con=conn, if_exists='replace', index=True)

