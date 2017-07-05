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
    'oauth_token': config.access_token,
    'sort': 'recent',
    'limit': '500',
    'v': '20170625'
}

sql = "select uid from (SELECT uid FROM user where photo_count>0) t limit 10000 OFFSET 5991;"
database_cursor.execute(sql)
results = database_cursor.fetchall()
uids = [uid[0] for uid in results]

for uid in uids:
    photo_record = []
    comment_record = []
    param_str = '&'.join(['='.join(i) for i in param.items()])
    req = requests.get('https://api.foursquare.com/v2/users/' + str(uid) + '/photos?' + param_str)
    
    soup = BeautifulSoup(req.content, 'html.parser')
    try:
        jdata = json.loads(str(soup))
    except:
        print('Error!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        continue
    count = jdata['response']['photos']['count']
    print(count)
    if count != 0:
        for i in jdata['response']['photos']['items']:
            pid = i['id']
            try:
                rid = i['venue']['id']
            except:
                rid = ''
            url = i['prefix'] + str(uid) + i['suffix']
            photo_record.append((pid, uid, rid, url))
        linePhoto = 'insert into photo (pid, uid, rid, url) values ' + str(photo_record)[1:-1] + ';'
        print(linePhoto)
        database_cursor.execute(linePhoto)
        database_conn.commit()

database_conn.close()   