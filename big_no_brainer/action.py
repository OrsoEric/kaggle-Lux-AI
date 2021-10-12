##  @package action
#   ARCHITECTURE
#
#   INFERENCE
#   1) Game() -> Perception()
#   2) Perception() -> model? -> Orders()
#   3) Orders() -> list()
#
#   TRAINING
#
#   1) run inference this vs this at given random map size   
#   2) game result -> Reward() -> float
#   3) reinforcement learning
#
#   Action translates a 
#

##  History
#       2021-10-12
#   Action operational

##  TODO
#   add shift to output matrix

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

import itertools
import json
#from inspect import CO_VARARGS
import logging
#enumeration support
from enum import Enum, auto
import pickle

#efficient nested loops
from itertools import product

import numpy as np

#LUX-AI-2021
from lux.constants import GAME_CONSTANTS
from lux.constants import Constants
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from lux.game import Game
from lux.game_map import Position
from lux.game_objects import Unit

from big_no_brainer.perception import Perception

#plot
import matplotlib.pyplot as plt
import seaborn as sns
#convert input matricies into .gif
import matplotlib.animation as animation

#--------------------------------------------------------------------------------------------------------------------------------
#   Action
#--------------------------------------------------------------------------------------------------------------------------------
#   This class translates the 15*32*32 output of the BNB network into actions emitted to the Game
#   Only one player is controlled, only units/citytiles that can act are emitted for action
#   Action chooses the maximum Q above a threshold amongst the matricies it has access to
#   Action back propagate on the BNB output matrix a positive for action choosen, a 0 for action discarded, a -1 for action invalid
#   This feedback is used for reinforcement learning purposes in learning and is displayed during inference to evaluate misaction rate
#   emission on empty squares is considered an error
#   emission of an invalid action is considered an error
#   accumulate metrics on total actions emitted this turn and total actions emitted

