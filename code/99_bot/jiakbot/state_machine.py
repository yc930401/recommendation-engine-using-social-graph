import nltk, re
from enum import Enum
import copy, configparser

class State(Enum):
    understood_nothing = 1
    understood_location = 2
    understood_food_cuisine = 3
    provided_initial_result = 4
    provided_revised_result = 5
    provided_no_result = 6
    provided_guess = 7
    provided_guess_result = 8

class StateMachine():

    def __init__(self,config, config_key):

        self.config = config
        self.config_key = config_key

        location_file_path = config[config_key]['location']
        cuisine_file_path = config[config_key]['cuisine']
        food_file_path = config[config_key]['food']
        non_food_file_path = config[config_key]['non_food']

        self.state = State.understood_nothing

        self.context = {
            'cuisines': [],
            'foods': [],
            'locations': []
        }

        self.history = []

        # read in locations
        self.location_file = open(location_file_path,'r')
        self.known_locations = [location.lower() for location in self.location_file.read().splitlines()]
        self.location_file.close()

        # read in cuisines
        self.cuisine_file = open(cuisine_file_path, 'r')
        self.known_cuisines = [cuisine.lower() for cuisine in self.cuisine_file.read().splitlines()]
        self.cuisine_file.close()

        # read in food
        self.food_file = open(food_file_path, 'r')
        self.known_foods = [food.lower() for food in self.food_file.read().splitlines()]
        self.food_file.close()

        # custom non food words
        self.non_food_file = open(non_food_file_path, 'r')
        self.non_food_words = [non_food.lower() for non_food in self.non_food_file.read().splitlines()]
        self.non_food_file.close()

    def update_state(self, parsed_dict):

        self.context['foods'] = []
        self.context['cuisines'] = []
        self.context['locations'] = []
        self.context['guessed_foods'] = []

        tagged = nltk.pos_tag(nltk.word_tokenize(parsed_dict['input_text']))

        # define the grammar. FP = Food Phrase. LP = Location Phrase
        grammar = r"""
            FP:
                {<VB.*><JJ.*|IN>?<RB>?<NN.*>+}
                {<DT><JJ.*>?<NN.*>+}
                {<CC><JJ.*>?<NN.*>+}
                {<JJ><NN>}

            LP:
                {<IN|TO><NN.*>+<VB.*|RB>?}
                {<IN|TO><JJ.*>?<NN.*>+?}
                {<NN.*>+<VBP>?}
        """

        cp = nltk.RegexpParser(grammar)
        result = cp.parse(tagged)
        print('state machine', result)

        # ----------------------------------------------------------------------------
        # Identify cuisines and/or food items from user input
        # food and cuisine identified together and then separated
        # ----------------------------------------------------------------------------
        identified_food_cuisines = []

        for subtree in result.subtrees(filter=lambda t: t.label() == 'FP'):
            leaves = subtree.leaves()
            food_cuisines = [w for (w, t) in leaves if re.search(r"(JJ.*|RB|NN.*)", t) and w not in self.non_food_words]
            food_cuisines = ' '.join(food_cuisines)
            if food_cuisines != '':
                identified_food_cuisines.append(food_cuisines.lower())

        # ----------------------------------------------------------------------------
        # identifying location
        # ----------------------------------------------------------------------------

        identified_locations = []

        for subtree in result.subtrees(filter=lambda t: t.label() == 'LP'):
            leaves = subtree.leaves()
            locations = [w for (w, t) in leaves if re.search(r"(JJ.*|NN.*|VB.*|RB)", t)]
            locations = ' '.join(locations)
            identified_locations.append(locations.lower())

        # ----------------------------------------------------------------------------
        # for detected locations, check if its actually a food
        # ----------------------------------------------------------------------------

        not_location = [location.lower() for location in identified_locations if location.lower() not in self.known_locations]

        if len(not_location) > 0:
            retag = nltk.pos_tag(nltk.word_tokenize(', '.join(not_location)))

            f_grammar = r"""
                FP:
                    {<JJ>?<NN>+}
            """

            fcp = nltk.RegexpParser(f_grammar)
            result = fcp.parse(retag)

            for subtree in result.subtrees(filter=lambda t: t.label() == 'FP'):
                leaves = subtree.leaves()
                food_cuisines = [w for (w,t) in leaves if re.search(r"(JJ|NN)", t) and w not in self.non_food_words]
                food_cuisines = ' '.join(food_cuisines)
                if food_cuisines != '':
                    identified_food_cuisines.extend([food_cuisines.lower()])

        # ----------------------------------------------------------------------------
        # for detected locations, check if its actually a food
        # ----------------------------------------------------------------------------

        not_food = [food.lower() for food in identified_food_cuisines if food.lower() in self.known_locations]

        if len(not_food) > 0:

            retag = nltk.pos_tag(nltk.word_tokenize(', '.join(not_food)))

            f_grammar = r"""
                    FP:
                        {<JJ>?<NN.*>+}
                """

            fcp = nltk.RegexpParser(f_grammar)
            result = fcp.parse(retag)

            for subtree in result.subtrees(filter=lambda t: t.label() == 'FP'):
                leaves = subtree.leaves()
                location = [w for (w, t) in leaves if re.search(r"(JJ|NN.*)", t)]
                location = ' '.join(location)
                if location != '':
                    identified_food_cuisines.remove(location)
                    identified_locations.extend([location.lower()])

        # ----------------------------------------------------------------------------
        # finalize the identified lists
        # ----------------------------------------------------------------------------

        identified_foods = [phrase for phrase in identified_food_cuisines if phrase.lower() not in self.known_cuisines]
        identified_cuisines = [phrase for phrase in identified_food_cuisines if phrase.lower() in self.known_cuisines]
        identified_locations = [phrase for phrase in identified_locations if phrase.lower() not in not_location]
        guessed_foods = []

        for food in self.known_foods:
            for token in parsed_dict['tokens']:
                if re.match('\b(' + token + ')\b', food):
                    guessed_foods.extend([food])

        # ----------------------------------------------------------------------------
        # all the logic to update the states
        # ----------------------------------------------------------------------------

        state_before_update = self.state

        # append to the state
        self.context['foods'].extend(identified_foods)
        self.context['cuisines'].extend(identified_cuisines)
        self.context['locations'].extend(identified_locations)
        self.context['guessed_foods'].extend(guessed_foods)

        # Update the state
        if len(self.context['cuisines']) > 0 or len(self.context['foods']) > 0:
            self.state = State.understood_food_cuisine

        elif len(self.context['locations']) > 0:
            self.state = State.understood_location

        elif len(self.context['guessed_foods']) > 0:
            self.state = State.provided_guess

        # Update history
        curr_state = copy.deepcopy(self.state)
        curr_context = copy.deepcopy(self.context)
        self.history.append((curr_state, curr_context))

        updated = False if self.state == state_before_update else True

        return updated

    def update_state_after_response(self,state):
        self.state = state
        curr_state = copy.deepcopy(self.state)
        curr_context = copy.deepcopy(self.context)

        self.history.append((curr_state, curr_context))

        return None


