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


    #Construct Replay
    c_json_replay = Replay()
    #load the json file containing the replay
    c_json_replay.json_load( REPLAY_FOLDER, REPLAY_FILE )
    #From a replay.json extract a list of Perception and one list of Action per player. lists have one entry per step (turn) in the game
    lc_perceptions, lc_action_p0, lc_action_p1 =  c_json_replay.json_to_perception_action()        

    mockup_train_net( lc_perceptions, lc_action_p0 )