class Action():

    #----------------    Configurations    ----------------

    #(3+7)*32*32 = 10*32*32
    #enumerate state vector that describe game wide information, will bypass the spatial processing stage. Total 15 actions
    class E_OUTPUT_SPACIAL_MATRICIES( Enum ):
        #Citytile Actions. 3*32*32
        CITYTILE_RESEARCH = 0
        CITYTILE_BUILD_WORKER = auto()
        CITYTILE_BUILD_CART = auto()
        #Unified unit actions. 7*32*32 e.g. cart can't comply with build city action.
        UNIT_MOVE_NORTH = auto()
        UNIT_MOVE_EAST = auto()
        UNIT_MOVE_SOUTH = auto()
        UNIT_MOVE_WEST = auto()
        UNIT_TRANSFER_RESOURCE = auto()
        UNIT_BUILD_CITY = auto()
        UNIT_PILLAGE_ROAD = auto()        

    #----------------    Constructor    ----------------

    def __init__( self, in_map_size : int ):
        """Constructor. Initialize mats and vars
        Args:
            ic_json (json): opened replay.json
            ild_units (list): list of dictionaries of units and their position. required to decode actions. one per turn, 360 turn per game.
                e.g. { u_1 : ( 11, 17 ), u_5 : ( 12, 17 ) }
            in_player (int): player for which Action is to be extracted. 2 player in a replay.json
        """

        #initialize class vars
        if self.__init_vars( in_map_size ):
            logging.critical( f"Failed to initialize class vars" )

        return

    #----------------    Overloads    ----------------

    def __str__(self) -> str:
        ln_sum = list()
        for e_header in Action.E_OUTPUT_SPACIAL_MATRICIES:
            ln_sum.append( self.mats[e_header.value].sum() ) 
        return f"Action | {ln_sum}"

    #----------------    Private Members    ----------------

    def __init_vars( self, in_map_size : int ) -> bool:
        """Initialize class vars
        Returns:
            bool: False=OK | True=FAIL
        """

        self.mats = np.zeros( (len(Action.E_OUTPUT_SPACIAL_MATRICIES), GAME_CONSTANTS['MAP']['WIDTH_MAX'], GAME_CONSTANTS['MAP']['HEIGHT_MAX']) )

        self._set_map_size( in_map_size )

        return False

    def __accumulate_mat( self, n_index : int, in_x : int, in_y : int ) -> bool:

        n_x = int(self._w_shift +in_x)
        n_y = int(self._h_shift +in_y)
        if n_x < 0 or n_x > GAME_CONSTANTS['MAP']['WIDTH_MAX']:
            logging.error(f"Bad X index: {n_x}")
            return True

        if n_y < 0 or n_y > GAME_CONSTANTS['MAP']['HEIGHT_MAX']:
            logging.error(f"Bad X index: {n_x}")
            return True
        #logging.debug(f"{n_index} {n_x} {n_y}")

        self.mats[n_index, n_x, n_y ] += 1

        return False

    #----------------    Protected Members    ----------------

    def _set_map_size( self, in_map_size : int ) -> bool:
        #size of the map in cells. THe map is square
        self.n_map_size = int(in_map_size)
        #set the offset. all map sizes uses max size and are shifted to be centered. Helps neural network convolution to generalize.
        self._w_shift = int( (GAME_CONSTANTS['MAP']['WIDTH_MAX'] -in_map_size) // 2 )
        self._h_shift = int( (GAME_CONSTANTS['MAP']['HEIGHT_MAX'] -in_map_size) // 2 )

        return False

    def _parse_agent_actions( self, id_units : dict, ils_actions : list ) -> bool:
        """Parse a string of actions into an initialized Action class by filling the mats
        An action is made by action tokens
        e.g. ['bw', '15', '1'] -> inn_mat[Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_BUILD_WORKER, 15, 1] = 1
        e.g. ['m', 'u_2', 's'] -> id_units { u_2 : (11,12) } -> inn_mat[Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_SOUTH, 11, 12] = 1}
        Args:
            ils_actions (list(str)): list of string with a list of actions.
                e.g. ["r 14 8", "m u_1 w"]
            id_units (dict): dictionary of units.
                "unit name" : (owner_id, unit_type, pos.x, pos.y)
                { u_1 : (0, 1, 11, 2) }
        Returns:
            bool: False=OK | True=FAIL
        """

        #scan all actions
        for s_action in ils_actions:
            #decompose the action into tokens
            ls_action_token = s_action.split(' ')
            #logging.debug(f"Step: {n_step} | Player {n_id} | Action Tokens: {ls_action_token}")
            #NOP
            s_header = ls_action_token[0]
            if s_header == "":
                logging.debug("NOP")
                pass
            
            #Citytile Research "r x y"
            elif s_header == GAME_CONSTANTS["ACTION"]["CITYTILE"]["RESEARCH"]:
                if (len(ls_action_token) != 3):
                    logging.error(f'Expected 3 tokens on action: { s_header } but got {len(ls_action_token)} instead.')
                    return True
                #Fetch action arguments
                n_x = int(ls_action_token[1])
                n_y = int(ls_action_token[2])
                #logging.debug(f"RESEARCH {n_x} {n_y}")
                self.__accumulate_mat( Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_RESEARCH.value, n_x, n_y ) 

            #Citytile Build Worker "bw x y"
            elif s_header == GAME_CONSTANTS["ACTION"]["CITYTILE"]["BUILD_WORKER"]:
                if (len(ls_action_token) != 3):
                    logging.error(f'Expected 3 tokens on action: { s_header } but got {len(ls_action_token)} instead.')
                    return True
                #Fetch action arguments
                n_x = int(ls_action_token[1])
                n_y = int(ls_action_token[2])
                #logging.debug(f"BUILD_WORKER {n_x} {n_y}")
                self.__accumulate_mat( Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_BUILD_WORKER.value, n_x, n_y ) 
            
            #Citytile Build Worker "bc x y"
            elif s_header == GAME_CONSTANTS["ACTION"]["CITYTILE"]["BUILD_CART"]:
                if (len(ls_action_token) != 3):
                    logging.error(f'Expected 3 tokens on action: { s_header } but got {len(ls_action_token)} instead.')
                    return True
                #Fetch action arguments
                n_x = int(ls_action_token[1])
                n_y = int(ls_action_token[2])
                #logging.debug(f"BUILD_CART {n_x} {n_y}")
                self.__accumulate_mat( Action.E_OUTPUT_SPACIAL_MATRICIES.BUILD_CART.value, n_x, n_y ) 
                
            #Unit Move
            elif s_header == GAME_CONSTANTS["ACTION"]["UNIT"]["MOVE"]:
                if (len(ls_action_token) != 3):
                    logging.error(f'Expected 3 tokens on action: { s_header } but got {len(ls_action_token)} instead.')
                    return True
                #Fetch action arguments
                s_unit_id = ls_action_token[1]
                s_move_direction = ls_action_token[2]
                #launch a search inside the dictionary of units
                if s_unit_id in id_units:
                    #get a tuple with the position of unit
                    t_pos = id_units[s_unit_id]
                else:
                    logging.error(f'Unit { s_unit_id } not found in unit dictionary: {id_units}')
                    return True
                #n_mat_index = -1
                #the direction encodes the destination matrix
                if s_move_direction == GAME_CONSTANTS["DIRECTIONS"]["NORTH"]:
                    n_mat_index = Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_NORTH.value
                elif s_move_direction == GAME_CONSTANTS["DIRECTIONS"]["EAST"]:
                    n_mat_index = Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_EAST.value
                elif s_move_direction == GAME_CONSTANTS["DIRECTIONS"]["SOUTH"]:
                    n_mat_index = Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_SOUTH.value
                elif s_move_direction == GAME_CONSTANTS["DIRECTIONS"]["WEST"]:
                    n_mat_index = Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_WEST.value
                elif s_move_direction == GAME_CONSTANTS["DIRECTIONS"]["CENTER"]:
                    #center move does not need to update a move matrix
                    continue
                else:
                    logging.error(f"Move Direction is unknown { s_move_direction }")
                    return True
                #logging.debug(f"Worker {s_unit_id} | Position {t_pos} | Move {s_move_direction}")
                #update the mat
                self.__accumulate_mat( n_mat_index, t_pos[0], t_pos[1] ) 

            #Unit Transfer Resource
            elif s_header == GAME_CONSTANTS["ACTION"]["UNIT"]["TRANSFER_RESOURCE"]:
                if (len(ls_action_token) != 4):
                    logging.error(f'Expected 4 tokens on action: { s_header } but got {len(ls_action_token)} instead.')
                    return True

                #Fetch action arguments
                s_source_unit_id = ls_action_token[1]
                s_dest_unit_id = ls_action_token[2]
                s_resource_type = ls_action_token[3]
                n_resource_amount = ls_action_token[4]

                logging.error(f"Transfer Action not implemented... {s_source_unit_id} {s_dest_unit_id} {s_resource_type} {n_resource_amount}")
                return True

            #Unit Build City
            elif s_header == GAME_CONSTANTS["ACTION"]["UNIT"]["BUILD_CITY"]:
                if (len(ls_action_token) != 2):
                    logging.error(f'Expected 2 tokens on action: { s_header } but got {len(ls_action_token)} instead.')
                    return True
                #Fetch action arguments
                s_unit_id = ls_action_token[1]
                #launch a search inside the dictionary of units
                if s_unit_id not in id_units:
                    logging.error(f'Unit { s_unit_id } not found in unit dictionary: {id_units}')
                    return True
                else:
                    #get a tuple with the position of unit
                    t_pos = id_units[s_unit_id]
                #logging.debug(f"Worker {s_unit_id} | Position {t_pos} | Build City")
                #update the mat
                self.__accumulate_mat( Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_BUILD_CITY.value, t_pos[0], t_pos[1] ) 

            #Unit Pillage
            elif s_header == GAME_CONSTANTS["ACTION"]["UNIT"]["PILLAGE_ROAD"]:
                if (len(ls_action_token) != 2):
                    logging.error(f'Expected 2 tokens on action: { s_header } but got {len(ls_action_token)} instead.')
                    return True
                #Fetch action arguments
                s_unit_id = ls_action_token[1]
                #launch a search inside the dictionary of units
                if s_unit_id not in id_units:
                    logging.error(f'Unit { s_unit_id } not found in unit dictionary: {id_units}')
                    return True
                else:
                    #get a tuple with the position of unit
                    t_pos = id_units[s_unit_id]
                #logging.debug(f"Worker {s_unit_id} | Position {t_pos} | Pillage Road")
                #update the mat
                self.__accumulate_mat( Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_PILLAGE_ROAD.value, t_pos[0], t_pos[1] ) 

            else:
                logging.debug(f"Unknown header: {s_header}")
                return True
                
        return False

    def _translate_citytile_actions( self ) -> list:
        """Translates citytile actions into a list of string actions to be fed to the game engine
        Requires output spacial matricies
        @TODO add a dictionary of citytiles to check if a city exist
        @TODO check action against cooldown perception matrix to see if an action is valid
            list: list of citytile string actions to be fed to the game engine
                e.g. ["r 14 8", "bw 11 0", "bc 1 1"]
        """
        #allocate list of stringactions for this step(turn) for citytiles
        ls_actions_citytile = list()
        #scan each cell of the map
        for n_x, n_y in product( range(self.n_map_size), range(self.n_map_size) ):
            #apply shift
            n_x_shift = n_x +self._w_shift
            n_y_shift = n_y +self._h_shift

            n_max_q_score = GAME_CONSTANTS["ACTION"]["TRANSLATE"]["MIN_SCORE"]
            n_max_q_index = -1
            #search the highest rated action in the three citytile output spacial matricies
            for n_index in [ Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_RESEARCH.value, Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_BUILD_WORKER.value, Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_BUILD_CART.value  ]:
                #detect the best score, if any
                n_score = self.mats[ n_index, n_x_shift, n_y_shift ]
                if n_score > n_max_q_score:
                    n_max_q_score = n_score
                    n_max_q_index = n_index
            #search failed
            if n_max_q_index < 0:
                #do nothing
                pass
            else:
                #emit CITYTILE_RESEARCH
                if n_max_q_index == Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_RESEARCH.value:
                    s_action = f'{GAME_CONSTANTS["ACTION"]["CITYTILE"]["RESEARCH"]} {n_x} {n_y}'
                elif n_max_q_index == Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_BUILD_WORKER.value:
                    s_action = f'{GAME_CONSTANTS["ACTION"]["CITYTILE"]["BUILD_WORKER"]} {n_x} {n_y}'
                elif n_max_q_index == Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_BUILD_CART.value:
                    s_action = f'{GAME_CONSTANTS["ACTION"]["CITYTILE"]["BUILD_CART"]} {n_x} {n_y}'
                else:
                    logging.error(f"Invalid Citytile action: {n_max_q_index}")
                    return list()
                #add action string to list of actionstrings for this turn
                ls_actions_citytile.append(s_action)

        return ls_actions_citytile

    def _translate_unit_actions( self ) -> list:
        """Translates citytile actions into a list of string actions to be fed to the game engine
        Requires output spacial matricies. Requires dictionary of unit->position, reverse translation
            list: list of citytile string actions to be fed to the game engine
                e.g. ["m u_1 n", "bcity u_4"]
        """

        return list()

    #----------------    Public Members    ----------------

    def fill_mats( self, id_units : dict, ils_actions : list ):

        #finally call the parser that decodes a list of string actions filling the output mat
        if self._parse_agent_actions( id_units, ils_actions ) == True:
            logging.error(f"failed to parse string actions: {ils_actions}")
            return True

        return False

    def translate( self ) -> list:
        """Translates actions into a list of string actions to be fed to the game engine
        Requires output spacial matricies and dictionary of units to perform the translation
        Returns:
            list: list actions to be fed to the game engine
                e.g. ["r 14 8", "m u_1 w"]
        """

        #allocate list of string actions to empty
        ls_actions = list()

        #translate citytile actions
        ls_actions_citytiles = self._translate_citytile_actions()
        if ls_actions_citytiles is None:
            logging.error(f"failed to parse citytile actions")
            return list()
        #concatenate
        ls_actions += ls_actions_citytiles

        # translate unit actions
        ls_actions_units = self._translate_unit_actions()
        if ls_actions_units is None:
            logging.error(f"failed to parse unit actions")
            return list()
        #concatenate
        ls_actions += ls_actions_units

        #logging.debug(f"{ls_actions_citytiles}")
        return ls_actions
