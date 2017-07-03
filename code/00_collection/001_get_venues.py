import requests
import time
import json
import configparser
import csv
import re

# Set the file paths
config_path = './code/00_collection/config.ini'
mrt_lrt_path = './data/mrt_lrt_latlng.csv'
venue_json_dir = './data/json_venues/'

# Read in the config.ini to get client_id and client_secret
config = configparser.ConfigParser()
config.read(config_path)

client_id = config['foursquare']['client_id']
client_secret = config['foursquare']['client_secret']

# Set the param for the call
param = {
    'client_id': client_id,
    'client_secret': client_secret,
    'radius': '800',
    'limit': '50',
    'offset': '0',
    'section': 'food',
    'v': '20170625'
}

# Read in the lat lng for all the mrt stations
stations = []
with open(mrt_lrt_path, 'r', encoding='utf-8') as csv_file:
    reader = csv.reader(csv_file, delimiter=',', quotechar='"')
    next(reader, None)
    for row in reader:
        lat = row[1]
        lng = row[0]
        sid = re.sub('[^0-9a-zA-Z]+', '_',row[4])

        stations.append([lat, lng, sid])

# for each lat lng, get the restaurants
for station in stations:

    offset = 0

    ll = ','.join(station[0:2])
    sid = station[2]

    while True:

        param['offset'] = str(offset)
        param['ll'] = ll

        param_str = '&'.join(['='.join(i) for i in param.items()])
        response = requests.get('https://api.foursquare.com/v2/venues/explore?' + param_str)
        parsed = response.json()

        # write the raw response to file
        outfile = open(venue_json_dir + sid + '_offset_' + param['offset'] + '.json', 'w')
        json.dump(parsed, outfile)
        outfile.close()

        # process the response
        total_results = parsed['response']['totalResults']

        # increment the offset
        offset += 50

        if total_results == 0 or offset >= total_results:
            break

    time.sleep(3)
