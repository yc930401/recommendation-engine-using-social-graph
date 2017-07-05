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
    'limit': '250',
    'v': '20170625'
}

sql = "select distinct uid from user;"
database_cursor.execute(sql)
results = database_cursor.fetchall()
uids = [uid[0] for uid in results]

sql = "select distinct rid from restaurant;"
database_cursor.execute(sql)
results = database_cursor.fetchall()
rids = [rid[0] for rid in results]

for uid in uids:
    offset = 0
    count = -1
    while count == -1 or count == 250:
        checkin_record = []
        param_str = '&'.join(['='.join(i) for i in param.items()])
        req = requests.get('https://api.foursquare.com/v2/users/' + str(uid) + '/checkins?' + param_str + '&offset=' + str(offset))
        
        soup = BeautifulSoup(req.content, 'html.parser')
        try:
            jdata = json.loads(str(soup))
        except:
            print('Error!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            continue
        count = jdata['response']['checkins']['count']
        print(count)
        if count != 0:
            for i in jdata['response']['checkins']['items']:
                rid = i['venue']['id']
                checkin_record.append((uid, rid))
            lineCheckin = 'insert into checkin (uid, rid) values ' + str(checkin_record)[1:-1] + ';'
            print(lineCheckin)
            database_cursor.execute(lineCheckin)
            database_conn.commit()

database_conn.close()   