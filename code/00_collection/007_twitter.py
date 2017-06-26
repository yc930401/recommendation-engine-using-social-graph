import config
import pymysql
from datetime import datetime
import oauth2 as oauth
import simplejson as json
import time

global database_conn
global database_cursor
database_conn = pymysql.connect(host = config.db_host, user = config.db_user, passwd = config.db_pass, db = config.db_database, use_unicode=True, charset="utf8")
database_cursor = database_conn.cursor()

consumer = oauth.Consumer(key = config.consumer_key, secret = config.consumer_secret)
access_token = oauth.Token(key = config.oauth_token, secret = config.oauth_token_secret)
client = oauth.Client(consumer, access_token)

sql = "select uid, twitter_account from user where twitter_account <> '';"
database_cursor.execute(sql)
results = database_cursor.fetchall()
accounts = {uid[0]:uid[1] for uid in results}
print(len(accounts))
for uid, twittet_account in accounts.items():
    print(str(uid))
    full_url = 'https://api.twitter.com/1.1/users/show.json?screen_name=' + twittet_account
    response, data = client.request(full_url, method = 'GET')
    result = json.loads(data)
    
    outfile = open('twitter_account=' + str(uid) + '.json', 'w')
    json.dump(result, outfile)
    outfile.close()
    
    try:
        location = result['location']
    except:
        location = ''
    try:
        time_zone = result['time_zone']
        if time_zone is None:
            time_zone = ''
    except:
        time_zone = ''
    try:
        description = " ".join((" ".join(result['description'].split())).split('"'))
    except:
        description = ''
    date_format = "%m/%d/%Y"
    try:
        a = datetime.strptime(result['created_at'][4:11] + result['created_at'][-4:],'%b %d %Y')
        b = datetime.now()
        account_age = (str(b - a)).split()[0]
    except:
        account_age = 0
    
    if account_age == 0:
        lineUser = 'update user set location="' + location + '", time_zone="' + time_zone + '", description="' + description + '" where uid = ' + str(uid) + ';'
    else:
        lineUser = 'update user set location="' + location + '", time_zone="' + time_zone + '", description="' + description + '", account_age=' + account_age + ' where uid = ' + str(uid) + ';'
    print(lineUser)
    database_cursor.execute(lineUser)
    database_conn.commit()

database_conn.close()  