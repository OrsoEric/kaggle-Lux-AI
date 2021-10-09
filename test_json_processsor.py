#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

import os
import logging

import json

import numpy as np

#import game constant and make them available to the program
from lux.constants import Constants
DIRECTIONS = Constants.DIRECTIONS
INPUT_CONSTANTS = Constants.INPUT_CONSTANTS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from lux.game import Game

from big_no_brainer.perception import Perception
from big_no_brainer.perception import gify_list_perception

#--------------------------------------------------------------------------------------------------------------------------------
#   CONFIGURATION
#--------------------------------------------------------------------------------------------------------------------------------

REPLAY_FOLDER = "replays"
REPLAY_FILE = "27883823.json"

#--------------------------------------------------------------------------------------------------------------------------------
#   FILE
#--------------------------------------------------------------------------------------------------------------------------------

def json_load( is_folder : str, is_filename : str ):

    s_filepath = os.path.join( os.getcwd(), is_folder, is_filename )
    try:
        with open(s_filepath) as c_file:
            c_opened_json = json.load( c_file )
    except:
        logging.critical(f"Could not open JSON: {s_filepath}")
        return None
    #logging.debug(f"JSON: {c_opened_json}")
    return c_opened_json

#--------------------------------------------------------------------------------------------------------------------------------
#   JSON->OBSERVATION
#--------------------------------------------------------------------------------------------------------------------------------

def json_observation( ic_json ):
    """From an opened replay.json extract a list of observations
    observation is a dictionary with the following fields e.g.
    'globalCityIDCount': 103, 'globalUnitIDCount': 145, 'height': 24, 'player': 0, 'remainingOverageTime': 60, 'reward': 40004, 'step': 275, 'updates':[''],  'width': 24
    Args:
        ic_json (json): replay json loaded from file and processed by json module
    Returns:
        list(str): list of observation strings. one for each step (turn in the game)
    """
    #Fetch the ID of the episode
    n_episode_id = ic_json["info"]["EpisodeId"]
    #???
    index = np.argmax([r or 0 for r in ic_json["rewards"]])
    logging.debug(f"ID: {n_episode_id} | Index: {index} | Teams: {ic_json['info']['TeamNames']}")

    #initialize list of observations
    lc_observations = list()

    #Scan every Step of the match (Turn)
    for n_step in range(len(ic_json["steps"])-1):
        #logging.debug(f"Step: {n_step} of {len(ic_json['steps'])-1}")
        #???
        if ic_json["steps"][n_step][index]["status"] == 'ACTIVE':
            #Fetch the observations of this turn
            c_observation = ic_json['steps'][n_step][0]['observation']
            #logging.debug(f"Step: {n_step} | Observations: {c_observation}")

            #append this step observations in the list of observations
            lc_observations.append( c_observation )

    logging.debug(f"Observations : {len(lc_observations)}")
    #return a list of oservations, one per Step (turn)
    return lc_observations

def observations_to_gamestates( ilc_observations : list ):
    """
    Args:
        ilc_observations (list(observations)): [description]
    Returns:
        list(Game): List of gamestates. One per turn
    """
    lc_gamestates = list()
    #from a list of observations generates a list of Game()
    for c_observation in lc_observations:

        if c_observation[INPUT_CONSTANTS.STEP] == 0:
            c_game_state = Game()
            c_game_state._initialize(c_observation[INPUT_CONSTANTS.UPDATES])
            c_game_state._update(c_observation[INPUT_CONSTANTS.UPDATES][2:])
            c_game_state._set_player_id( c_observation["player"] )

        else:
            c_game_state._update(c_observation[INPUT_CONSTANTS.UPDATES])

        #logging.debug(f"Step: {c_observation[INPUT_CONSTANTS.STEP]} | Gamestate: {c_game_state}")
        lc_gamestates.append( c_game_state )

    logging.debug(f"Gamestates : {len(lc_gamestates)}")
    return lc_gamestates

#--------------------------------------------------------------------------------------------------------------------------------
#   MAIN
#--------------------------------------------------------------------------------------------------------------------------------

#   if interpreter has the intent of executing this file
if __name__ == "__main__":

    logging.basicConfig( level=logging.DEBUG, format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s' )

    #load the json file containing the replay
    c_json_replay = json_load( REPLAY_FOLDER, REPLAY_FILE )

    #from json loads a list of observations
    lc_observations = json_observation( c_json_replay )

    #from list of observations generate list of Game()
    lc_gamestates = observations_to_gamestates( lc_observations )
    
    lc_perceptions = list()
    #from a list of Game() generates a list of Perception()
    for c_gamestate in lc_gamestates:
        c_perception = Perception( c_gamestate )
        lc_perceptions.append( c_perception )
    
    logging.debug(f"Perceptions : {len(lc_perceptions)}")

    #from a list of Perception generates a .gif()
    gify_list_perception( lc_perceptions, "replay.gif", 1,in_max_frames=10 )
