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

sql = 'SELECT uid FROM user limit 10000 OFFSET 7821;'#"SELECT uid, first_name, last_name FROM user;"
database_cursor.execute(sql)
results = database_cursor.fetchall()
users = [record[0] for record in results]

count = 0
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
        continue
    i = jdata['response']['user']
    tip_count = i['tips']['count']
    friend_count = i['friends']['count']
    photo_count = i['photos']['count']
    try:
        twitter_account = i['contact']['twitter']
    except:
        twitter_account = ''
    try:
        facebook_account = i['contact']['facebook']
    except:
        facebook_account = ''
    try:
        home_city = "".join(i['homeCity'].split('"'))
    except:
        home_city = ''
    friend_id = 0
    for item in i['friends']['groups'][1]['items']:
        friend_id = item['id']
        if friend_id in users:
            relationship.add((uid, friend_id))
    if twitter_account == '' and facebook_account == '':
        print('What????????????????????????????')
    lineUser = 'update user set twitter_account=' + '"' + twitter_account + '", facebook_account='+ '"' + facebook_account + '", tip_count=' + str(tip_count) + ', friend_count=' + str(friend_count) + ', photo_count=' + str(photo_count) + ', home_city="' + home_city + '" where uid = ' + str(uid) + ';'
    print(lineUser)
    database_cursor.execute(lineUser)
    database_conn.commit()
    '''
    if len(relationship) != 0:
        lineRelationship = 'insert into relationship values ' + str(relationship)[1:-1] + ';'
        database_cursor.execute(lineRelationship)
        database_conn.commit()
    '''
database_conn.close()   