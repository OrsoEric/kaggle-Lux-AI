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

    #(3+7+5)*32*32 = 15*32*32
    #enumerate state vector that describe game wide information, will bypass the spatial processing stage. Total 15 actions
    class E_OUTPUT_SPACIAL_MATRICIES( Enum ):
        #Citytile Actions. 3*32*32
        CITYTILE_RESEARCH = 0
        CITYTILE_BUILD_WORKER = auto()
        CITYTILE_BUILD_CART = auto()
        #Worker actions 7*32*32
        WORKER_MOVE_NORTH = auto()
        WORKER_MOVE_EAST = auto()
        WORKER_MOVE_SOUTH = auto()
        WORKER_MOVE_WEST = auto()
        WORKER_TRANSFER_RESOURCE = auto()
        WORKER_BUILD_CITY = auto()
        WORKER_PILLAGE_ROAD = auto()
        #Cart Actions 5*32*32
        CART_MOVE_NORTH = auto()
        CART_MOVE_EAST = auto()
        CART_MOVE_SOUTH = auto()
        CART_MOVE_WEST = auto()
        CART_TRANSFER_RESOURCE = auto()


    #----------------    Constructor    ----------------