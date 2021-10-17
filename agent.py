
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

from big_no_brainer.perception import Perception
from big_no_brainer.action import Action

#--------------------------------------------------------------------------------------------------------------------------------
#   CONSTANTS(fake)
#--------------------------------------------------------------------------------------------------------------------------------

#True: save the game state at first turn with pickle
X_PICKLE_SAVE_GAME_STATE = False

#--------------------------------------------------------------------------------------------------------------------------------
#   
#--------------------------------------------------------------------------------------------------------------------------------

global lc_perceptions
lc_perceptions = list()

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

#Game() class that holds all processed observations
game_state = None

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

	logging.info(f"map size: {game_state.map_height}*{game_state.map_width}")

	#compute which player is assigned to this agent, and which player is assigned to the opponent's agent
	player = game_state.players[game_state.id]
	opponent = game_state.players[game_state.opponent_id]
	logging.debug(f"Turn {game_state.turn} | Player {game_state.id} {player}")

	#--------------------------------------------------------------------------------------------------------------------------------
	#   Agent 
	#--------------------------------------------------------------------------------------------------------------------------------

	#construct Perception() matricies from a Game() gamestate class
	c_perception = Perception()
	c_perception.from_game( game_state )

	#--------------------------------------------------------------------------------------------------------------------------------
	# 	BNB Big No Brainer network
	#--------------------------------------------------------------------------------------------------------------------------------

	#generates a virgin action
	c_action = Action()
	agent_actions = c_action.translate()
	
	logging.debug(f"Actions: {agent_actions}")
	return agent_actions
