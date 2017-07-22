import sqlite3
from nltk.corpus import wordnet as wn

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('SELECT rid, tip FROM tips;')
results = c.fetchall()

food_list = []
# food_list from existing file
f = open('D:/Workspace-Github/saproject/code/bot/jiakbot/corpus/knowledge/foods.txt', 'r')
for i in range(173):
    food_list.append(f.readline().split('\n')[0].lower())
f.close()
print(food_list)

records = []
food_venue = open('D:/Workspace-Github/saproject/code/bot/jiakbot/corpus/knowledge/food_venue.txt', 'w', encoding = 'utf-8')
for rid, tip in results:
    for food in food_list:
        if food in tip.lower():
            food_venue.write('%s\t%s\n' % (food, rid))
            records.append(str((rid, food)))
food_venue.close()

query_str = 'INSERT INTO venues_food VALUES ' + ', '.join(records) + ';'
print(query_str)
c.execute(query_str)
conn.commit()
conn.close()
