import sqlite3
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('SELECT tid, tip FROM tips;')
results = c.fetchall()

for tid, tip in results:
    sid = SentimentIntensityAnalyzer()
    rating = round((sid.polarity_scores(tip)['compound'] + 1) * 5, 2) # Rating: 1-10
    c.execute("""UPDATE tips SET senti_score = ? WHERE tid = ?;""",(rating, tid))

conn.commit()
conn.close()
