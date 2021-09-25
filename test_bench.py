##	@package test_bench
#	test bench is meant to be executed to probe and stimulate agent components
#	a game state is loaded using pickle, bypassing the need to use the NODE.JS game engine

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

import logging
#pickle game state loader
from agent import load_game_state

#from agent import agent

from rule import Rule

#--------------------------------------------------------------------------------------------------------------------------------
#   TEST BENCHES
#--------------------------------------------------------------------------------------------------------------------------------

##	test the test bench
#	1) load a game state
#	2) execute agent rule
#	3) shows actions taken
def test_test_bench() -> bool:

    game_state = load_game_state( "pickle_dump_game_state.bin" )
    if (game_state == None):
        return True
    #initialize rule processor with the game state
    agent_rule_processor = Rule( game_state.map, game_state.players[game_state.id], game_state.players[game_state.opponent_id] )
    #ask the rule processor to come up with a list of actions
    agent_actions = agent_rule_processor.compute_actions()
    logging.debug(f"Actions: {agent_actions}")

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

    test_test_bench()