########################################################
# for testing purposes
########################################################
# sm = StateMachine()
#
# parsed_dict = {'input_text': 'I want to eat at Raffles Place'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
# print(sm.history)
#
# parsed_dict = {'input_text': 'i want to have burgers or japanese food at raffles place'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
# print(sm.history)

# parsed_dict = {'input_text': 'where can i get katong laksa around here?'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'any good tonkatsu or yakitori place nearby?'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'where is a good place for french food'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'got any places serving fish & chips in shenton way'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'what food is good and cheap near simei'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'get me some hot and spicy chicken wings'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'any place serving good porterhouse steaks in marina bay?'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'recommend an Australian barbecue restaurant'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'where can i get authentic seafood paella in city hall'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'any place serving blue mountain coffee?'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'Recommend a spanish tapas place near bugis'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'where can i find cheap szechuan food'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'i want to eat salad today'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'i want a different food place, please recommend?'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'when is the best time to go for lunch in CBD?'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'i want to eat bak kut teh'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'my boss bringing us out for chilli crab or black pepper crab, quick recommend a place'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'i want hawker stalls selling western food'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'where can i find fish head curry in little india'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'i want to have japanese monster curry rice today'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'I am going to Jurong East. Recommend a place for chinese food'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'where can i get the best roti plata in kovan'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'lazy to think what to eat today. recommend anything'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'i want to have beef horfun today'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'where can i get penang char koay teow around dhoby ghaut'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'let us go for pipa duck today'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'my friend suggest to go for chicken rice. where is the nearest place?'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
#
# parsed_dict = {'input_text': 'where can i get pork knuckles with beer the german way'}
# sm.update_state(parsed_dict=parsed_dict)
# print('original statement:', parsed_dict['input_text'])
# print('foods:{0} | cuisines:{1} | locations:{2} {3}'.format(sm.context['foods'],sm.context['cuisines'],sm.context['locations'],'\n'))
