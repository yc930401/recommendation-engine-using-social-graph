import os
import json
import sqlite3

venue_json_dir = './data/json_venues/'

resta_ids = []

# connect database
conn = sqlite3.connect('./data/foursquare.db')
c = conn.cursor()
c.execute('DELETE FROM venues;')
conn.commit()

for filename in os.listdir(venue_json_dir):
    print('Processing:', filename)

    json_file = open(venue_json_dir + filename)
    raw_json = json_file.readlines()[0]

    parsed = json.loads(raw_json,encoding='utf-8')

    resta_records = []
    mrt = filename.split('_')[0]

    print(mrt)

    for i in parsed['response']['groups'][0]['items']:
        rid = i['venue']['id']
        url = 'https://foursquare.com/v/' + i['referralId'] + '/' + i['venue']['id']
        venue_type = i['venue']['categories'][0]['name']
        venue_name = i['venue']['name']

        try:
            rating = i['venue']['rating']
        except:
            rating = 0
        lat = i['venue']['location']['lat']
        lng = i['venue']['location']['lng']
        try:
            address = i['venue']['location']['address']
        except:
            address = ''
        try:
            postal = i['venue']['location']['postalCode']
        except:
            postal = ''

        if rid not in resta_ids:
            resta_records.append((rid, url, venue_type, venue_name, address, lat, lng, postal, mrt, rating))
            resta_ids.append(rid)

    # prepare and execute statement
    for record in resta_records:
        var_str = ', '.join('?' * len(record))
        query_str = 'INSERT INTO venues VALUES (%s);' % var_str
        c.execute(query_str, record)

    conn.commit()

conn.close()
