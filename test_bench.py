##	@package test_bench
#	test bench is meant to be executed to probe and stimulate agent components
#	a game state is loaded using pickle, bypassing the need to use the NODE.JS game engine

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

import logging
from lux.game_map import Position

#pickle game state loader
from agent import load_game_state

#from agent import agent

from rule import Rule

#--------------------------------------------------------------------------------------------------------------------------------
#   CONSTANTS(fake)
#--------------------------------------------------------------------------------------------------------------------------------

#executes the pickle load and Rule class vanilla
TEST_TEST_BENCH = True
TEST_RULE_SEARCH_NEAREST = False

#--------------------------------------------------------------------------------------------------------------------------------
#   TEST BENCHES
#--------------------------------------------------------------------------------------------------------------------------------

##	test the test bench
#	1) load a game state
#	2) execute agent rule
#	3) shows actions taken
def test_test_bench( is_file_name ) -> bool:
	#load game state
	game_state = load_game_state( is_file_name )
	if (game_state == None):
		logging.critical(f"Failed to load")
		return True
	#initialize rule processor with the game state
	agent_rule_processor = Rule( game_state.map, game_state.players[game_state.id], game_state.players[game_state.opponent_id] )
	#ask the rule processor to come up with a list of actions
	agent_actions = agent_rule_processor.compute_actions()
	logging.debug(f"Actions: {agent_actions}")

	return False

def test_rule_search_nearest( is_file_name ) -> bool:
	#load game state
	game_state = load_game_state( is_file_name )
	if (game_state == None):
		logging.critical(f"Failed to load")
		return True

	#initialize rule processor with the game state
	agent_rule_processor = Rule( game_state.map, game_state.players[game_state.id], game_state.players[game_state.opponent_id] )

	print("Test search cell type method")
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.ANY, Position(0,0) ))
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.ANY, Position(6,8) ))
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.CITYTILE, Position(6,8) ))
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.CITYTILE_PLAYER, Position(6,8) ))
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.CITYTILE_OPPONENT, Position(6,8) ))
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.RESOURCE, Position(6,8) ))
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.COAL, Position(3,2) ))
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.URANIUM, Position(3,2) ))
	print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.WOOD, Position(3,2) ))
	#print(agent_rule_processor.search_nearest( game_state.map, Rule.E_CELL_TARGET.EMPTY, Position(3,2) ))
	

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

	if TEST_TEST_BENCH==True:
		test_test_bench( "pickle_dump_game_state.bin" )

	if TEST_RULE_SEARCH_NEAREST == True:
		test_rule_search_nearest( "pickle_dump_game_state.bin" )
