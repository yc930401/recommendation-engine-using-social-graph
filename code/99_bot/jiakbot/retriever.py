# import your libraries here
import sqlite3
import nltk
import re
from nltk.tokenize import word_tokenize
from gensim import corpora
from gensim import models
from gensim import similarities
import numpy as np
import operator
import pickle

stop_list = nltk.corpus.stopwords.words('english')

class Retriever:

    def __init__(self,config, config_key):

        self.config = config
        self.config_key = config_key
        self._db_path = config[config_key]['db_path']
        self.g_path = config[config_key]['g_path']
        self.g_recent_path = config[config_key]['g_recent_path']

        self.g = pickle.load(open(self.g_path, 'rb'))
        self.g_recent = pickle.load(open(self.g_recent_path, 'rb'))

        self.retrieved_biz = []
        self.retrieved_biz_type = []

    def get_venue_by_food(self,parsed_dict,requested_food, uid=None): # guaranteed to be different each time

        venue = {
            'rid': '',
            'venue_name': '',
            'venue_food': '',
            'venue_type': '',
            'mrt': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT DISTINCT v.rid, v.venue_name, f.food, v.venue_type, v.rating, v.mrt_name FROM venues v " \
                  "INNER JOIN venues_food f ON v.rid = f.rid " \
                  "WHERE lower(f.food) LIKE '%{0}%'".format(requested_food) + " " + \
                  exclude_str + " " + \
                  "ORDER BY v.rating DESC;"

        print('get_venue_by_food --- ',sql_str)

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        all_results = c.fetchall()
        conn.close()

        if len(all_results) == 0: return

        if uid is not None:
            rids = [r[0] for r in all_results]
            top_rid = self._get_venue_by_rids(uid, rids)[0]

            for r in all_results:
                if r[0] == top_rid:
                    result = r
                    break
        else:
            result = all_results[0]

        rid = result[0]
        venue['rid'] = result[0]  #  biz_id
        venue['venue_name'] = result[1] #  biz_name
        venue['venue_food'] = result[2] #  the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['mrt'] = result[5]  # mrt
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,rid)

        self.retrieved_biz.extend([venue])

        return venue


    def get_venue_by_venue_type(self,parsed_dict,requested_venue_type, uid=None): # guaranteed to be different each time

        venue = {
            'rid': '',
            'venue_name': '',
            'venue_food': '',
            'venue_type': '',
            'mrt': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT DISTINCT v.rid, v.venue_name, f.food, v.venue_type, v.rating, v.mrt_name FROM venues v " \
                  "INNER JOIN venues_food f ON v.rid = f.rid " \
                  "WHERE lower(v.venue_type) LIKE '%{0}%' ".format(requested_venue_type) + \
                  exclude_str + " " + \
                  "ORDER BY v.rating DESC;"

        print('get_venue_by_venue_type --- ',sql_str)

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        all_results = c.fetchall()
        conn.close()

        if len(all_results) == 0: return

        if uid is not None:
            rids = [r[0] for r in all_results]
            top_rid = self._get_venue_by_rids(uid, rids)[0]
            for r in all_results:
                if r[0] == top_rid:
                    result = r
                    break
        else:
            result = all_results[0]

        rid = result[0]
        venue['rid'] = result[0]  # biz_id
        venue['venue_name'] = result[1]  # biz_name
        venue['venue_food'] = result[2]  # the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['mrt'] = result[5]  # mrt
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,rid)

        self.retrieved_biz.extend([venue])
        self.retrieved_biz_type.extend(['venue_type'])

        return venue

    def get_venue_by_food_venue_type(self,parsed_dict,requested_food,requested_venue_type, uid=None): # guaranteed to be different each time

        venue = {
            'rid': '',
            'venue_name': '',
            'venue_food': '',
            'venue_type': '',
            'mrt': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT DISTINCT v.rid, v.venue_name, f.food, v.venue_type, v.rating, v.mrt_name FROM venues v " \
                  "INNER JOIN venues_food f ON v.rid = f.rid " \
                  "WHERE lower(v.venue_type) LIKE '%{0}%' " \
                  "OR lower(f.food) LIKE '%{1}%' ".format(requested_food, requested_venue_type) + " " + \
                  exclude_str + " " + \
                  "ORDER BY v.rating DESC;"

        print('get_venue_by_food_venue_type --- ',sql_str)

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        all_results = c.fetchall()
        conn.close()

        if len(all_results) == 0: return

        if uid is not None:
            rids = [r[0] for r in all_results]
            top_rid = self._get_venue_by_rids(uid, rids)[0]
            for r in all_results:
                if r[0] == top_rid:
                    result = r
                    break
        else:
            result = all_results[0]

        rid = result[0]
        venue['rid'] = result[0]  #  rid
        venue['venue_name'] = result[1] #  biz_name
        venue['venue_food'] = result[2] #  the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['mrt'] = result[5]  # mrt
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,rid)

        self.retrieved_biz.extend([venue])
        self.retrieved_biz_type.extend(['food_venue_type'])

        return venue

    def get_random_venue(self,parsed_dict, uid=None):

        venue = {
            'rid': '',
            'venue_name': '',
            'venue_food': '',
            'venue_type': '',
            'mrt': '',
            'statement': '',
            'rating': ''
        }

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT DISTINCT v.rid, v.venue_name, f.food, v.venue_type, v.rating, v.mrt_name FROM venues v " \
                  "INNER JOIN venues_food f ON v.rid = f.rid WHERE 1 = 1 " + \
                  exclude_str + " " + \
                  "ORDER BY v.rating DESC;"

        print('get_random_venue --- ', sql_str)
        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        all_results = c.fetchall()
        conn.close()

        if len(all_results) == 0: return

        if uid is not None:
            top_rid = self._get_venue_by_uid(uid)[0]
            for r in all_results:
                if r[0] == top_rid:
                    result = r
                    break
        else:
            result = all_results[0]


        rid = result[0]
        venue['rid'] = result[0]  # rid
        venue['venue_name'] = result[1]  # biz_name
        venue['venue_food'] = result[2]  # the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['mrt'] = result[5]  # mrt
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict,rid)

        self.retrieved_biz.extend([venue])

        return venue

    def get_random_similar_stmt_by_biz(self,parsed_dict,rid):

        statement = ''

        # Step 1: Select all statements
        sql_str = "SELECT t.rid, t.tip FROM tips t " \
                  "WHERE t.rid = '{0}' ORDER BY t.senti_score DESC LIMIT 10;".format(rid)

        print('get_random_similar_stmt_by_biz --- ', sql_str)

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
        sql_str = "SELECT tip, tok_tip FROM tips WHERE tok_tip IS NOT NULL ORDER BY RANDOM() LIMIT 500" #

        print('get_random_similar_stmt --- ', sql_str)


        results = []
        tokenized_docs = []

        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        for row in c.execute(sql_str):
            try:
                tokenized_docs.append(row[1].split('|'))
                results.append(row[0])

            except:
                print('error getting random similar statement')

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

    def get_similar_venue_by_name(self,parsed_dict, requested, uid=None):

        venue = {}
        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT v.rid, v.venue_name, f.food, v.venue_type, v.rating, v.mrt_name FROM venues v " \
                  "INNER JOIN venues_food f ON v.rid = f.rid " \
                  "WHERE 1 = 1 " \
                  "AND v.venue_name LIKE '%{0}%' ".format(requested) + " " + exclude_str + " " + \
                  "ORDER BY v.rating DESC;"

        print('get_similar_venue_by_name --- ', sql_str)

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        all_results = c.fetchall()
        conn.close()

        if len(all_results) == 0: return

        if uid is not None:
            rids = [r[0] for r in all_results]
            top_rid = self._get_venue_by_rids(uid, rids)[0]
            for r in all_results:
                if r[0] == top_rid:
                    result = r
                    break
        else:
            result = all_results[0]

        rid = result[0]
        venue['rid'] = result[0]  # rid
        venue['venue_name'] = result[1]  # biz_name
        venue['venue_food'] = result[2]  # the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['mrt'] = result[5]  # mrt
        venue['statement'] = self.get_random_similar_stmt_by_biz(parsed_dict, rid)

        self.retrieved_biz.extend([venue])

        conn.close()

        return venue

    def get_similar_venue_by_review(self,parsed_dict,requested, uid=None):

        venuees = []
        venue = {}

        exclude_str = self._get_rid_exclude_str()

        sql_str = "SELECT v.rid, v.venue_name, f.food, v.venue_type, v.rating, v.mrt_name FROM venues v " \
                  "INNER JOIN venues_food f ON v.rid = f.rid " \
                  "WHERE 1 = 1 " \
                  "AND v.rid IN (SELECT DISTINCT(t.rid) FROM tips t WHERE t.tip LIKE '%" + requested + "%')" + \
                  " " + exclude_str + " " + \
                  "ORDER BY v.rating DESC;"

        print('get_similar_venue_by_review --- ', sql_str)
        # print(sql_str.encode(encoding='UTF-8',errors='strict'))

        # connect and get the result
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        all_results = c.fetchall()
        conn.close()

        if len(all_results) == 0: return

        if uid is not None:
            rids = [r[0] for r in all_results]
            top_rid = self._get_venue_by_rids(uid, rids)[0]
            for r in all_results:
                if r[0] == top_rid:
                    result = r
                    break
        else:
            result = all_results[0]

        rid = result[0]
        venue['rid'] = result[0]  # rid
        venue['venue_name'] = result[1]  # biz_name
        venue['venue_food'] = result[2]  # the type of food they serve
        venue['venue_type'] = result[3]  # the type of food they serve
        venue['rating'] = result[4]  # rating
        venue['mrt'] = result[5]  # mrt
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

    def _get_degree_weighted_centrality(self, G, nodes=None, alpha=0.5):

        dw_centrality = {}

        if nodes == None:  # if no nodes specified, calculate for every damn node
            nodes = G.nodes()

        for n in nodes:

            w = 0
            for e in G.edge[n].values():
                w += e['weight']

            k = len(G.edge[n].values()) ** (1 - alpha)
            s = w ** alpha
            dw_centrality[n] = np.round(k * s, 3)

        return (dw_centrality)

    def _get_venue_by_rids(self, uid, rids):

        print('recommending _get_venue_by_rids ... ')
        sub_graph_nodes = []
        sub_venue_nodes = []
        for rid in rids:
            sub_graph_nodes.extend([rid])
            sub_graph_nodes.extend(self.g.neighbors(rid))
            sub_venue_nodes.extend(self.g.neighbors(rid))

        sub_graph = self.g.subgraph(sub_graph_nodes)

        # fetch the clus_id
        sql_str = "SELECT kmn_clus_id FROM users WHERE uid = {0}".format(uid)
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        clus_id = result[0]
        clus_sub_graph_nodes = []
        clus_venue_nodes = []

        for n, d in sub_graph.nodes(data=True):

            if d['bipartite'] == 0 and d['clus_id'] == clus_id:
                clus_sub_graph_nodes.extend([n])
                clus_sub_graph_nodes.extend(sub_graph.neighbors(n))
                clus_venue_nodes.extend(sub_graph.neighbors(n))

        if len(clus_sub_graph_nodes) != 0:
            # get sub graph
            clus_sub_graph = sub_graph.subgraph(clus_sub_graph_nodes)
            dw = self._get_degree_weighted_centrality(clus_sub_graph, nodes=clus_venue_nodes)
        else:
            dw = self._get_degree_weighted_centrality(sub_graph, nodes=clus_venue_nodes)

        top_rid = sorted(dw.items(), key=operator.itemgetter(1), reverse=True)[0]
        
        return(top_rid)

    def _get_venue_by_uid(self, uid):

        print('recommending _get_venue_by_uid ... ')

        # fetch the clus_id
        sql_str = "SELECT kmn_clus_id FROM users WHERE uid = {0}".format(uid)
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute(sql_str)
        result = c.fetchone()
        conn.close()

        clus_id = result[0]

        # get nodes of cluster
        sub_graph_nodes = []
        sub_venue_nodes = []

        for n, d in self.g.nodes(data=True):

            if d['bipartite'] == 0 and d['clus_id'] == clus_id:
                sub_graph_nodes.extend([n])
                sub_graph_nodes.extend(self.g.neighbors(n))
                sub_venue_nodes.extend(self.g.neighbors(n))

        sub_graph = self.g.subgraph(sub_graph_nodes)
        dw = self._get_degree_weighted_centrality(sub_graph, nodes=sub_venue_nodes)

        top_rid = sorted(dw.items(), key=operator.itemgetter(1), reverse=True)[0]

        return(top_rid)

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

# parsed_dict = {'tokens': ['you', 'know', 'of', 'any', 'place', 'for', 'japanese', 'or', 'sells', 'burgers', '?']}
# print(r.get_venue_by_food(parsed_dict,'burgers'))
# print(r.get_similar_venue('burgers'))

# r.get_random_similar_stmt("i like to eat healthy")