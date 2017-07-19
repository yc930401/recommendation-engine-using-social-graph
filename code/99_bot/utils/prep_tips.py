from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import nltk
import re

import sqlite3

db_path = 'D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()


c.execute('SELECT tid, tip FROM tips')
results = c.fetchall()
records = []

# initialize the stop words removal and stemming
stop_list = nltk.corpus.stopwords.words('english')
stemmer = nltk.stem.porter.PorterStemmer()

# iterate through each record and create biz_id - category as a record
for tid, tip in results:
    sent_tokens = sent_tokenize(tip)
    for sent_token in sent_tokens:
        cleansed = word_tokenize(sent_token)
        cleansed = [w.lower() for w in cleansed]
        cleansed = [w for w in cleansed if re.search('^[a-z]+$', w)]
        if len(cleansed) > 1:
            cleansed = "|".join([w for w in cleansed])
            print(cleansed)
            c.execute('UPDATE tips SET tok_tip = ? WHERE tid= ?;', (cleansed, tid))
conn.commit()
conn.close()