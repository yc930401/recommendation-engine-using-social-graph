import configparser
import json
import random
from retriever import Retriever
from state_machine import StateMachine, State

# Responder
# ------------------------------------------------------------------------------
class Responder:

    def __init__(self,config, config_key):

        self.config = config
        self.config_key = config_key

        # For Understanding User Inputs
        self.input_yes_or_no = json.load(open(config[config_key]['input_yes_or_no']))
        self.input_about = json.load(open(config[config_key]['input_about']))
        self.location_file_path = config[config_key]['location']
        self.cuisine_file_path = config[config_key]['cuisine']
        self.food_file_path = config[config_key]['food']

        # For Generating Responses
        self.response_greetings = json.load(open(config[config_key]['response_greetings']))
        self.response_yes_no = json.load(open(config[config_key]['response_yes_no']))
        self.response_about = json.load(open(config[config_key]['response_about']))
        self.response_general = json.load(open(config[config_key]['response_general']))
        self.response_for_business = json.load(open(config[config_key]['response_for_business']))

        # Helpers
        self.retriever = Retriever(config, config_key)

        # read in valid locations
        with open(self.location_file_path,'r') as location_file:
            self.valid_locations = [location.lower() for location in location_file.read().splitlines()]


        # read in cuisines
        with open(self.cuisine_file_path, 'r') as cuisine_file:
            self.known_cuisines = [cuisine.lower() for cuisine in cuisine_file.read().splitlines()]

        # read in food
        with open(self.food_file_path, 'r') as food_file:
            known_foods = [food.lower() for food in food_file.read().splitlines()]


        self.state_after_response = State.understood_nothing

    def get_response(self, parsed_dict, state, context, history, uid=None):

        # Initialization
        self.state_after_response = state

        # Understanding using input
        abt_question = True if parsed_dict['input_type'] == 'question' else False
        abt_intent = True if set(parsed_dict['tokens']) & set(self.input_about['intent']) else False
        abt_statement = True if parsed_dict['input_type'] == 'statement' else False
        abt_rhetoric = True if parsed_dict['input_type'] == 'rhetoric' else False
        abt_greeting = True if set(parsed_dict['tokens']) & set(self.response_greetings.keys()) else False
        abt_bot = True if set(parsed_dict['pronouns']) & set(self.input_about['bot']) or \
                          set(parsed_dict['nouns']) & set(self.input_about['bot']) else False
        abt_user = True if set(parsed_dict['pronouns']) & set(self.input_about['user']) or \
                           set(parsed_dict['nouns']) & set(self.input_about['user']) else False
        abt_yes = True if set(parsed_dict['tokens']) & set(self.input_yes_or_no['yes']) else False
        abt_no = True if set(parsed_dict['tokens']) & set(self.input_yes_or_no['no']) else False

        # ---------------------------------------------------------
        # Begin construction of response
        # ---------------------------------------------------------

        response = ''

        # (STATE) UNDERSTOOD NOTHING - MAY BE GREETING, ABOUT BOT, OR SOMETHING RANDOM
        # ---------------------------------------------------------
        if state == State.understood_nothing:

            # use classifier to determine the type of input
            # ---------------------------------------------------
            if abt_statement:

                if abt_greeting: # Greet if greeting
                    greeting = set(parsed_dict['tokens']) & set(self.response_greetings.keys())
                    response = random.choice(self.response_greetings[greeting.pop()])

                elif abt_user:  # Talk about user
                    response = random.choice(self.response_about['user'])

                elif abt_bot: # Talk about jiakbot
                    response = random.choice(self.response_about['bot'])

                elif abt_yes: # yes to anything
                    response = random.choice(self.response_yes_no['yes_generic'])

                elif abt_no:  # no to anything
                    response = random.choice(self.response_yes_no['no_generic'])

                else:
                    response = self.retriever.get_random_similar_stmt(parsed_dict['input_text'])
                    if response == None:
                        response = random.choice(self.response_general['generic'])

            # if user asks a question
            elif abt_question:
                response = random.choice(self.response_general['question'])

            # some random rhetoric question
            elif abt_rhetoric:
                response = random.choice(self.response_general['rhetoric'])

            # if user asks to recommend override everything else
            # -----------------
            if abt_intent:
                response = random.choice(self.response_general['recommend'])


            return response

        # (STATE) UNDERSTOOD LOCATION - LOCATION MAY OR MAY NOT BE CORRECT
        # ---------------------------------------------------------
        elif state == State.understood_location:

            # Check if location is known and valid
            if context['locations'][0] not in self.valid_locations:
                response = random.choice(self.response_general['unknown_location'])
            else:
                result = self.retriever.get_random_venue(parsed_dict, uid)
                response = self._format_response_with_biz(result)

                # Update internal state
                self.state_after_response = State.provided_initial_result

            return response

        # (STATE) UNDERSTOOD FOOD CUISINE - RETRIEVE SOMETHING FROM DB
        # ---------------------------------------------------------
        elif state == State.understood_food_cuisine:

            guessed = False

            requested_food = context['foods'][0] if len(context['foods']) > 0 else None
            requested_cuisine = context['cuisines'][0] if len(context['cuisines']) > 0 else None

            # Attempt to get food / cuisine based what user wants
            if requested_food and not requested_cuisine:
                result = self.retriever.get_venue_by_food(parsed_dict,requested_food, uid)
            elif requested_cuisine and not requested_food:
                result = self.retriever.get_venue_by_venue_type(parsed_dict,requested_cuisine, uid)
            elif requested_food and requested_cuisine:
                result = self.retriever.get_venue_by_food_venue_type(parsed_dict,requested_food, requested_cuisine, uid)

            # If no result attempt to get similar stuff based on biz name
            if not result:
                requested = requested_food if requested_food else requested_cuisine
                result = self.retriever.get_similar_venue_by_name(parsed_dict,requested, uid)

            # Lastly attempt to get similar stuff based on review text
            if not result:
                requested = requested_food if requested_food else requested_cuisine
                result = self.retriever.get_similar_venue_by_review(parsed_dict,requested, uid)
                guessed = True

            # Construct the response for guessed response
            if result and guessed:
                response = self._format_response_with_guessed_biz(result, requested, uid)
                self.state_after_response = State.provided_initial_result  # Update internal state

            # Construct the response for non-guessed response
            elif result:
                response = self._format_response_with_biz(result)
                self.state_after_response = State.provided_initial_result  # Update internal state

            # Construct the response for no result
            else:
                response = random.choice(self.response_general['no_result'])
                self.state_after_response = State.provided_no_result  # Update internal state

            return response

        # (STATE) PROVIDED NO RESULT - GETTING FEEDBACK OR WIPE STATE
        # ---------------------------------------------------------
        elif state == State.provided_no_result:

            answered_yes = False
            answered_no = False
            answered_something_else = False

            # Checks what the user answers
            for word in parsed_dict['tokens']:
                if word in self.input_yes_or_no['yes']:
                    answered_yes = True
                    break
                elif word in self.input_yes_or_no['no']:
                    answered_no = True
                    break
                else:
                    answered_something_else = True

            if answered_yes:
                response = random.choice(self.response_general['request_food_cuisine'])
                self.state_after_response = State.understood_nothing
            else:
                response = random.choice(self.response_general['unknown_food_cuisine'])
                self.state_after_response = State.understood_nothing  # Update internal state

            return response

        # (STATE) PROVIDED INITIAL RESULT - GETTING FEEDBACK OR WIPE STATE
        # ---------------------------------------------------------
        elif state == State.provided_initial_result:

            response = None
            answered_yes = False
            answered_no = False
            answered_something_else = False

            # Checks what the user answers
            for word in parsed_dict['tokens']:
                if word in self.input_yes_or_no['yes']:
                    answered_yes = True
                    break
                elif word in self.input_yes_or_no['no']:
                    answered_no = True
                    break
                else:
                    answered_something_else = True

            # Based on the answer perform stuff
            if answered_yes:
                response = random.choice(self.response_yes_no['yes_after_result'])
                self.state_after_response = State.understood_nothing

            if answered_no:
                history_food_cuisine = []

                for state,context in history:
                    if state == State.provided_initial_result:
                        history_food_cuisine.append(context['foods'][0]) if len(context['foods']) > 0 else None
                        history_food_cuisine.append(context['cuisines'][0]) if len(context['cuisines']) > 0 else None

                for fc in history_food_cuisine:
                    result = self.retriever.get_similar_venue_by_review(parsed_dict, fc, uid)

                    if result is not None:
                        response = self._format_response_with_guessed_biz(result, fc)
                        self.state_after_response = State.provided_revised_result
                        break

                    else:
                        response = random.choice(self.response_general['no_result'])
                        self.state_after_response = State.provided_revised_result

            if answered_something_else:
                response = random.choice(self.response_general['request_yes_no'])

            return response

        # (STATE) PROVIDED REVISED RESULT - IF DON'T LIKE WIPE STATE
        # ---------------------------------------------------------
        elif state == State.provided_revised_result:

            # Checks if the user says yes
            for word in parsed_dict['tokens']:
                give_up = False if word in self.input_yes_or_no['yes'] else True

            response = random.choice(self.response_yes_no['repeated_no_response']) if give_up else random.choice(response_yes_no['yes_after_result'])
            self.state_after_response = State.understood_nothing

        return response

    def _format_response_with_biz(self,business):

        response = random.choice(self.response_for_business['with_biz']).format(biz_name=business['venue_name'],
                                                                           category=business['venue_type'].lower(),
                                                                           statement=business['statement'],
                                                                           rating=business['rating'])
        return response

    def _format_response_with_guessed_biz(self,business, kw):
        response = random.choice(self.response_for_business['with_guessed_biz']).format(biz_name=business['venue_name'],
                                                                                   category=business['venue_type'].lower(),
                                                                                   kw=kw)

        return response
