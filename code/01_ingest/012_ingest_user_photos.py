import os
import json
import sqlite3

user_photos_json_dir = './data/json_user_photos/'

# connect database
conn = sqlite3.connect('./data/foursquare.db')
c = conn.cursor()
c.execute('DELETE FROM user_photos;')
conn.commit()

pids = []

counter = 0

for filename in os.listdir(user_photos_json_dir):

    json_file = open(user_photos_json_dir + filename)
    raw_json = json_file.readlines()[0]

    parsed = json.loads(raw_json,encoding='utf-8')

    photo_records = []

    uid = filename.split('.')[0]

    try:
        x = parsed['response']['photos']
    except:
        print(filename, ' | ',parsed)
        continue

    for i in parsed['response']['photos']['items']:

        pid = i['id']

        try:
            rid = i['venue']['id']
        except:
            rid = ''

        url = i['prefix'] + str(uid) + i['suffix']

        if pid not in pids:
            photo_records.append((pid, uid, rid, url))

    # prepare and execute statement
    for record in photo_records:
        var_str = ', '.join('?' * len(record))
        query_str = 'INSERT INTO user_photos (pid,uid,rid,url) VALUES (%s);' % var_str
        c.execute(query_str, record)

    conn.commit()

    counter += 1

    if counter % 100 == 0:
        print("Completed processing file # ",counter)

conn.close()
