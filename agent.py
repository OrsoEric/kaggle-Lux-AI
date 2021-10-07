
""" agent.py
Releases:
2021-09-22a BOT0 - IDLE BOT     : Default RULE based agent that uses the starting worker to collect resources
2021-09-23a BOT2 - RESEARCH BOT : Agent now launches research action when city can use an action. Code cleanup
2021-09-24a Move rules to Rule.py Rule class
2021-09-25
2021-10-10 
"""

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

import math
import pickle
import logging
#used to estimate resource use of the agent
from time import perf_counter

#import game constant and make them available to the program
from lux.constants import Constants
DIRECTIONS = Constants.DIRECTIONS
INPUT_CONSTANTS = Constants.INPUT_CONSTANTS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from lux.game import Game

#Import the rule processor for the rule based agent
from rule import Rule

from big_no_brainer import Perception

#--------------------------------------------------------------------------------------------------------------------------------
#   CONSTANTS(fake)
#--------------------------------------------------------------------------------------------------------------------------------

#True: save the game state at first turn with pickle
X_PICKLE_SAVE_GAME_STATE = False

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

#Game() class that holds all processed observations
game_state = None

##  save a game state to file
#   uses pickle
def save_game_state( ic_game_state : Game(), is_file_name : str() ) -> bool:
    """save a game state to file
    Args:
        ic_game_state (Game): game state to be saved
        is_file_name (str): destination file name 
    Returns:
        bool: false: success | true: fail
    """
    
    try:
        with open(is_file_name, "wb") as opened_file:
            pickle.dump( ic_game_state, opened_file )

    except OSError as problem:
        logging.critical(f"Pickle: {problem}")
        return True

    return False

##  load a game state to file
#   uses pickle
def load_game_state( is_file_name : str() ) -> Game:
    """load a game state to file
    Args:
        is_file_name (str): source file name 
    Returns:
        Game: loaded game state
    """
    
    try:
        with open(is_file_name, "rb") as opened_file:
            ic_game_state = pickle.load( opened_file )

    except OSError as problem:
        logging.critical(f"Pickle: {problem}")
        return None

    return ic_game_state

##  agent function
#   processes inputs into a Game() class
#   launches execution of Rule processor
#   returns actions
#	DO NOT CHANGE THE INTERFACE!!! Locally execution is from main.py, on kaggle agent() is called directly
def agent( observation , configurations ):

	#--------------------------------------------------------------------------------------------------------------------------------
	#   Process input observations into a Game() class
	#--------------------------------------------------------------------------------------------------------------------------------

	global game_state

	if observation[INPUT_CONSTANTS.STEP] == 0:
		game_state = Game()
		game_state._initialize(observation[INPUT_CONSTANTS.UPDATES])
		game_state._update(observation[INPUT_CONSTANTS.UPDATES][2:])
		game_state._set_player_id( observation.player )

	else:
		game_state._update(observation[INPUT_CONSTANTS.UPDATES])

	#--------------------------------------------------------------------------------------------------------------------------------
	#   Game wide parameters
	#--------------------------------------------------------------------------------------------------------------------------------

	#compute which player is assigned to this agent, and which player is assigned to the opponent's agent
	player = game_state.players[game_state.id]
	opponent = game_state.players[game_state.opponent_id]
	logging.debug(f"Turn {game_state.turn} | Player {game_state.id} {player}")

	#--------------------------------------------------------------------------------------------------------------------------------
	#   Agent Rule Processor
	#--------------------------------------------------------------------------------------------------------------------------------

	#during the first turn, save the game state to file
	if ((game_state.turn == 0) and (X_PICKLE_SAVE_GAME_STATE == True)):
		save_game_state( game_state, "pickle_dump_game_state.bin" )

	#initialize rule processor with the game state
	#agent_rule_processor = Rule( game_state.map, player, opponent )
	agent_rule_processor = Rule( game_state )
	#ask the rule processor to come up with a list of actions
	agent_actions = agent_rule_processor.compute_actions()
	logging.debug(f"Actions: {agent_actions}")

	return agent_actions, Perception(game_state)
