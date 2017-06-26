import config
import pymysql
import urllib.request

global database_conn
global database_cursor
database_conn = pymysql.connect(host = config.db_host, user = config.db_user, passwd = config.db_pass, db = config.db_database, use_unicode=True, charset="utf8")
database_cursor = database_conn.cursor()

sql = 'SELECT pid, url FROM photo;'
database_cursor.execute(sql)
results = database_cursor.fetchall()
urls = {record[0]:record[1] for record in results}
for pid, url in urls.items():
    urllib.request.urlretrieve(url, 'D:\\Workspace-ME\\Collection\\src\\photos\\' + pid + '.jpg')
    print(pid)