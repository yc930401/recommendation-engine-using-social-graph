import logging
import configparser

# import jiakbot helpers
from state_machine import StateMachine
from jiakbot_parser import JiakBotParser
from responder import Responder

# set up logger
logging.basicConfig()
logger = logging.getLogger()

# INFO to switch display all logs. WARNING to display only warning
logger.setLevel(logging.WARNING)

class JiakBot:

    # Read in the config in the auth files
    config_file_path = 'D:/Workspace-Github/saproject/code/99_bot/jiakbot/config_app/app_config.ini'
    config = configparser.ConfigParser()
    config.read(config_file_path)
    config_key = 'yangcheng'

    jiakbot_parser = JiakBotParser(config, config_key)
    state_machine = StateMachine(config, config_key)
    responder = Responder(config, config_key)

    # Initializer
    def __init__(self):
        pass

    # Public function to respond
    # -----------------------------------------------------
    def respond(self, sentence):

        p = self.jiakbot_parser
        sm = self.state_machine
        r = self.responder

        response = ''

        # get the parsed dict
        parsed_dict = p.parse_input(sentence)

        # get the current state
        sm.update_state(parsed_dict)

        # get the response
        response = r.get_response(parsed_dict, sm.state,sm.context,sm.history)

        if sm.state != r.state_after_response:
            sm.update_state_after_response(r.state_after_response)

        print('-----  DEBUGGING  -----')
        print('parsed_dict:', parsed_dict)
        print('state:',sm.state)
        print('context', sm.context)
        print('----- ----- ----- -----')

        return(response)

