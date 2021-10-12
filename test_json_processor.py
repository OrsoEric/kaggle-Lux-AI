##  test_json_processor
#       2021-10-09
#   Perception scrubbing and gif Operational 
#
#       2021-10-10
#   Defining action class. Dig deep on how the json is structured
#       2021-10-11
#   Refactor perception class to work from both a Game class or a list of updates directly
#

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

import os
import logging

import json
import copy
import numpy as np
from big_no_brainer.action import Action

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
REPLAY_FILE = "27879876.json"

GIF_FRAMERATE = 10
#GIF_TURN_LIMIT = -1
GIF_TURN_LIMIT = 5

TEST_JSON_TO_PERCEPTION_GIF = False
TEST_JSON_ACTION = True

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

def json_to_action( ic_json, id_units : dict ):
    """From a replay.json extract all actions of the player with a given index
    output is a list of list of strings in the form. One list of string per step.
    each list of string list all actions the player gave to it's citytile units
    [["r 14 8", "m u_1 w"]
    ["", ""]
    ["m u_1 w"]]

    Args:
        ic_json (json): json file opened by json module
        id_units (dict): dictionary of units e.g. {u_55 : (0, 13, 12) }
        in_player (int): index of the player wor whom action matrix is generated
    """

    #allocate player actions
    lls_player_action = list()
    logging.debug(f"JSON Steps: {len(ic_json['steps'])}")
    #Scan every Step of the match (Turn)
    n_last_step = len(ic_json["steps"])
    #for n_step in range(1, n_last_step):
    #scan each step (turn)
    for c_step in ic_json['steps']:
        #logging.debug(f"Step: {n_step} of {len(ic_json['steps'])}")
        #logging.debug(f"Step: {c_step}")
        #fetch step (turn) only present in player 0 observations
        n_step = c_step[0]["observation"]["step"]
        #for all players
        for c_player in c_step:
            #logging.debug(f"Player: {c_player}")
            #fetch index of player
            n_id = c_player["observation"]["player"]
            #if player is active or the game is about to be done
            if c_player["status"] == "ACTIVE" or c_player["status"] == "DONE":
                #fetch the list of actions the player took in the previous turn
                #From JSON, From Steps (list of turns), from a given step (turn index), from player 0, is player is active (not dead)
                ls_actions = c_player['action']
                #logging.debug(f"Step: {n_step} | Action: {ls_actions}")
                #scan all actions
                for s_action in ls_actions:
                    #decompose the action into tokens
                    ls_action_token = s_action.split(' ')
                    logging.debug(f"Step: {n_step} | Player {n_id} | Action Tokens: {ls_action_token}")

            #append this step observations in the list of observations
            #lls_player_action.append( c_observation )



    return

def observations_to_gamestates( ilc_observations : list ):
    """
    Args:
        ilc_observations (list(observations)): [description]
    Returns:
        list(Game): List of gamestates. One per turn
    """
    global c_game_state
    lc_gamestates = list()
    #from a list of observations generates a list of Game()
    for c_observation in ilc_observations:

        if c_observation[INPUT_CONSTANTS.STEP] == 0:
            c_game_state = Game()
            c_game_state._initialize(c_observation[INPUT_CONSTANTS.UPDATES])
            c_game_state._update(c_observation[INPUT_CONSTANTS.UPDATES][2:])
            c_game_state._set_player_id( c_observation["player"] )

        else:
            c_game_state._update(c_observation[INPUT_CONSTANTS.UPDATES])

        #logging.debug(f"Step: {c_observation[INPUT_CONSTANTS.STEP]} | Gamestate: {c_game_state} ")
        lc_gamestates.append( copy.deepcopy( c_game_state ) )

    logging.debug(f"Gamestates : {len(lc_gamestates)}")
    return lc_gamestates

