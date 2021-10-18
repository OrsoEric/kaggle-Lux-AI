##  test_json_processor
#       2021-10-09
#   Perception scrubbing and gif Operational 
#
#       2021-10-10
#   Defining action class. Dig deep on how the json is structured
#       2021-10-11
#   Refactor perception class to work from both a Game class or a list of updates directly
#       2021-10-13
#   Import all json from folder

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

import logging
import os

#Replay class takes care of loading and conversions from a replay.json created by lux-ai to Perception and Action classes
from big_no_brainer.perception import Perception
from big_no_brainer.action import Action
from big_no_brainer.replay import Replay

#--------------------------------------------------------------------------------------------------------------------------------
#   CONFIGURATION
#--------------------------------------------------------------------------------------------------------------------------------

REPLAY_FOLDER = "replays"
REPLAY_FILE = "27879876.json"

#--------------------------------------------------------------------------------------------------------------------------------
#   Helper functions
#--------------------------------------------------------------------------------------------------------------------------------

def get_replays( is_folder : str ) -> list:
    """ Search in a folder for replays and return a list of all replay files with .json extension
    Args:
        is_folder (str): folder with replays
    Returns:
        list: list of replay.json files
    """
    #folder with replays
    s_filepath = os.path.join( os.getcwd(), REPLAY_FOLDER )
    ls_files = os.listdir( s_filepath )
    #search for all filenames in the list for files with a .json extension
    ls_replays = [ s_file for s_file in ls_files if s_file.find(".json") > -1 ]
    logging.debug(f"Replays found: {len(ls_replays)} | {ls_replays}")

    return ls_replays

#--------------------------------------------------------------------------------------------------------------------------------
#   BNB Big No Brainer imitation net
#--------------------------------------------------------------------------------------------------------------------------------
#   Replay.json are concatenated and fed to the training of the BNB net

def mockup_train_net( lc_step_in : list, lc_step_out : list ) -> bool:
    """???
    Args:
        lc_features (list): list of Perception, one for each step (turn). Perception.mats shape: feature*size*size
        lc_labels (list): list of Action, one for each step (turn). Action.mats shape: actions*size*size
    Returns:
            bool: False=OK | True=FAIL
    """
    logging.debug(f"Features: {len(lc_step_in)} | Shape: {lc_step_in[0].status.shape} | Feature Name: {[e_enum.name for e_enum in Perception.E_INPUT_STATUS_VECTOR]}")
    logging.debug(f"Features: {len(lc_step_in)} | Shape: {lc_step_in[0].mats.shape} | Feature Name: {[e_enum.name for e_enum in Perception.E_INPUT_SPACIAL_MATRICIES]}")
    logging.debug(f"Labels: {len(lc_step_out)} | Shape: {lc_step_out[0].mats.shape} | Label Name: {[e_enum.name for e_enum in Action.E_OUTPUT_SPACIAL_MATRICIES]}")

    logging.debug(f"IN :{lc_step_in[0].mats[0]}")
    logging.debug(f"OUT :{lc_step_out[0].mats[0]}")

    return False

#--------------------------------------------------------------------------------------------------------------------------------
#   MAIN
#--------------------------------------------------------------------------------------------------------------------------------

#   if interpreter has the intent of executing this file
if __name__ == "__main__":
    logging.basicConfig( level=logging.DEBUG, format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s' )
    #get a list of replay.json in the folder
    ls_replays_filename = get_replays( REPLAY_FOLDER )
    #allocate training set
    lc_train_perception = list()
    lc_train_action = list()
    #scan all replays
    for s_replay_filename in ls_replays_filename:
        #Construct Replay
        c_json_replay = Replay()
        #load the json file containing the replay
        c_json_replay.json_load( REPLAY_FOLDER, REPLAY_FILE )
        #From a replay.json extract a list of Perception and one list of Action per player. lists have one entry per step (turn) in the game
        lc_perceptions, lc_action_p0, lc_action_p1 =  c_json_replay.json_to_perception_action()        
        #DUMB!!! COncantenate all Perception/Action from P0
        lc_train_perception += lc_perceptions
        lc_train_action += lc_action_p0

    mockup_train_net( lc_train_perception, lc_train_action )

    