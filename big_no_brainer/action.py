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

    def __init__( self, ic_json : json, ild_units : list, in_player : int ):
        """Constructor. Initialize mats and vars

        Args:
            ic_json (json): opened replay.json
            ild_units (list): list of dictionaries of units and their position. required to decode actions. one per turn, 360 turn per game.
                e.g. { u_1 : ( 11, 17 ), u_5 : ( 12, 17 ) }
            in_player (int): player for which Action is to be extracted. 2 player in a replay.json
        """

        #initialize class vars
        if self.__init_vars():
            logging.critical( f"Failed to initialize class vars" )

        #from a json generate a list of list of actions, one list of actions for a given player
        lls_actions  = self._generate_list_action( ic_json, in_player )
        #from a list of list of string action and a list dictionaries of units fill the output mats
        self._fill_action_mats( ild_units, lls_actions )

        return

    #----------------    Private Members    ----------------

    def __init_vars( self ) -> bool:
        """Initialize class vars
        Returns:
            bool: False=OK | True=FAIL
        """
        self.mats = np.zeros( (len(Action.E_OUTPUT_SPACIAL_MATRICIES), GAME_CONSTANTS['MAP']['WIDTH_MAX'], GAME_CONSTANTS['MAP']['HEIGHT_MAX']) )

        #self._w_shift = (GAME_CONSTANTS['MAP']['WIDTH_MAX'] -ic_game_state.map_width) // 2
        #self._h_shift = (GAME_CONSTANTS['MAP']['HEIGHT_MAX'] -ic_game_state.map_height) // 2

        return False

    #----------------    Protected Members    ----------------

    def _generate_list_action( self, ic_json : json, in_player : int ) ->list:
        """AI is creating summary for _generate_list_action
        Args:
            ic_json (json): opened replay.json
            in_player (int): index of the player for which actions are to be computed. two players in a game
        Returns:
            list: list of string action. e.g.
                [["r 14 8", "m u_1 w"]
                [""]
                ["m u_1 w"]]
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
                #if player the indexed one, is active or the game is about to be done
                if n_id == in_player and (c_player["status"] == "ACTIVE" or c_player["status"] == "DONE"):
                    #fetch the list of actions the player took in the previous turn
                    #From JSON, From Steps (list of turns), from a given step (turn index), from player 0, is player is active (not dead)
                    ls_actions = c_player['action']
                    #logging.debug(f"Step: {n_step} | Action: {ls_actions}")
                    #append to list of list of string actions
                    lls_player_action.append( ls_actions )

        logging.debug(f"Player {in_player} | Action strings decoded: {len(lls_player_action)}")

        return lls_player_action

    def _fill_action_mats( self, ild_units : list, ills_actions : list ) -> bool:
        #check input
        if len(ild_units) != GAME_CONSTANTS["PARAMETERS"]["MAX_DAYS"] or len(ills_actions) != GAME_CONSTANTS["PARAMETERS"]["MAX_DAYS"]+1:
            logging.error(f"Unexpected input length | Dictionary Units: {len(ild_units)} | List of string actions: {len(ills_actions)}")

        #drop first string action. Perception(Step 0) <=> Action(Step = 1)
        ills_actions.pop( 0 )
        #scan dictionary of units and string action of the same turn
        for d_units, ls_actions in zip( ild_units, ills_actions ):
            #logging.debug(f" Dictionary: {d_units} | String actions: {ls_actions}")
            #finally call the parser that decodes a list of string actions filling the output mat
            if self._parse_agent_actions( d_units, ls_actions ) == True:
                logging.error(f"failed to parse string actions: {ls_actions}")
                return True

        return False

    #----------------    Public Members    ----------------

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
                    logging.error(f'Expected 3 tokens on action: { GAME_CONSTANTS["ACTION"]["CITYTILE"]["RESEARCH"] } but got {len(ls_action_token)} instead.')
                
                n_x = int(ls_action_token[1])
                n_y = int(ls_action_token[2])
                logging.debug(f"R {n_x} {n_y}")
                self.mats[Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_RESEARCH.value, n_x, n_y] += 1
            else:
                logging.debug(f"Unknown header: {s_header}")
                pass
                

        logging.debug(f"total research: {self.mats[Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_RESEARCH.value].sum()}")
        return False


