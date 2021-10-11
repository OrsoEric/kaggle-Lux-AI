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

    def __init__( self ):
        """Constructor. Initialize mats and vars
        """

        #initialize class vars
        if self.__init_vars():
            logging.critical( f"Failed to initialize class vars" )

        return

    #----------------    Private Members    ----------------

    def __init_vars( self ) -> bool:
        """Initialize class vars
        Returns:
            bool: False=OK | True=FAIL
        """
        self.mats = np.zeros( (len(Action.E_OUTPUT_SPACIAL_MATRICIES), GAME_CONSTANTS['MAP']['WIDTH_MAX'], GAME_CONSTANTS['MAP']['HEIGHT_MAX']) )

        return False

    #----------------    Protected Members    ----------------

    #----------------    Public Members    ----------------

    def _parse_agent_actions( self, ils_actions : list, id_units : dict ) -> bool:
        """Parse a string of actions into an initialized Action class
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
            


        return False


