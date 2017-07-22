from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from sklearn.externals import joblib
import re
import numpy as np

class JiakBotParser:

    def __init__(self,config, config_key):

        self.config = config
        self.config_key = config_key

        self.question_clf = joblib.load(config[config_key]['question_clf'])

    def parse_input(self, user_input):
        parsed_dict = {'tokens': word_tokenize(user_input.lower()),
                       'input_text': user_input,
                       'cleansed_text': None,
                       'verbs': [],
                       'adverbs': [],
                       'nouns': [],
                       'adjs': [],
                       'pronouns': [],
                       'input_type': []}

        tagged = pos_tag(parsed_dict['tokens'])

        parsed_dict['verbs'] = [word for word, pos in tagged \
                                if (
                                pos == 'VB' or pos == 'VBZ' or pos == 'VBD' or pos == 'VBN' or pos == 'VBG' or pos == 'VBP')]

        parsed_dict['adverbs'] = [word for word, pos in tagged \
                                  if (pos == 'RB' or pos == 'RBR' or pos == 'RBS' or pos == 'WRB')]

        parsed_dict['nouns'] = [word for word, pos in tagged \
                                if (pos == 'NN' or pos == 'NNS' or pos == 'NNP' or pos == 'NNPS')]

        parsed_dict['adjs'] = [word for word, pos in tagged \
                               if (pos == 'JJ' or pos == 'JJR' or pos == 'JJS')]

        parsed_dict['pronouns'] = [word for word, pos in tagged \
                                   if (pos == 'PRP' or pos == 'PRP$' or pos == 'WP' or pos == 'WP$')]

        
        stop_list = stopwords.words('english')
        words = [w for w in parsed_dict['tokens'] if re.search('^[a-z]+$', w)]
        parsed_dict['cleansed_text'] = [w for w in words if w not in stop_list]

        #######################################################################
        # predicting question / rhetoric / statements

        where_features = ['where is', 'where are', 'where can', 'where was', 'where you', 'where to', 'where']
        who_features = ['who is', 'who was', 'who are', 'who were', 'who to', 'who did', 'who do', 'who']
        what_features = ['what is', 'what was', 'what are', 'what were', 'what to', 'what did', 'what do', 'what']
        when_features = ['when is', 'when was', 'when are', 'when were', 'when to', 'when did', 'when do', 'when']
        why_features = ['why is', 'why was', 'why are', 'why were', 'why did', 'why do', 'why']
        which_features = ['which is', 'which was', 'which are', 'which were', 'which did', 'which do', 'which']
        how_features = ['how is', 'how was', 'how are', 'how were', 'how did', 'how do', 'how']
        would_features = ['why would', 'would i', 'would you']
        can_features = ['can you', 'could you', 'could i']
        qm = ['\\?']

        features = where_features + who_features + \
                   what_features + when_features + why_features + which_features + \
                   how_features + would_features + can_features + qm

        # empty vector
        vector = []

        # create custom feature vector with label
        for feature in features:

            # match against the feature
            match = re.search(feature, user_input.lower())

            if match is not None:
                vector.extend([1])
            else:
                vector.extend([0])

        input_vector = np.array(vector).reshape(1,-1)
        parsed_dict['input_type'] = self.question_clf.predict(input_vector)[0]

        # print(user_input,self.question_clf.predict(input_vector)[0])
        #######################################################################
        return parsed_dict

# jbp = JiakBotParser()
# jbp.parse_input("why would i care?")
# jbp.parse_input("where can i find good noodles?")
# print(jbp.parse_input("you know of any place for japanese or sells burgers?"))
# jbp.parse_input("chicken rice nice or not?")
# jbp.parse_input("what is nice at raffles place?")
# jbp.parse_input("can you recommend where to find good coffee")
