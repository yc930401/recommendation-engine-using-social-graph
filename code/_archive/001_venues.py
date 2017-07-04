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
    #'near': 'Singapore',
    'll': '1.438921, 103.817338',
    'radius': '5000',
    'limit': '50',
    'offset': '0',
    'section': 'food',
    'v': '20170625'
}

lls = ['1.433430, 103.718462', '1.421074, 103.702669', '1.394303, 103.697176', '1.370277, 103.698549',
       '1.353803, 103.673830', '1.350370, 103.709535', '1.327031, 103.706102', '1.327717, 103.668336', 
       '1.285843, 103.630571', '1.456082, 103.813219', '1.438921, 103.798112', '1.441667, 103.829698',
       '1.423820, 103.769273', '1.424506, 103.803606', '1.418328, 103.833131', '1.402540, 103.755540',
       '1.393617, 103.793306', '1.396362, 103.818712', '1.392930, 103.853731', '1.406659, 103.881196',
       '1.398422, 103.906602', '1.373710, 103.761720', '1.358608, 103.807039', '1.364786, 103.837938',
       '1.370277, 103.868837', '1.379888, 103.896303', '1.377828, 103.925828', '1.370964, 103.942308',
       '1.365472, 103.973207', '1.355175, 103.896303', '1.350370, 103.937501', '1.329777, 103.956727',
       '1.338701, 103.764467', '1.332522, 103.793993', '1.331150, 103.826952', '1.331150, 103.856477',
       '1.331836, 103.885316', '1.331836, 103.912782', '1.303691, 103.789873', '1.303691, 103.816652',
       '1.305064, 103.844804', '1.302318, 103.881883', '1.305750, 103.907976', '1.281037, 103.865404',
       '1.277605, 103.825578', '1.255638, 103.832445', '1.295453, 103.842058', '1.338014, 103.719835']

resta_ids = []
for ll in lls:
    count = 0
    param['offset'] = 0
    while count == 0 or count == 50:
        resta_record = []
        param['offset'] = str(int(param['offset']) + 50)
        param['ll'] = ll
        param_str = '&'.join(['='.join(i) for i in param.items()])
        req = requests.get('https://api.foursquare.com/v2/venues/explore?' + param_str)
        
        soup = BeautifulSoup(req.content, 'html.parser')
        jdata = json.loads(str(soup))
        
        outfile = open('venue_offset=' + param['offset'] + '.json', 'w')
        json.dump(jdata, outfile)
        outfile.close()   
        
        count = len(jdata['response']['groups'][0]['items'])
        for i in jdata['response']['groups'][0]['items']:
            rid = i['venue']['id']
            url = 'https://foursquare.com/v/' + i['referralId'] + '/' + i['venue']['id']
            type = i['venue']['categories'][0]['name']
            name = i['venue']['name']
            try:
                rating = i['venue']['rating']
            except:
                rating = 0
            lat = i['venue']['location']['lat']
            lng = i['venue']['location']['lng']
            try:
                address = i['venue']['location']['address']
            except:
                address = ''
            try:
                zipcode = i['venue']['location']['postalCode']
            except:
                zipcode = ''
            if rid not in resta_ids:
                resta_record.append((rid, url, type, name, address, lat, lng, zipcode, rating))
                resta_ids.append(rid)
        if count == 0 or len(resta_record) == 0:
            break
        line = 'insert into restaurant values ' + str(resta_record)[1:-1] + ';'
        print(line)
        database_cursor.execute(line)
        database_conn.commit()
print(len(resta_ids))
database_conn.close()