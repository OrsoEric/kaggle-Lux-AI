#lux-ai-2021 main.py main.py --out=replay.json

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

    logging.basicConfig(
        #level of debug to show
        level=logging.INFO,
        #header of the debug message
        format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s',
    )

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
            #compute the ID of the player this agent is controlling
            player_id = int( observation[INPUT_CONSTANTS.UPDATES][0] )
            observation.player_id = player_id

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

"""
File \"/opt/conda/lib/python3.7/site-packages/kaggle_environments/agent.py\", line 50, in get_last_callable\n    
exec(code_object, env)\n  File \"/kaggle_simulations/agent/main.py\", line 15, in <module>\n    from agent import agent\n  
File \"/kaggle_simulations/agent/agent.py\", line 36, in <module>\n    
from rule import Rule\n  File \"/kaggle_simulations/agent/rule.py\", line 26, in <module>\n    
class Rule:\n  File \"/kaggle_simulations/agent/rule.py\", line 154, in Rule\n    
def __compute_worker_actions(self, ic_player : Player, ic_worker : Unit ) -> list[str]:\n
TypeError: 'type' object is not subscriptable\n
\n
During handling of the above exception, another exception occurred:\n
\n
Traceback (most recent call last):\n  
File \"/opt/conda/lib/python3.7/site-packages/kaggle_environments/agent.py\", line 157, in act\n
	action = self.agent(*args)\n  
File \"/opt/conda/lib/python3.7/site-packages/kaggle_environments/agent.py\", line 123, in callable_agent\n
agent = get_last_callable(raw_agent, path=raw) "
"""