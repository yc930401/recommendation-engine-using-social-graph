import requests
import json
import configparser
import sqlite3
from multiprocessing import Pool, Value, Lock
from ctypes import c_int
import time

# Set the file paths
db_path ='./data/foursquare.db'
config_path = './code/00_collection/config.ini'
outfile_path = './data/json_photo_cat.txt'

# Read in the config.ini to get client_id and client_secret
config = configparser.ConfigParser()
config.read(config_path)

progress = config['user_photos']['progress']
limit = config['user_photos']['limit']

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('SELECT pid, url FROM user_photos LIMIT ' + limit + ' OFFSET ' + progress + ';')
pid_urls = c.fetchall()

counter = Value(c_int)
counter_lock = Lock()

# global counter
def increment():
    with counter_lock:
        counter.value +=1

def get_image_class(outfile_path,pid_url):

    outfile = open(outfile_path, 'a')

    response = requests.get('http://api.foodai.org/v1/classify?image_url=' + pid_url[1] + '&num_tag=3')

    try:
        parsed = response.json()
        json.dump(parsed, outfile)
        outfile.write('|' + pid_url[0] + '|' + pid_url[1] + '\n')
    except:
        print('Error with pid:',pid_url[0])
    finally:
        increment()
        outfile.close()

        if counter.value % 100 == 0:
            print('processed records #', counter.value)

# parallel this
pid_urls = [pid_url for pid_url in pid_urls]

if __name__ == '__main__':

    time_bgn = time.time()

    args = list(zip([outfile_path]*len(pid_urls),pid_urls))
    with Pool(10) as p:
        p.starmap(get_image_class, args)

    dur = (time.time() - time_bgn)/60
    dur = '{0:.2f}'.format(dur)

    print('time taken to process',len(pid_urls),'records is',dur,'minutes')

    with open(config_path, 'w') as configfile:
        v = int(progress) + len(pid_urls)
        config.set('user_photos', 'progress', str(v))
        config.write(configfile)
