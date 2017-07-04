import config
import pymysql
import facebook

global database_conn
global database_cursor
database_conn = pymysql.connect(host = config.db_host, user = config.db_user, passwd = config.db_pass, db = config.db_database, use_unicode=True, charset="utf8")
database_cursor = database_conn.cursor()

sql = "select uid, facebook_account from user where twitter_account = '' and facebook_account <> '';"
database_cursor.execute(sql)
results = database_cursor.fetchall()
accounts = {uid[0]:uid[1] for uid in results}

####################### Cannot get facebook user data #########################
for uid, fecebook_account in accounts.items():   
    graph = facebook.GraphAPI(config.client_token, version='2.7')
    profile = graph.get_object('http://www.facebook.com/' + fecebook_account)
    args = {'fields' : 'hometown, location, about' }
    profile = graph.get_object('http://www.facebook.com/' + fecebook_account, **args)
'''
 
    lineUser = 'update user set location="' + location + '", time_zone="' + time_zone + '", description="' + description + ', "account_age=' + account_age + ' where uid = ' + str(uid) + ';'
    print(lineUser)
    database_cursor.execute(lineUser)
    database_conn.commit()

database_conn.close()  
'''