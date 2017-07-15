# sample user_info_dict
user_info_dict = {
    'friends':[123,234,345,456,234,123,4523],
    'venues':['asdfasdf','asdfasdf','asdfasdf','asdfasdfasd','asdfasdf'], # Same length as venue rating
    'venue_rating':[1,2,4,2,4,6,5] # same length as venues
}

def get_user_cluster(user_info_dict):

    # return format
    cluster_dict = {
        'kmeans':None,
        'spec':None,
        'hier':None,
        'train_stn':None
    }

    # Read from model folder using pickle or joblib
    # http://machinelearningmastery.com/save-load-machine-learning-models-python-scikit-learn/

    # Get the clusters and assign it to the dictionary


    # Return the dictionary
    return(cluster_dict)

