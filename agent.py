
""" agent.py
Releases:
2021-09-22a BOT0 - IDLE BOT     : Default RULE based agent that uses the starting worker to collect resources
2021-09-23a BOT2 - RESEARCH BOT : Agent now launches research action when city can use an action. Code cleanup
2021-09-24a Move rules to Rule.py Rule class
2021-09-25
"""

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

import math
import pickle
import logging
#used to estimate resource use of the agent
from time import perf_counter

#efficient nested loops
from itertools import product

#import game constant and make them available to the program
from lux.constants import Constants
DIRECTIONS = Constants.DIRECTIONS
INPUT_CONSTANTS = Constants.INPUT_CONSTANTS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from lux.game_map import Cell

from lux.game import Game

from lux import annotate

#Import the rule processor for the rule based agent
from rule import Rule

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

##  agent function
#   processes inputs into a Game() class
#   launches execution of Rule processor
#   returns actions
def agent(observation, configuration):

    #--------------------------------------------------------------------------------------------------------------------------------
    #   Process input observations into a Game() class
    #--------------------------------------------------------------------------------------------------------------------------------

    global game_state

    ### Do not edit ###
    if observation[INPUT_CONSTANTS.STEP] == 0:
        game_state = Game()
        game_state._initialize(observation[INPUT_CONSTANTS.UPDATES])
        game_state._update(observation[INPUT_CONSTANTS.UPDATES][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation[INPUT_CONSTANTS.UPDATES])

    #--------------------------------------------------------------------------------------------------------------------------------
    #   Game wide parameters
    #--------------------------------------------------------------------------------------------------------------------------------

    #compute the size of the map.
    width, height = game_state.map.width, game_state.map.height
    #compute which player is assigned to this agent, and which player is assigned to the opponent's agent
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]

    logging.debug(f"Turn {game_state.turn} | {player}")

    #--------------------------------------------------------------------------------------------------------------------------------
    #   Agent Rule Processor
    #--------------------------------------------------------------------------------------------------------------------------------

    #during the first turn, save the game state to file
    if ((game_state.turn == 1) and (X_PICKLE_SAVE_GAME_STATE == True)):
        save_game_state( game_state, "pickle_dump_game_state.bin" )

    #initialize rule processor with the game state
    agent_rule_processor = Rule( game_state.map, player, opponent )
    #ask the rule processor to come up with a list of actions
    agent_actions = agent_rule_processor.compute_actions()
    logging.debug(f"Actions: {agent_actions}")

    #--------------------------------------------------------------------------------------------------------------------------------
    #   CITY RULES
    #--------------------------------------------------------------------------------------------------------------------------------
    """
    #iterate over all cities.
    for index, my_city in player.cities.items():
        #iterate over all city tiles that make up an individual city
        for my_city_tile in my_city.citytiles:
            #if the city can act
            if my_city_tile.can_act() == True:
                #have the city tile research
                logging.debug(f"Research: {my_city_tile}")
                actions.append( my_city_tile.research() )

    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    """
    return agent_actions
