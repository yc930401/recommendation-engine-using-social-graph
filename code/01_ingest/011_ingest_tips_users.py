import os
import json
import sqlite3

tips_json_dir = './data/json_tips/'

# connect database
conn = sqlite3.connect('./data/foursquare.db')
c = conn.cursor()
c.execute('DELETE FROM tips;')
c.execute('DELETE FROM users;')
conn.commit()

<<<<<<< HEAD
=======

>>>>>>> 748c91984e0ab8a3d192694693e532771463fbc3
uids = []
cids = []

counter = 0

for filename in os.listdir(tips_json_dir):

    json_file = open(tips_json_dir + filename)
    raw_json = json_file.readlines()[0]

    parsed = json.loads(raw_json,encoding='utf-8')

    comment_records = []
    user_records = []

    rid = filename
    try:
        x = parsed['response']['tips']
    except:
        print(filename, ' | ',parsed)
        continue

<<<<<<< HEAD
=======
    print(parsed)

>>>>>>> 748c91984e0ab8a3d192694693e532771463fbc3
    for i in parsed['response']['tips']['items']:

        uid = i['user']['id']
        gender = i['user']['gender']

        cid = i['id']
        text = i['text']

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

        if cid not in cids:
            comment_records.append((rid, uid, text))
            cids.append(cid)

    # prepare and execute statement
    for record in user_records:
        var_str = ', '.join('?' * len(record))
<<<<<<< HEAD
        query_str = 'INSERT INTO users (uid, first_name, last_name, gender) VALUES (%s);' % var_str
=======
        query_str = 'INSERT INTO users VALUES (%s);' % var_str
>>>>>>> 748c91984e0ab8a3d192694693e532771463fbc3
        c.execute(query_str, record)

    for record in comment_records:
        var_str = ', '.join('?' * len(record))
        query_str = 'INSERT INTO tips VALUES (%s);' % var_str
        c.execute(query_str, record)

    conn.commit()

    counter += 1

    if counter % 100 == 0:
        print("Completed processing file # ",counter)

conn.close()
