import sqlite3
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Set the file paths
db_path ='D:/Workspace-Github/saproject/data/foursquare.db'

# connect and write to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT rid, uid, tip from tips;')
results = c.fetchall()

for rid, uid, tip in results:
    sid = SentimentIntensityAnalyzer()
    rating = round((sid.polarity_scores(tip)['compound'] + 1) * 5, 2) #rating: 1-10
    print(rating)
    c.execute("""UPDATE tips SET senti_score = ? WHERE uid= ? and rid = ?;""",(rating, uid, rid))
conn.commit()
conn.close()
