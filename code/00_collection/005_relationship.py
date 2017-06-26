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
    'v': '20170625'
}

sql = 'SELECT distinct uid FROM user;'
database_cursor.execute(sql)
results = database_cursor.fetchall()
users_all = [record[0] for record in results]

sql = 'SELECT distinct uid FROM user limit 10000 OFFSET 0;'#"SELECT uid, first_name, last_name FROM user;"
database_cursor.execute(sql)
results = database_cursor.fetchall()
users = [record[0] for record in results]

for uid in users:
    user_record = []
    comment_record = []
    relationship = set()
    param_str = '&'.join(['='.join(i) for i in param.items()])
    req = requests.get('https://api.foursquare.com/v2/users/' + str(uid) + '?' + param_str)
    
    soup = BeautifulSoup(req.content, 'html.parser')
    try:
        jdata = json.loads(str(soup))
    except:
        print('Error!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        continue
    print(str(uid))
    for item in jdata['response']['user']['friends']['groups'][1]['items']:
        friend_id = item['id']
        if friend_id in users_all:
            relationship.add((uid, friend_id))
    if len(relationship) != 0:
        lineRelationship = 'insert into relationship values ' + str(relationship)[1:-1] + ';'
        print(lineRelationship)
        database_cursor.execute(lineRelationship)
        database_conn.commit()
database_conn.close()   