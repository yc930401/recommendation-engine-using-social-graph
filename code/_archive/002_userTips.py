import requests
from bs4 import BeautifulSoup
import simplejson as json
import config
import pymysql

global database_conn
global database_cursor
database_conn = pymysql.connect(host = config.db_host, user = config.db_user, passwd = config.db_pass, db = config.db_database, use_unicode=True, charset="utf8")
database_cursor = database_conn.cursor()

param = {
    'client_id': config.client_id,
    'client_secret': config.client_secret,
    'sort': 'recent',
    'limit': '500',
    'v': '20170625'
}

sql = "SELECT rid FROM restaurant;"
database_cursor.execute(sql)
results = database_cursor.fetchall()
rids = [rid[0] for rid in results]

count = 0
uids = []
for rid in rids:
    user_record = []
    comment_record = []
    param_str = '&'.join(['='.join(i) for i in param.items()])
    req = requests.get('https://api.foursquare.com/v2/venues/' + rid + '/tips?' + param_str)
    
    try:
        soup = BeautifulSoup(req.content, 'html.parser')
        jdata = json.loads(str(soup))
    except:
        continue
    
    outfile = open('tips_' + rid + '.json', 'w')
    json.dump(jdata, outfile)
    outfile.close()   
    
    count = jdata['response']['tips']['count']
    for i in jdata['response']['tips']['items']:
        cid = i['id']
        text = i['text']
        uid = i['user']['id']
        try:
            firstName = i['user']['firstName']
        except:
            firstName = ''
        try:
            lastName = i['user']['lastName']
        except:
            lastName = ''
        gender = i['user']['gender']
        
        if uid not in uids:
            user_record.append((uid, firstName, lastName, gender))
            uids.append(uid)
        comment_record.append((rid, uid, text))
    if count == 0:
        break
    lineUser = 'insert into user(uid, first_name, last_name, gender) values ' + str(user_record)[1:-1] + ';'
    lineComment = 'insert into comment values ' + str(comment_record)[1:-1] + ';'
    print(lineUser)
    print(lineComment)
    if len(user_record) == 0:
        break
    database_cursor.execute(lineUser)
    try:
        database_cursor.execute(lineComment)
    except:
        print('Duplicate comment: ', lineComment)
    finally:
        database_conn.commit()

database_conn.close()   