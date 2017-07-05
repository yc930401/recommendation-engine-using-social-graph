import requests
import json
import configparser
import sqlite3
import time

def write_to_config(config_path):
    with open(config_path, 'w') as configfile:
        v = int(progress) + counter
        config.set('users', 'progress', str(v))
        config.write(configfile)


# Set the file paths
config_path = './code/00_collection/config.ini'
photo_json_dir = './data/json_user_photos/'
db_path = './data/foursquare.db'

# Read in the config.ini to get client_id and client_secret
config = configparser.ConfigParser()
config.read(config_path)

app_to_use = 'app01'
client_id = config[app_to_use]['client_id']
client_secret = config[app_to_use]['client_secret']
access_token = config[app_to_use]['access_token']

# track progress
progress = config['users']['progress']
limit = config['users']['limit']

# Set the param for the call
param = {
    'client_id': client_id,
    'client_secret': client_secret,
    'oauth_token': access_token,
    'sort': 'recent',
    'limit': '200',
    'v': '20170625'
}

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT DISTINCT uid FROM users LIMIT ' + limit + ' OFFSET ' + progress + ';')
#c.execute("select uid from users where uid in ('17103062')")

uids = c.fetchall()

counter = 0

for uid in uids:

    uid = uid[0]
    photo_record = []

    param_str = '&'.join(['='.join(i) for i in param.items()])

    # make the API Call
    response = requests.get('https://api.foursquare.com/v2/users/' + str(uid) + '/photos?' + param_str)
    parsed = response.json()

    print(uid, parsed['meta'])

    # write the raw response to file
    outfile = open(photo_json_dir + str(uid) + '.json', 'w')
    json.dump(parsed, outfile)
    outfile.close()

    counter += 1

    if counter % 100 == 0:
        write_to_config(config_path)
        time.sleep(5)
        print('Processed user #', counter)

write_to_config(config_path)
