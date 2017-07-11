import requests
import json
import configparser
import sqlite3
import time

def write_to_config(config_path):
    with open(config_path, 'w') as configfile:
        v = int(progress) + counter
        config.set('user_friends', 'progress', str(v))
        config.write(configfile)

# Set the file paths
config_path = './code/00_collection/config.ini'
friends_json_dir = './data/json_friends/'
db_path = './data/foursquare.db'

# Read in the config.ini to get client_id and client_secret
config = configparser.ConfigParser()
config.read(config_path)

app_to_use = 'app01'
client_id = config[app_to_use]['client_id']
client_secret = config[app_to_use]['client_secret']
access_token = config[app_to_use]['access_token']

# track progress
progress = config['user_friends']['progress']
limit = config['user_friends']['limit']

# Set the param for the call
param = {
    'client_id': client_id,
    'client_secret': client_secret,
    'oauth_token': access_token,
    'limit': '500',
    'v': '20170625'
}

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT DISTINCT uid FROM users LIMIT ' + limit + ' OFFSET ' + progress + ';')
#c.execute("select uid from users where uid in ('17103062')")

uids = c.fetchall()
user_processed = 0

for uid in uids:

    counter = 0
    offset = 0
    uid = uid[0]
    photo_record = []

    while True:

        param['offset'] = str(offset)
        param_str = '&'.join(['='.join(i) for i in param.items()])

        # make the API Call
        response = requests.get('https://api.foursquare.com/v2/users/' + str(uid) + '/friends?' + param_str)
        parsed = response.json()

        # write the raw response to file
        outfile = open(friends_json_dir + str(uid) + '.json', 'w')
        json.dump(parsed, outfile)
        outfile.close()

        # process the response
        total_results = parsed['response']['friends']['count']

        # increment the offset
        offset += 100
        counter += 100
        user_processed += 1

        print('counter',counter)

        if counter % 100 == 0:
            write_to_config(config_path)
            print('Record #',user_processed ,'| Processed user #',uid ,'| offset', counter)
            time.sleep(1)

        if total_results == 0 or offset >= total_results:
            print('Processed friends',total_results)
            break

write_to_config(config_path)
