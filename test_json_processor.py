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

import logging
#Replay class takes care of loading and conversions from a replay.json created by lux-ai to Perception and Action classes
from big_no_brainer.perception import Perception
from big_no_brainer.replay import Replay

#--------------------------------------------------------------------------------------------------------------------------------
#   CONFIGURATION
#--------------------------------------------------------------------------------------------------------------------------------

REPLAY_FOLDER = "replays"
REPLAY_FILE = "27879876.json"

GIF_FRAMERATE = 10
GIF_TURN_LIMIT = -1
#GIF_TURN_LIMIT = 15

TEST_JSON_TO_PERCEPTION_GIF = False
TEST_JSON_ACTION = False
TEST_JSON_TO_PERCEPTION_ACTION_TO_GIF = False
TEST_JSON_ACTION_TRANSLATION = False

TEST_MOCKUP_TRAINING = False

#--------------------------------------------------------------------------------------------------------------------------------
#   
#--------------------------------------------------------------------------------------------------------------------------------

def mockup_train_net( lc_features : list, lc_labels : list ):

    return

#--------------------------------------------------------------------------------------------------------------------------------
#   MAIN
#--------------------------------------------------------------------------------------------------------------------------------

#   if interpreter has the intent of executing this file
if __name__ == "__main__":

    logging.basicConfig( level=logging.DEBUG, format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s' )
    
    logging.debug(f"{[e_enum.name for e_enum in Perception.E_INPUT_SPACIAL_MATRICIES]}")

    if TEST_JSON_TO_PERCEPTION_GIF == True:

        #Construct Replay
        c_json_replay = Replay()
        #load the json file containing the replay
        c_json_replay.json_load( REPLAY_FOLDER, REPLAY_FILE )
        #from a json extract a list of perceptions, one per turn
        lc_perceptions, ld_units = c_json_replay.json_to_perceptions()
        #from a list of Perception generates a .gif()
        c_json_replay.perceptions_to_gif( "replay.gif", GIF_FRAMERATE, in_max_frames=GIF_TURN_LIMIT )
    
    if TEST_JSON_ACTION == True:
        #Construct Replay
        c_json_replay = Replay()
        #load the json file containing the replay
        c_json_replay.json_load( REPLAY_FOLDER, REPLAY_FILE )
        #From a replay.json extract a list of Perception and one list of Action per player. lists have one entry per step (turn) in the game
        lc_perceptions, lc_action_p0, lc_action_p1 =  c_json_replay.json_to_perception_action()

    if TEST_JSON_TO_PERCEPTION_ACTION_TO_GIF == True:
        #Construct Replay
        c_json_replay = Replay()
        #load the json file containing the replay
        c_json_replay.json_load( REPLAY_FOLDER, REPLAY_FILE )
        #From a replay.json extract a list of Perception and one list of Action per player. lists have one entry per step (turn) in the game
        lc_perceptions, lc_action_p0, lc_action_p1 =  c_json_replay.json_to_perception_action()        
        #from a list of Perception and actions for both players generates a .gif()
        c_json_replay.perceptions_actions_to_gif( "replay_actions.gif", GIF_FRAMERATE, in_max_frames=GIF_TURN_LIMIT )

    if TEST_JSON_ACTION_TRANSLATION == True:
        #Construct Replay
        c_json_replay = Replay()
        #load the json file containing the replay
        c_json_replay.json_load( REPLAY_FOLDER, REPLAY_FILE )
        #From a replay.json extract a list of Perception and one list of Action per player. lists have one entry per step (turn) in the game
        lc_perceptions, lc_action_p0, lc_action_p1 =  c_json_replay.json_to_perception_action()        
        #for each step (turn) translate Action into a list of action strings that can be sent to the game engine
        for c_perception, c_action in zip( lc_perceptions, lc_action_p0 ):
            ls_actions = c_action.translate()
            logging.debug(f"Step {c_perception.status[ Perception.E_INPUT_STATUS_VECTOR.MAP_TURN.value ]} | List of action strings: {ls_actions}")


    if TEST_MOCKUP_TRAINING == True:
        #Construct Replay
        c_json_replay = Replay()
        #load the json file containing the replay
        c_json_replay.json_load( REPLAY_FOLDER, REPLAY_FILE )
        #From a replay.json extract a list of Perception and one list of Action per player. lists have one entry per step (turn) in the game
        lc_perceptions, lc_action_p0, lc_action_p1 =  c_json_replay.json_to_perception_action()        

        mockup_train_net( lc_perceptions, lc_action_p0 )
        
    pass
