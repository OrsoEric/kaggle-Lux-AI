##	@package test_bench
#	test bench is meant to be executed to probe and stimulate agent components
#	a game state is loaded using pickle, bypassing the need to use the NODE.JS game engine

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

import logging

import numpy as np
#plot
import matplotlib.pyplot as plt
import seaborn as sns
#convert input matricies into .gif
import matplotlib.animation as animation
from big_no_brainer.action import Action


from lux.game_map import Position

#pickle game state loader
#from agent import load_game_state

#from agent import agent
#from rule import Rule

from big_no_brainer.perception import Perception
#from big_no_brainer.perception import gify_list_perception
from big_no_brainer.model_tf import bnb_model_tf

#--------------------------------------------------------------------------------------------------------------------------------
#   CONSTANTS(fake)
#--------------------------------------------------------------------------------------------------------------------------------

#----------------    Big No Brainer    ---------------

#depickle a game state, and test the construction of a perception
TEST_BIGNOBRAINER_PERCEPTION = False
TEST_BIGNOBRAINER_PERCEPTION_ANIMATED = False 
TEST_TF_MODEL = True

#--------------------------------------------------------------------------------------------------------------------------------
#   TEST BENCHES
#--------------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------------------------------------
#   BIG NO BRAINER
#--------------------------------------------------------------------------------------------------------------------------------


def test_big_no_brainer_perception( is_file_name : str ) -> bool:
	"""Test the creation of a perception class for the Big No Brainer NN Agent
	Args:
		is_file_name (str): name of the pickled game state
	Returns:
		bool: False = OK | True = Fail 
	"""

	#load game state
	c_game_state = load_game_state( is_file_name )
	if (c_game_state is None):
		logging.critical(f"Failed to load game state >{is_file_name}<")
		return True

	c_game_state.opponent_id = 1-c_game_state.id

	#try to generate a Perception class
	c_perception = Perception( c_game_state )

	logging.debug( c_perception )

	return False



def test_big_no_brainer_perception_animation( ils_file_name : list ) -> bool:
	"""Test the creation of a perception class for the Big No Brainer NN Agent
	Load from a given list of gamestates
	Save on a gif an animation of the heatmaps
	Args:
		is_file_name (str): name of the pickled game state
	Returns:
		bool: False = OK | True = Fail 
	"""

	logging.info(f"Game states: {ils_file_name}")

	#allocate list of perceptions
	lc_data = list()
	lc_perception = list()

	for s_file_name in ils_file_name:
		#load game state
		c_game_state = load_game_state( s_file_name )
		#boilerplate game was a different API
		c_game_state.opponent_id = 1-c_game_state.id
		if (c_game_state is None):
			logging.critical(f"Failed to load game state >{s_file_name}<")
			return True

		#try to generate a Perception class
		c_perception = Perception( c_game_state )
		#c_data = c_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value[0] ]
		#lc_data.append( c_data )
		lc_perception.append( c_perception )
		#plt.show()
	
	#from a list of perceptions, generate heatmaps of the input matricies and save them as animated gifs
	gify_list_perception( lc_perception, "perception.gif", 2 )

	return False

#--------------------------------------------------------------------------------------------------------------------------------
#   MAIN
#--------------------------------------------------------------------------------------------------------------------------------

#   if interpreter has the intent of executing this file
if __name__ == "__main__":
	#setup logging
	logging.basicConfig(
		#level of debug to show
		level=logging.DEBUG,
		#header of the debug message
		format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s',
	)

	if TEST_BIGNOBRAINER_PERCEPTION==True:
		#test_big_no_brainer_perception( "pickle_dump_game_state.bin" )
		test_big_no_brainer_perception( "saved_game_states\\backup_100.bin" )

	if TEST_BIGNOBRAINER_PERCEPTION_ANIMATED==True:
		#animate_heatmap("test.gif")
		test_big_no_brainer_perception_animation( [f"saved_game_states\\backup_{50*index}.bin" for index in range(8) ]  )

	if TEST_TF_MODEL == True:
		#construct zero input
		c_perception = Perception()
		c_action = Action( 32 )

		logging.debug(f"input state: {c_perception.status.shape}")
		logging.debug(f"input mats: {c_perception.mats.shape}")
		logging.debug(f"output mats: {c_action.mats.shape}")

		bnb_model_tf( c_perception, c_action )

		pass	