#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

import os
import logging

import json

import numpy as np

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
            #logging.debug(f"Observations: {c_observation}")

            #actions = ic_json['steps'][n_step+1][index]['action']

            #append this step observations in the list of observations
            lc_observations.append( c_observation )

    #return a list of oservations, one per turn
    return lc_observations

#--------------------------------------------------------------------------------------------------------------------------------
#   MAIN
#--------------------------------------------------------------------------------------------------------------------------------

#   if interpreter has the intent of executing this file
if __name__ == "__main__":

    logging.basicConfig( level=logging.DEBUG, format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s' )

    c_json_replay = json_load( REPLAY_FOLDER, REPLAY_FILE )

    lc_observations = json_observation( c_json_replay )
    logging.debug(f"Observations : {len(lc_observations)}")

