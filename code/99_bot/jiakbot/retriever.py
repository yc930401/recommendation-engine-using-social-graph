# import your libraries here
import sqlite3
import nltk
import re
from nltk.tokenize import word_tokenize
from gensim import corpora
from gensim import models
from gensim import similarities
import configparser

stop_list = nltk.corpus.stopwords.words('english')

class Retriever:

    def __init__(self,config, config_key):

        self.config = config
        self.config_key = config_key
        self._db_path = config[config_key]['db_path']
        self.retrieved_biz = []

    def get_business_by_food(self,parsed_dict,requested_food): # guaranteed to be different each time

        business = {
            'biz_id': '',
            'biz_name': '',
            'category': '',
            'cuisine': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food, b.biz_rating FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "WHERE lower(f.food) LIKE '%{0}%'".format(requested_food) + " " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  #  biz_id
        business['biz_name'] = result[1] #  biz_name
        business['category'] = result[2] #  the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,biz_id)

        self.retrieved_biz.extend([business])

        return business


    def get_business_by_cuisine(self,parsed_dict,requested_cuisine): # guaranteed to be different each time

        business = {
            'biz_id': '',
            'biz_name': '',
            'category': '',
            'cuisine': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, c.cuisine, b.biz_rating FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "LEFT JOIN cuisines c ON b.biz_id = c.biz_id " \
                  "WHERE lower(c.cuisine) LIKE '%{0}%' ".format(requested_cuisine) + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 10;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  # biz_id
        business['biz_name'] = result[1]  # biz_name
        business['category'] = result[2]  # the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,biz_id)

        self.retrieved_biz.extend([business])
        self.retrieved_biz_type.extend(['cuisine'])

        return business

    def get_business_by_food_cuisine(self,parsed_dict,requested_food,requested_cuisine): # guaranteed to be different each time

        business = {
            'biz_id': '',
            'biz_name': '',
            'category': '',
            'cuisine': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "LEFT JOIN cuisines c ON b.biz_id = c.biz_id " \
                  "WHERE lower(c.cuisine) LIKE '%{0}%' " \
                  "OR lower(f.food) LIKE '%{1}%' ".format(requested_food, requested_cuisine) + " " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  #  biz_id
        business['biz_name'] = result[1] #  biz_name
        business['category'] = result[2] #  the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,biz_id)

        self.retrieved_biz.extend([business])
        self.retrieved_biz_type.extend(['food_cuisine'])

        return business

    def get_random_business(self,parsed_dict):

        business = {
            'biz_id': '',
            'biz_name': '',
            'category': '',
            'cuisine': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food, b.biz_rating FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id WHERE 1 = 1 " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  # biz_id
        business['biz_name'] = result[1]  # biz_name
        business['category'] = result[2]  # the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,biz_id)

        self.retrieved_biz.extend([business])

        return business

    def get_random_similar_stmt_by_biz(self,parsed_dict,biz_id):

        statement = ''

        # Step 1: Select all statements
        sql_str = "SELECT r.biz_id, r.description, s.stmt FROM reviews r " \
                  "LEFT JOIN stmts s ON r.review_id = s.review_id " \
                  "WHERE r.biz_id = '{0}';".format(biz_id)


        results = []
        tokenized_docs = []

        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        for row in c.execute(sql_str):
            doc = word_tokenize(row[2])
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
            statement = results[most_similar_stmt_id][2]
        else:
            return None

        return statement

    def get_random_similar_stmt(self, stmt):

        statement = ''

        # Step 1: Select all statements
        sql_str = "SELECT stmt, stmt_cleansed FROM stmts ORDER BY RANDOM() LIMIT 10000" #

        results = []
        tokenized_docs = []

        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        for row in c.execute(sql_str):
            tokenized_docs.append(row[1].split('|'))
            results.append(row[0])

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

    def get_similar_business_by_name(self,parsed_dict, requested):

        businesses = []
        business = {}
        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food, b.biz_rating FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "LEFT JOIN reviews r ON b.biz_id = r.biz_id " \
                  "WHERE 1 = 1 " \
                  "AND b.biz_name LIKE '%{0}%' " \
                  "AND f.food NOT LIKE '%{0}%'".format(requested) + " " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  # biz_id
        business['biz_name'] = result[1]  # biz_name
        business['category'] = result[2]  # the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict, biz_id)

        self.retrieved_biz.extend([business])

        conn.close()

        return business

    def get_similar_business_by_review(self,parsed_dict,requested):

        businesses = []
        business = {}

        exclude_str = self._get_biz_id_exclude_str()

        sql_str = "SELECT b.biz_id, b.biz_name, f.food, b.biz_rating FROM businesses b " \
                  "LEFT JOIN foods f ON b.biz_id = f.biz_id " \
                  "LEFT JOIN reviews r ON b.biz_id = r.biz_id " \
                  "WHERE 1 = 1 " \
                  "AND r.description LIKE '%{0}%' " \
                  "AND f.food NOT LIKE '%{0}%'".format(requested) + " " + \
                  exclude_str + " " + \
                  "ORDER BY b.biz_rating DESC LIMIT 1;"

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        if result is None: return

        biz_id = result[0]
        business['biz_id'] = result[0]  # biz_id
        business['biz_name'] = result[1]  # biz_name
        business['category'] = result[2]  # the type of food they serve
        business['rating'] = result[3]  # rating
        business['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict, biz_id)

        self.retrieved_biz.extend([business])

        conn.close()

        return business

    def _get_biz_id_exclude_str(self):
        str = ''

        if len(self.retrieved_biz) > 0:
            biz_ids = [b['biz_id'] for b in self.retrieved_biz]
            biz_ids_str = ",".join('"' + biz_id + '"' for biz_id in biz_ids)
            str = "AND b.biz_id NOT IN ("+ biz_ids_str + ")"

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
#          'cuisines': ['japanese'],
#          'locations': [],
#          'retrieved': False,
#          'foods': ['burgers']}
#
# parsed_dict = {'tokens': ['you', 'know', 'of', 'any', 'place', 'for', 'japanese', 'or', 'sells', 'burgers', '?']}
# print(r.get_business_by_food(parsed_dict,'burgers'))
# print(r.get_similar_business('burgers'))

# r.get_random_similar_stmt("i like to eat healthy")