def json_to_perceptions( ic_json ):
    """From a loaded replay.json extract a list of observations
    Args:
        ic_json ([type]): [description]
    Returns:
        [type]: [description]
    """
    #from json loads a list of observations
    lc_observations = json_observation( c_json_replay )
    #from list of observations generate list of Game()
    lc_gamestates = observations_to_gamestates( lc_observations )
    #Allocate
    lc_perceptions = list()
    ld_units = list()
    #from a list of Game() generates a list of Perception()
    for c_gamestate in lc_gamestates:
        c_perception = Perception()
        c_perception.from_game( c_gamestate )
        logging.debug(f"Game: {c_gamestate}")
        logging.debug(f"Step: {c_perception.status[Perception.E_INPUT_STATUS_VECTOR.MAP_TURN.value]}  | Perceptions : {c_perception}")
        #add the percepton to the list of perceptions
        lc_perceptions.append( c_perception )
        #add the dictionary of units to a list of dictionaries. (redundant)
        ld_units.append( c_perception.d_unit )

    logging.debug(f"Perceptions : {len(lc_perceptions)}")
    logging.debug(f"Dictionary of units : {len(ld_units)}")
    
    return lc_perceptions, ld_units

def json_to_perception_action( ic_json ):
    """ Parse a replay.json into a list of observations and two list of actions
    The lists contain one row per step (turn) of the game

    """

    #allocate player actions
    lls_player_action = list()
    logging.debug(f"JSON Steps: {len(ic_json['steps'])}")
    #Scan every Step of the match (Turn)
    n_last_step = len(ic_json["steps"])
    #for n_step in range(1, n_last_step):
    ls_old_observation = None
    ls_observations = None
    #scan each step (turn)
    for c_step in ic_json['steps']:
        #logging.debug(f"Step: {n_step} of {len(ic_json['steps'])}")
        #logging.debug(f"Step: {c_step}")
        #fetch step (turn) only present in player 0 observations
        n_step = c_step[0]["observation"]["step"]

        if (n_step != 50):
            continue

        #remember the previous observation
        ls_old_observation = ls_observations
        #allocate observations and actions for this turn
        ls_observations = list()
        ls_actions_p0 = list()
        ls_actions_p1 = list()

        #for all players
        for c_player in c_step:
            #logging.debug(f"Player: {c_player}")
            #fetch index of player
            n_id = c_player["observation"]["player"]
            #if player is active or the game is about to be done
            if c_player["status"] == "ACTIVE" or c_player["status"] == "DONE":
                #from player 0
                if (n_id == 0):
                    #fetch observations
                    ls_observations.append( c_player["observation"]["updates"])
                    #fetch actions
                    ls_actions_p0.append( c_player['action'] )
                elif (n_id == 1):
                    #fetch actions
                    ls_actions_p1.append( c_player['action'] )
                else:
                    logging.critical(f"unknown player: {n_id} at step: {n_step}")

                ls_actions = c_player['action']
                #logging.debug(f"Step: {n_step} | Action: {ls_actions}")
                

        #use the previous observation and the current actions to generate Perception and Action matricies


    logging.debug(f"Step: {n_step}")
    logging.debug(f"Observation: {ls_old_observation}")
    logging.debug(f"Observation: {ls_observations}")
    logging.debug(f"Action P0: {ls_actions_p0}")
    logging.debug(f"Action P1: {ls_actions_p1}")
    
    return


#--------------------------------------------------------------------------------------------------------------------------------
#   MAIN
#--------------------------------------------------------------------------------------------------------------------------------

#   if interpreter has the intent of executing this file
if __name__ == "__main__":

    logging.basicConfig( level=logging.DEBUG, format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s' )

    #load the json file containing the replay
    c_json_replay = json_load( REPLAY_FOLDER, REPLAY_FILE )

    if TEST_JSON_TO_PERCEPTION_GIF == True:
        #from a json extract a list of perceptions, one per turn
        lc_perceptions, ld_units = json_to_perceptions( c_json_replay )
        #from a list of Perception generates a .gif()
        gify_list_perception( lc_perceptions, "replay.gif", GIF_FRAMERATE,in_max_frames=GIF_TURN_LIMIT )

    if TEST_JSON_ACTION == True:
        #from a json extract a list of perceptions, one per turn
        lc_perceptions, ld_units = json_to_perceptions( c_json_replay )
        #from a json extract a list of actions. needs a dictionary of units that can be foind in the perceptions 
        lc_actions_p0 = Action( c_json_replay, ld_units, 0 )
        lc_actions_p0 = Action( c_json_replay, ld_units, 1 )

        pass


    #json_to_action( c_json_replay )    

    #json_to_perception_action( c_json_replay )
    

    
