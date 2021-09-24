
""" agent.py
Releases:
2021-09-22a BOT0 - IDLE BOT     : Default RULE based agent that uses the starting worker to collect resources
2021-09-23a BOT2 - RESEARCH BOT : Agent now launches research action when city can use an action. Code cleanup
"""

import math
import logging
#used to estimate resource use of the agent
from time import perf_counter

#efficient nested loops
from itertools import product

#import game constant and make them available to the program
from lux.constants import Constants
DIRECTIONS = Constants.DIRECTIONS
INPUT_CONSTANTS = Constants.INPUT_CONSTANTS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from lux.game_map import Cell

from lux.game import Game

from lux import annotate
#???
game_state = None

def agent(observation, configuration):
    global game_state

    ### Do not edit ###
    if observation[INPUT_CONSTANTS.STEP] == 0:
        game_state = Game()
        game_state._initialize(observation[INPUT_CONSTANTS.UPDATES])
        game_state._update(observation[INPUT_CONSTANTS.UPDATES][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation[INPUT_CONSTANTS.UPDATES])

    #--------------------------------------------------------------------------------------------------------------------------------
    #   Game wide parameters
    #--------------------------------------------------------------------------------------------------------------------------------

    #compute the size of the map.
    width, height = game_state.map.width, game_state.map.height
    #compute which player is assigned to this agent, and which player is assigned to the opponent's agent
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]

    #list of actions the agent is going to send to the game engine. initialize to NOP
    actions = list()

    #--------------------------------------------------------------------------------------------------------------------------------
    #   Find all squares with resouces
    #--------------------------------------------------------------------------------------------------------------------------------

    #initialize a list of squares with resources to empty
    l_squares_with_resources: list[Cell] = list()
    #scan every 2D coordinate on the map
    for x, y in product( range(width), range(height) ):
        #compute the content of the square at the given coordinate
        my_cell = game_state.map.get_cell( x, y )
        #if the square has resources on it
        if my_cell.has_resource():
            #add the square to the list of squares with resouces
            l_squares_with_resources.append( my_cell )

    #--------------------------------------------------------------------------------------------------------------------------------
    #   WORKER RULES
    #--------------------------------------------------------------------------------------------------------------------------------

    #iterate over all units
    for my_unit in player.units:
        #WORKER RULES
        if my_unit.is_worker():
            #Worker is out of cooldown
            if my_unit.can_act():
                if my_unit.get_cargo_space_left() > 0:
                    closest_dist = math.inf
                    closest_resource_tile = None
                    # if the unit is a worker and we have space in cargo, lets find the nearest resource tile and try to mine it
                    for resource_tile in l_squares_with_resources:
                        if resource_tile.resource.type == Constants.RESOURCE_TYPES.WOOD:
                            if not player.researched(resource_tile.resource.type):
                                continue
                            else:
                                dist = resource_tile.pos.distance_to(my_unit.pos)
                                if dist < closest_dist:
                                    closest_dist = dist
                                    closest_resource_tile = resource_tile
                        elif resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL:
                            if not player.researched_coal():
                                continue
                            else:
                                continue
                        elif resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM:
                            if not player.researched_uranium():
                                continue
                            else:
                                continue
                        #resource type is invalid. algorithmic error!
                        else:
                            logging.critical(f"Unknown resource {resource_tile}")
                        
                    if closest_resource_tile is not None:
                        logging.debug(f"Resource {closest_resource_tile} found by worker {my_unit}")
                        actions.append( my_unit.move( my_unit.pos.direction_to( closest_resource_tile.pos ) ) )
                else:
                    # if unit is a worker and there is no cargo space left, and we have cities, lets return to them
                    if len(player.cities) > 0:
                        closest_dist = math.inf
                        closest_city_tile = None
                        for k, city in player.cities.items():
                            for city_tile in city.citytiles:
                                dist = city_tile.pos.distance_to(my_unit.pos)
                                if dist < closest_dist:
                                    closest_dist = dist
                                    closest_city_tile = city_tile
                        if closest_city_tile is not None:
                            logging.debug(f"Worker {my_unit} returning to city {closest_city_tile}")
                            move_dir = my_unit.pos.direction_to(closest_city_tile.pos)
                            actions.append(my_unit.move(move_dir))
            #WORKER can't act
            else:
                pass

        #Handle carts
        elif my_unit.is_cart():
            pass

        #Default Case:
        else:
            #ERROR!!! Unknown unit
            logging.critical(f"Unit type is unknown: {my_unit}")

    #--------------------------------------------------------------------------------------------------------------------------------
    #   CITY RULES
    #--------------------------------------------------------------------------------------------------------------------------------

    #iterate over all cities.
    for index, my_city in player.cities.items():
        #iterate over all city tiles that make up an individual city
        for my_city_tile in my_city.citytiles:
            #if the city can act
            if my_city_tile.can_act() == True:
                #have the city tile research
                logging.debug(f"City {my_city_tile} does research")
                actions.append( my_city_tile.research() )

    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions
