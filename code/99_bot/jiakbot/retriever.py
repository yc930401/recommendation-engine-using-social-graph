# import your libraries here
import sqlite3
import nltk
import re
from nltk.tokenize import word_tokenize
from gensim import corpora
from gensim import models
from gensim import similarities

stop_list = nltk.corpus.stopwords.words('english')

class Retriever:

    def __init__(self,config, config_key):

        self.config = config
        self.config_key = config_key
        self._db_path = config[config_key]['db_path']
        self.retrieved_biz = []

    def get_venue_by_food(self,parsed_dict,requested_food): # guaranteed to be different each time

        venue = {
            'rid': '',
            'venue_name': '',
            'venue_food': '',
            'venue_type': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT v.rid, v.venue_name, f.food, v.venue_type, v.rating FROM venues v " \
                  "LEFT JOIN venues_food f ON v.rid = f.rid " \
                  "WHERE lower(f.food) LIKE '%{0}%'".format(requested_food) + " " + \
                  exclude_str + " " + \
                  "ORDER BY v.rating DESC LIMIT 100;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        venue['rid'] = result[0]  #  biz_id
        venue['venue_name'] = result[1] #  biz_name
        venue['venue_food'] = result[2] #  the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,biz_id)

        self.retrieved_biz.extend([venue])

        return venue


    def get_venue_by_venue_type(self,parsed_dict,requested_venue_type): # guaranteed to be different each time

        venue = {
            'rid': '',
            'venue_name': '',
            'venue_food': '',
            'venue_type': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT v.rid, v.venue_name, f.food, v.venue_type, v.rating FROM venues v " \
                  "LEFT JOIN foods f ON v.rid = f.rid " \
                  "WHERE lower(v.venue_type) LIKE '%{0}%' ".format(requested_venue_type) + \
                  exclude_str + " " + \
                  "ORDER BY v.rating DESC LIMIT 10;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        venue['rid'] = result[0]  # biz_id
        venue['venue_name'] = result[1]  # biz_name
        venue['venue_food'] = result[2]  # the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,biz_id)

        self.retrieved_biz.extend([venue])
        self.retrieved_biz_type.extend(['venue_type'])

        return venue

    def get_venue_by_food_venue_type(self,parsed_dict,requested_food,requested_venue_type): # guaranteed to be different each time

        venue = {
            'rid': '',
            'venue_name': '',
            'venue_food': '',
            'venue_type': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT v.rid, v.venue_name, f.food, v.venue_type, v.rating FROM venues v " \
                  "LEFT JOIN venue_food f ON v.rid = f.rid " \
                  "WHERE lower(v.venue_type) LIKE '%{0}%' " \
                  "OR lower(f.food) LIKE '%{1}%' ".format(requested_food, requested_venue_type) + " " + \
                  exclude_str + " " + \
                  "ORDER BY v.rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        rid = result[0]
        venue['rid'] = result[0]  #  rid
        venue['venue_name'] = result[1] #  biz_name
        venue['venue_food'] = result[2] #  the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,rid)

        self.retrieved_biz.extend([venue])
        self.retrieved_biz_type.extend(['food_venue_type'])

        return venue

    def get_random_venue(self,parsed_dict):

        venue = {
            'rid': '',
            'venue_name': '',
            'venue_food': '',
            'venue_type': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT v.rid, v.venue_name, f.food, v.venue_type, v.rating FROM venues v " \
                  "LEFT JOIN venue_food f ON v.rid = f.rid WHERE 1 = 1 " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        rid = result[0]
        venue['rid'] = result[0]  # rid
        venue['venue_name'] = result[1]  # biz_name
        venue['venue_food'] = result[2]  # the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,rid)

        self.retrieved_biz.extend([venue])

        return venue

    def get_random_similar_stmt_by_biz(self,parsed_dict,rid):

        statement = ''

        # Step 1: Select all statements
        sql_str = "SELECT t.rid, t.tip FROM tips t " \
                  "WHERE t.rid = '{0}';".format(rid)


        results = []
        tokenized_docs = []

        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        for row in c.execute(sql_str):
            doc = word_tokenize(row[1])
            tokenized_docs.append(doc)
            results.append(row)

        conn.close()

        processed_docs = [[w.lower() for w in doc] for doc in tokenized_docs]
        processed_docs = [[w for w in doc if re.search('^[a-z]+$', w)] for doc in processed_docs]
        processed_docs = [[w for w in doc if w not in stop_list] for doc in processed_docs]

        # Step 2: Select most similar review based on query using cosine similarity

        reviews = corpora.Dictionary(processed_docs)

        r_vecs = [reviews.doc2bow(doc) for doc in processed_docs]
        r_tfidf = models.TfidfModel(r_vecs)
        r_vecs_with_tfidf = [r_tfidf[vec] for vec in r_vecs]

        r_index = similarities.SparseMatrixSimilarity(r_vecs_with_tfidf, len(reviews))

        query = parsed_dict['tokens']
        query_vec = reviews.doc2bow(query)
        query_vec_tfidf = r_tfidf[query_vec]

        q_sims = r_index[query_vec_tfidf]
        q_sorted_sims = sorted(enumerate(q_sims), key=lambda item: -item[1])

        # Step 3: Return most relevant statement back
        if len(q_sorted_sims) != 0:
            most_similar_stmt_id = q_sorted_sims[0][0]
            statement = results[most_similar_stmt_id][1]
        else:
            return None

        return statement

    def get_random_similar_stmt(self, stmt):

        statement = ''

        # Step 1: Select all statements
        sql_str = "SELECT tip, tok_tip FROM tips ORDER BY RANDOM() LIMIT 1000" #

        results = []
        tokenized_docs = []

        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        for row in c.execute(sql_str):
            try:
                tokenized_docs.append(row[1].split('|'))
                results.append(row[0])
            except:
                print('Error tip!')
        conn.close()

        processed_docs = [[w for w in doc if re.search('^[a-z]+$', w)] for doc in tokenized_docs]

        # Step 2: Select most similar review based on query using cosine similarity
        reviews = corpora.Dictionary(processed_docs)

        r_vecs = [reviews.doc2bow(doc) for doc in processed_docs]
        r_tfidf = models.TfidfModel(r_vecs)
        r_vecs_with_tfidf = [r_tfidf[vec] for vec in r_vecs]

        r_index = similarities.SparseMatrixSimilarity(r_vecs_with_tfidf, len(reviews))

        query = word_tokenize(stmt)
        query_vec = reviews.doc2bow(query)
        query_vec_tfidf = r_tfidf[query_vec]

        q_sims = r_index[query_vec_tfidf]
        q_sorted_sims = sorted(enumerate(q_sims), key=lambda item: -item[1])

        # Step 3: Return most relevant statement back only if it crosses the threshold
        if len(q_sorted_sims) != 0:
            stmt_index = q_sorted_sims[0][0]
            score = q_sorted_sims[0][1]
        else:
            return None

        if score > 0.6:
            statement = results[stmt_index]
        else:
            statement = None

        return statement

    def get_similar_venue_by_name(self,parsed_dict, requested):

        venue = {}
        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT v.rid, v.venue_name, f.food, v.venue_type, v.rating FROM venues v " \
                  "INNER JOIN venues_food f ON v.rid = f.rid " \
                  "WHERE 1 = 1 " \
                  "AND v.venue_name LIKE '%{0}%' ".format(requested) + " " + exclude_str + " " + \
                  "ORDER BY v.rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        rid = result[0]
        venue['rid'] = result[0]  # rid
        venue['venue_name'] = result[1]  # biz_name
        venue['venue_food'] = result[2]  # the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict, rid)

        self.retrieved_biz.extend([venue])

        conn.close()

        return venue

    def get_similar_venue_by_review(self,parsed_dict,requested):

        venuees = []
        venue = {}

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT v.rid, v.venue_name, f.food, v.venue_type, v.rating FROM venues v " \
                  "INNER JOIN venues_food f ON v.rid = f.rid " \
                  "WHERE 1 = 1 " \
                  "AND v.rid IN (SELECT DISTINCT(t.rid) FROM tips t WHERE t.tip LIKE '%{0}%')".format(requested) + \
                  " " + exclude_str + " " + \
                  "ORDER BY v.rating DESC LIMIT 1;"
        print(sql_str.encode(encoding='UTF-8',errors='strict'))
        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        rid = result[0]
        venue['rid'] = result[0]  # rid
        venue['venue_name'] = result[1]  # biz_name
        venue['venue_food'] = result[2]  # the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict, rid)

        self.retrieved_biz.extend([venue])

        conn.close()

        return venue

    def _get_rid_exclude_str(self):
        str = ''

        if len(self.retrieved_biz) > 0:
            rids = [b['rid'] for b in self.retrieved_biz]
            rids_str = ",".join('"' + rid + '"' for rid in rids)
            str = "AND v.rid NOT IN ("+ rids_str + ")"

        return str

########################################################
# for testing purposes
########################################################

# r = Retriever()

# state = {'current_state': [1, 1, 0],
#          'retrievable': True,
#          'post_feedback': False,
#          'previous_state': [1, 1, 0],
#          'recommendations': [],
#          'venue_types': ['japanese'],
#          'locations': [],
#          'retrieved': False,
#          'foods': ['burgers']}
#
# parsed_dict = {'tokens': ['you', 'know', 'of', 'any', 'place', 'for', 'japanese', 'or', 'sells', 'burgers', '?']}
# print(r.get_venue_by_food(parsed_dict,'burgers'))
# print(r.get_similar_venue('burgers'))

# r.get_random_similar_stmt("i like to eat healthy")