##	@package test_bench
#	test bench is meant to be executed to probe and stimulate agent components
#	a game state is loaded using pickle, bypassing the need to use the NODE.JS game engine

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

import logging

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