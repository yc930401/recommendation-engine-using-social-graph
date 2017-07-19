import sqlite3
from nltk.corpus import wordnet as wn

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('SELECT rid, tip FROM tips;')
results = c.fetchall()
conn.close()

# food_list from wordnet
food = wn.synset('food.n.02')
food_list = list(set([w.replace('_', ' ') for s in food.closure(lambda s:s.hyponyms()) for w in s.lemma_names()]))
#food_list = []

# food_list from existing file
f = open('D:/Workspace-Github/saproject/code/99_bot/jiakbot/corpus/knowledge/foods.txt', 'r')
for i in range(53):
    food_list.append(f.readline().split('\n')[0].lower())
f.close()

# food_list from wiki
f = open('D:/Workspace-Github/saproject/code/99_bot/jiakbot/corpus/knowledge/food2.txt', 'r')
for i in range(120):
    food_list.append(f.readline().split('\n')[0].lower())
f.close()

print(food_list)
food_venue = open('D:/Workspace-Github/saproject/code/99_bot/jiakbot/corpus/knowledge/food_venue.txt', 'w', encoding = 'utf-8')
for rid, tip in results:
    for food in food_list:
        if food in tip.lower():
            food_venue.write('%s\t%s\n' % (food, rid))
food_venue.close()

