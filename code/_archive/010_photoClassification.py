import requests
from bs4 import BeautifulSoup
import simplejson as json
import config
import pymysql
from multiprocessing import Pool
import multiprocessing

global database_conn
global database_cursor
database_conn = pymysql.connect(host = config.db_host, user = config.db_user, passwd = config.db_pass, db = config.db_database, use_unicode=True, charset="utf8")
database_cursor = database_conn.cursor()


def parallel(photoUrls):
    for pid, url in photoUrls.items():
        req = requests.get('http://api.foodai.org/v1/classify?image_url=' + url + '&num_tag=3')
        soup = BeautifulSoup(req.content, 'html.parser')
        try:
            jdata = json.loads(str(soup))
        except:
            print('Error!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            continue
        try:
            tag, probability = jdata['tags'][0]
            lineClassify = 'update photo set class="' + tag + '", probability=' + str(probability) + ' where pid="' + pid + '";'
            print(str(multiprocessing.current_process()) + lineClassify)
            database_cursor.execute(lineClassify)
            database_conn.commit()
        except:
            continue
    database_conn.close()   

if __name__ == '__main__':    
    photoUrlsub = {i:{} for i in range(7)}
    for i in range(7):
        offset = 1000*i
        sql = "select pid, url from photo where pid not in (SELECT pid FROM saproject.photo where class <> '') order by pid limit 2000 offset " + str(offset) + ";"
        database_cursor.execute(sql)
        results = database_cursor.fetchall()
        photoUrlsub[i] = {item[0]:item[1] for item in results}
    print(photoUrlsub)
    with Pool(7) as p:
        p.map(parallel, [value for value in photoUrlsub.values()])