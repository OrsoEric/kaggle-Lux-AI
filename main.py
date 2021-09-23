#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

from typing import Dict
#import sys
import logging

#import the stdin constants and make them available 
from lux.constants import Constants
INPUT_CONSTANTS = Constants.INPUT_CONSTANTS
#AI agent
from agent import agent

#--------------------------------------------------------------------------------------------------------------------------------
#   MAIN
#--------------------------------------------------------------------------------------------------------------------------------

#   if interpreter has the intent of executing this file
if __name__ == "__main__":

    def read_input():
        """fetch inputs from stdin
        Raises:
            SystemExit: [description]
        Returns:
            [type]: [description]
        """
        try:
            return input()
        except EOFError as eof:
            raise SystemExit(eof)

    class Observation( Dict[str, any] ):
        """
        Args:
            Dict ([type]): [description]
        """
        def __init__(self, player=0) -> None:
            """
            Args:
                player (int, optional): [description]. Defaults to 0.
            """
            self.player = player
            # self.updates = []
            # self.step = 0

    #Observations about the map
    observation = Observation()
    observation[INPUT_CONSTANTS.UPDATES] = []
    observation[INPUT_CONSTANTS.STEP] = 0
    #while init
    step = 0
    player_id = 0
    #forever
    while True:
        #the game will send environment data via stdin
        inputs = read_input()
        #add game engine input observation to the observations
        observation[INPUT_CONSTANTS.UPDATES].append(inputs)
        #Observations are being collected
        if step == 0:
            player_id = int( observation[INPUT_CONSTANTS.UPDATES][0] )
            observation.player = player_id

        #When observations have been fully collected
        if inputs == INPUT_CONSTANTS.DONE:
            #ask the agent for a list of actions based on observations
            actions = agent(observation, None)
            observation[INPUT_CONSTANTS.UPDATES] = []
            step += 1
            observation[INPUT_CONSTANTS.STEP] = step
            #??? Probably a final action to close the list of actions of this agent
            print(",".join(actions))
            print("D_FINISH")