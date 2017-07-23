import os
import json
import sqlite3

user_friends_json_dir = './data/json_friends/'

# connect database
conn = sqlite3.connect('./data/foursquare.db')
c = conn.cursor()
c.execute('DELETE FROM user_friends;')
conn.commit()

user_friends = {}
counter = 0

for filename in os.listdir(user_friends_json_dir):

    json_file = open(user_friends_json_dir + filename, encoding='utf-8')
    raw_json = json_file.readlines()[0]
    parsed = json.loads(raw_json,encoding='utf-8')

    uid = filename.split('_')[0]

    # check if friend list exists
    try:
        x = parsed['response']['friends']
    except:
        print(filename, ' | ',parsed)
        continue

    # for each friend check if exists, if not add to dict
    if uid not in user_friends.keys():
        user_friends[uid] = []

    for i in parsed['response']['friends']['items']:

        friend_uid = i['id']
        if friend_uid not in user_friends[uid]:
            user_friends[uid].append(friend_uid)

    # count processed files
    counter += 1
    if counter % 500 == 0:
        print("Completed processing file # ",counter)

# after finishing processing a UID, insert to db
for k in user_friends.keys():
    for v in user_friends[k]:
        var_str = k + ',' + v
        query_str = 'INSERT INTO user_friends (uid,friend_uid) VALUES (%s);' % var_str
        c.execute(query_str)

c.execute('DELETE FROM user_friends WHERE friend_uid NOT IN (SELECT uid FROM users);')
conn.commit()
conn.close()
