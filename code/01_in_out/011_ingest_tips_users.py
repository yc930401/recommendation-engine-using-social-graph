import os
import json
import sqlite3
import time

tips_json_dir = './data/json_tips/'

# connect database
conn = sqlite3.connect('./data/foursquare.db')
c = conn.cursor()
c.execute('DELETE FROM tips;')
c.execute('DELETE FROM users;')
conn.commit()

uids = []
tids = []

counter = 0

for filename in os.listdir(tips_json_dir):

    json_file = open(tips_json_dir + filename)
    raw_json = json_file.readlines()[0]

    parsed = json.loads(raw_json,encoding='utf-8')

    comment_records = []
    user_records = []

    rid = filename.split('.')[0]
    try:
        x = parsed['response']['tips']
    except:
        print(filename, ' | ',parsed)
        continue

    for i in parsed['response']['tips']['items']:

        uid = i['user']['id']
        gender = i['user']['gender']

        tid = i['id']
        text = i['text']
        created_at = i['createdAt']
        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created_at))

        try:
            firstName = i['user']['firstName']
        except:
            firstName = ''
        try:
            lastName = i['user']['lastName']
        except:
            lastName = ''

        if uid not in uids:
            user_records.append((uid, firstName, lastName, gender))
            uids.append(uid)

        if tid not in tids:
            comment_records.append((tid, rid, uid,created_at, text))
            tids.append(tid)

    # prepare and execute statement
    for record in user_records:
        var_str = ', '.join('?' * len(record))
        query_str = 'INSERT INTO users (uid, first_name, last_name, gender) VALUES (%s);' % var_str
        c.execute(query_str, record)

    for record in comment_records:
        var_str = ', '.join('?' * len(record))
        query_str = 'INSERT INTO tips (tid, rid, uid,created_at, tip) VALUES (%s);' % var_str
        c.execute(query_str, record)

    conn.commit()

    counter += 1

    if counter % 100 == 0:
        print("Completed processing file # ",counter)

conn.close()
