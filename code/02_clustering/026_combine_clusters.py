import sqlite3


# Set SQL Database file paths
# db_path ='D:\MITB\Courses\B.8 - Social Analytics & Applications\Group Project/foursquare.db'
db_path = './data/foursquare.db'

# Establish connection to SQL Database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('UPDATE users SET senti_clus_id = 99 WHERE senti_clus_id IS NULL;')
conn.commit()

c.execute('UPDATE users SET combined_clus_id = senti_clus_id || "_" || venue_clus_id || "_" || mrt_loc_clus_id;')

conn.close()
