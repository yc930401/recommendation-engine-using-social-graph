import requests
import time
import json
import configparser
import csv
import re
import sqlite3

# Set the file paths
config_path = './code/00_collection/config.ini'
tips_json_dir = './data/json_tips/'
db_path ='./data/foursquare.db'

# Read in the config.ini to get client_id and client_secret
config = configparser.ConfigParser()
config.read(config_path)

client_id = config['foursquare']['client_id']
client_secret = config['foursquare']['client_secret']
progress = config['tips']['progress']
limit = config['tips']['limit']

# Set the param for the call
param = {
    'client_id': client_id,
    'client_secret': client_secret,
    'sort': 'recent',
    'limit': '500',
    'v': '20170625'
}

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()


c.execute('SELECT DISTINCT rid FROM venues LIMIT ' + limit + ' OFFSET ' + progress + ';')
rids = c.fetchall()

for rid in rids:
    rid = rid[0]
    user_record = []
    comment_record = []
    param_str = '&'.join(['='.join(i) for i in param.items()])

    # make the API Call
    response = requests.get('https://api.foursquare.com/v2/venues/' + rid + '/tips?' + param_str)
    parsed = response.json()

    # write the raw response to file
    outfile = open(tips_json_dir + rid + '.json', 'w')
    json.dump(parsed, outfile)
    outfile.close()

with open(config_path, 'w') as configfile:
    v = int(progress)+int(limit)
    config.set('tips','progress',str(v))
    config.write(configfile)
