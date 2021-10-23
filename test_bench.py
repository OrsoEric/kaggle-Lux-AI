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
TEST_TF_MODEL = False

TEST_TF_LOAD_MODEL = True

#--------------------------------------------------------------------------------------------------------------------------------
#   TEST BENCHES
#--------------------------------------------------------------------------------------------------------------------------------

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

    if TEST_TF_MODEL == True:
        #construct zero input
        c_perception = Perception()
        c_action = Action( 32 )

        logging.debug(f"input state: {c_perception.status.shape}")
        logging.debug(f"input mats: {c_perception.mats.shape}")
        logging.debug(f"output mats: {c_action.mats.shape}")

        bnb_model_tf( c_perception, c_action )



        pass	

    if TEST_TF_LOAD_MODEL == True:
        #construct zero input
        c_perception = Perception()
        c_action = Action( 32 )

        logging.debug(f"input state: {c_perception.status.shape}")
        logging.debug(f"input mats: {c_perception.mats.shape}")
        logging.debug(f"output mats: {c_action.mats.shape}")

        c_model = bnb_model_tf( c_perception, c_action )
        logging.debug(f"Restoring weights...")
        c_model.load_weights("shaka")
        c_model.summary()

        c_model.predict()


        pass