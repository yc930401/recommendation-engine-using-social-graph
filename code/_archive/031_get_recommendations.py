import networkx as nx
import numpy as np
import operator
from collections import Counter
from datetime import datetime

# -----------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------
def getFormattedTime():
    return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def get_degree_weighted_centrality(G, nodes=None, alpha=0.5):

    dw_centrality = {}

    if nodes == None: # if no nodes specified, calculate for every damn node
        nodes = G.nodes()

    for n in nodes:

        w = 0
        for e in G.edge[n].values():
            w += e['weight']

        k = len(G.edge[n].values()) ** (1 - alpha)
        s = w ** alpha
        dw_centrality[n] = np.round(k*s,3)

    return(dw_centrality)

# ----------------------------------------
# RECOMMENDATIONS
# ----------------------------------------
# Note:
#  _history should be in the format [u,v,score]
# where u = uid, v = venue (rid), score = senti_score
# ----------------------------------------

def get_global_recommendation(G,top_n=10):
    venues = []

    # get the restaurants nodes from bipartite graph
    top_nodes = set(n for n,d in G.nodes(data=True) if d['bipartite'] == 0)
    bottom_nodes = set(G) - top_nodes

    # calculate the degree centrality
    dw = get_degree_weighted_centrality(G,nodes=bottom_nodes)

    # sort venues by degree centrality weighted by senti_score
    sorted_dw = sorted(dw.items(), key=operator.itemgetter(1), reverse=True)

    # return top n
    for v,s in sorted_dw[:top_n]:
        venues.append(v)

    return(venues)

# friend_uids = [611228,3441492,32264433,4998202,2686277]
# uid = 1194133

def get_friends_recommendations(G, friend_uids, uid, top_n=10):
    venues = []

    # get the restaurants nodes from bipartite graph
    top_nodes = set(n for n,d in G.nodes(data=True) if d['bipartite'] == 0)
    bottom_nodes = set(G) - top_nodes

    # get cluster with most friends
    friend_clus_ids = [d['clus_id'] for n,d in G.nodes(data=True) if n in friend_uids]
    clus_id_count = dict(Counter(friend_clus_ids))
    top_clus_id = sorted(clus_id_count.items(), key=operator.itemgetter(1), reverse=True)[0]

    # get nodes of cluster
    venue_nodes = [(n,d) for n,d in G.nodes(data=True) if d['bipartite'] == 0]
    clus_nodes = [n for n,d in venue_nodes if d['clus_id'] in top_clus_id]

    neighbors = []
    for node in clus_nodes:
        neighbors.extend(G.neighbors(node))

    clus_nodes.extend(neighbors)

    # get sub graph
    sub_graph = G.subgraph(clus_nodes)

    # check if visited venues are in sub_graph
    visited_venues = G.neighbors(uid)
    visited_venues = [v for v in visited_venues if sub_graph.has_node(v)]

    # get generic recommendation if no visited venues in cluster
    if len(visited_venues) == 0:
        dw_nodes = venue_nodes

    # if visited venues in cluster based it on the neighbours
    else:
        vv_neighbors = []
        for v in visited_venues:
            vv_neighbors.extend(sub_graph.neighbors(v))

        vv_neighbors_venues = []
        for v in vv_neighbors:
            vv_neighbors_venues.extend(sub_graph.neighbors(v))

        dw_nodes = vv_neighbors_venues

    # sort venues by degree centrality weighted by senti_score and return
    dw = get_degree_weighted_centrality(sub_graph,nodes=dw_nodes)

    # sort venues by degree centrality weighted by senti_score
    sorted_dw = sorted(dw.items(), key=operator.itemgetter(1), reverse=True)

    # return top n
    for v,s in sorted_dw[:top_n]:
        venues.append(v)

    return(venues)


def construct_history(G, uid):
    ew = []

    venues = G.neighbors(uid)
    for v in venues:
        ew.append([uid,v,G.get_edge_data(uid, v)['weight']])

    return(ew)

# G = g.copy()
# uid = 1194133
# history = construct_history(G,uid)

def get_recommendation_for_history(G, uid, clus_id, history, top_n=10):

    # NOTES: history is used for evaluation and can be full or recent history
    # minus the latest venue for comparison purposes
    # graph should always be a full graph

    venues = []

    # get nodes of cluster
    sub_graph_nodes = []

    for n,d in G.nodes(data=True):

        if d['bipartite'] == 0 and d['clus_id'] == clus_id:
            sub_graph_nodes.extend([n])
            sub_graph_nodes.extend(G.neighbors(n))

    # get sub graph
    sub_graph = G.subgraph(sub_graph_nodes)
    sub_graph.add_weighted_edges_from(history)

    # check if visited venues are in sub_graph
    visited_venues = sub_graph.neighbors(uid)

    vv_neighbors = []
    for v in visited_venues:
        vv_neighbors.extend(sub_graph.neighbors(v))

    vv_neighbors_venues = []
    for v in vv_neighbors:
        vv_neighbors_venues.extend(sub_graph.neighbors(v))

    dw_nodes = vv_neighbors_venues

    # sort venues by degree centrality weighted by senti_score and return
    dw = get_degree_weighted_centrality(sub_graph, nodes=dw_nodes)

    # sort venues by degree centrality weighted by senti_score
    sorted_dw = sorted(dw.items(), key=operator.itemgetter(1), reverse=True)

    # return top n
    for v, s in sorted_dw[:top_n]:
        venues.append(v)

    return(venues)

def get_venue_by_rids(rids):

def get_venue_by_uid(uid):

# get_recommendation_for_history(G,uid,0,history)
# # ----------------------------------------
# # SAMPLE CODES
# # ----------------------------------------
# dev_ew = [['a', 'b', 4],
#           ['a', 'c', 4],
#           ['b', 'c', 2],
#           ['b', 'e', 1],
#           ['b', 'd', 1],
#           ['e', 'f', 7]]
#
# G = nx.Graph()
# G.add_weighted_edges_from(dev_ew)
#
# # normalized degree centrality
# nx.degree_centrality(G)
#
# # un-normalized degree centrality
# nx.degree(G)
#
# # weighted centrality
# for n in G.nodes():
#     w = 0
#     for e in G.edge[n].values():
#         w += e['weight']
#     print('weight for node',n,'is',w)
# # ----------------------------------------
