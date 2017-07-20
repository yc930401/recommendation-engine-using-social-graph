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

mrt_dict = {}

with open('./data/mappings/mrt_lrt_latlng.csv', encoding='utf-8') as mrt_mapping_file:
    lines = mrt_mapping_file.readlines()
    for line in lines:
        r = line.rstrip('\n').split(',')
        mrt_dict[r[4]] = r[3]

venue_dict = {}
with open('./data/mappings/grouping.csv', encoding='utf-8') as venue_mapping_file:
    lines = venue_mapping_file.readlines()
    for line in lines:
        r = line.rstrip('\n').split(',')
        venue_dict[r[0]] = r[1]


for filename in os.listdir(venue_json_dir):
    print('Processing:', filename)

    json_file = open(venue_json_dir + filename, encoding='utf-8')
    raw_json = json_file.readlines()[0]

    parsed = json.loads(raw_json,encoding='utf-8')

    resta_records = []
    mrt = filename.split('_')[0]
    mrt_name = mrt_dict[mrt]
    print(mrt)

    for i in parsed['response']['groups'][0]['items']:
        rid = i['venue']['id']
        url = 'https://foursquare.com/v/' + i['referralId'] + '/' + i['venue']['id']
        venue_type = i['venue']['categories'][0]['name']
        venue_name = i['venue']['name']
        new_type = venue_dict[venue_type]
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
            resta_records.append((rid, url, venue_type, venue_name, address, lat, lng, postal, mrt, mrt_name, rating, new_type))
            resta_ids.append(rid)

    # prepare and execute statement
    for record in resta_records:
        var_str = ', '.join('?' * len(record))
        query_str = 'INSERT INTO venues (rid, url, venue_type, venue_name, address, lat, lng, postal, mrt, mrt_name, rating, new_type) ' \
                    'VALUES (%s);' % var_str
        c.execute(query_str, record)

    conn.commit()

conn.close()
