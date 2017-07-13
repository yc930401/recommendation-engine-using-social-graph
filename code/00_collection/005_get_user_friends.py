import requests
import json
import configparser
import sqlite3
import time
import sys,os

def write_to_config(config_path):
    with open(config_path, 'w') as configfile:
        v = int(progress) + uid_count
        config.set('user_friends', 'progress', str(v))
        config.write(configfile)

# Set the file paths
config_path = './code/00_collection/config.ini'
friends_json_dir = './data/json_friends/'
db_path = './data/foursquare.db'

# Declare the config parser
config = configparser.ConfigParser()

#app_ids = ['app01','app02','app03','app04','app05','app06','app07','app08','app09',
#           'app10','app11','app12','app13','app14','app15','app16','app17','app18']

app_ids = ['app06','app07','app08']

# For each app_id
for app_to_use in app_ids:

    print('--------------------------------------')
    print('using app id', app_to_use)
    print('--------------------------------------')

    # Read in current progress
    config.read(config_path)
    progress = config['user_friends']['progress']
    limit = config['user_friends']['limit']

    # Read in the app ID to use
    client_id = config[app_to_use]['client_id']
    client_secret = config[app_to_use]['client_secret']
    access_token = config[app_to_use]['access_token']

    # Set the params
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
    c.execute('SELECT DISTINCT uid FROM users WHERE uid != "6858102" LIMIT ' + limit + ' OFFSET ' + progress + ';')

    # fetch the user ids
    uids = c.fetchall()

    req_count = 0
    uid_count = 0

    try:

        for uid in uids:

            offset = 0
            uid = uid[0]

            # print current request
            print('Processing user #', uid)

            while True:

                param['offset'] = str(offset)
                param_str = '&'.join(['='.join(i) for i in param.items()])

                # make the API Call
                response = requests.get('https://api.foursquare.com/v2/users/' + str(uid) + '/friends?' + param_str)
                parsed = response.json()

                # write the raw response to file
                outfile = open(friends_json_dir + str(uid) + '_' + str(offset) + '.json', 'w')
                json.dump(parsed, outfile)
                outfile.close()

                # process the response
                if parsed['meta']['code'] != 200:
                    raise Exception('API call did not get any result with msg: ' + str(parsed['meta']))

                total_results = parsed['response']['friends']['count']

                # increment the offset
                offset += 100
                req_count += 1

                # if no more results for the user then increment uid process +1
                if total_results == 0 or offset >= total_results:
                    print('Req Count', req_count, '| Processing user #', uid, '| Processed friends',total_results)
                    uid_count += 1
                    write_to_config(config_path)
                    time.sleep(1)
                    break

                # break if hit limit and use the next app id
                if req_count == 500:
                    break

            # break if hit limit and use the next app id
            if req_count == 500:
                break



    except Exception as e:
        print(repr(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    finally:
        write_to_config(config_path)
