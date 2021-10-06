##  @package big_no_brainer
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

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

import logging
#enumeration support
from enum import Enum, auto
import numpy as np
#LUX-AI-2021
from lux.constants import GAME_CONSTANTS
from lux.game import Game


#--------------------------------------------------------------------------------------------------------------------------------
#   Perception
#--------------------------------------------------------------------------------------------------------------------------------

class Perception():

    #----------------    Configurations    ----------------

    #Turn number
    #turn inside the day cylce
    #day/night information?
    #research level for own and enemy
    #total number of city own/enemy
    #total number of citytiles own/enemy
    #total number of units own enemy
    #total number of workers own enemy
    #total number of carts own enemy
    #total number of fuel own enemy
    #total number of resources own enemy
    #total number of resources left on map own enemy
    
    #enumerate state vector that describe game wide information, will bypass the spatial processing stage
    class E_INPUT_STATUS_VECTOR( Enum ):
        MAP_TURN = auto(),
        MAP_IS_NIGHT = auto(),
        OWN_RESEARCH = auto(),
        OWN_RESEARCHED_COAL = auto(),
        OWN_RESEARCHED_URANIUM = auto(),
        ENEMY_RESEARCH = auto(),
        ENEMY_RESEARCHED_COAL = auto(),
        ENEMY_RESEARCHED_URANIUM = auto(),
        #number of global state variables
        NUM = auto(),

    #enumerate possible types of cell {5+6+12+8=31} * {Width} * {Height}
    class E_INPUT_SPACIAL_MATRICIES( Enum ):
        #combined citytile fuel matrix
        CITYTILE_FUEL = auto(),
        #Combined cooldown matrix
        COOLDOWN = auto(),

    class Dummy(Enum):
        #Resources 5 * {Width} * {Height}
        MAP_RESOURCE_ALL = auto(),
        MAP_RESOURCE_WOOD = auto(),
        MAP_RESOURCE_COAL = auto(),
        MAP_RESOURCE_URANIUM = auto(),
        MAP_ROAD_LEVEL = auto(),

        #CityTiles 6 * {Width} * {Height}
        OWN_CITYTILES = auto(),
        OWN_CITYTILES_MAINTENANCE = auto(),
        OWN_CITYTILES_FUEL = auto(),
        ENEMY_CITYTILES = auto(),
        ENEMY_CITYTILES_MAINTENANCE = auto(),
        ENEMY_CITYTILES_FUEL = auto(),

        #Units 12 * {Width} * {Height}
        OWN_UNITS = auto(),
        OWN_WORKERS = auto(),
        OWN_CARTS = auto(),
        OWN_UNIT_RESOURCE_ALL = auto(),
        OWN_UNIT_RESOURCE_WOOD = auto(),
        OWN_UNIT_RESOURCE_COAL = auto(),
        OWN_UNIT_RESOURCE_URANIUM = auto(),
        ENEMY_UNITS = auto(),
        ENEMY_WORKERS = auto(),
        ENEMY_CARTS = auto(),
        ENEMY_UNIT_RESOURCE_ALL = auto(),
        ENEMY_UNIT_RESOURCE_WOOD = auto(),
        ENEMY_UNIT_RESOURCE_COAL = auto(),
        ENEMY_UNIT_RESOURCE_URANIUM = auto(),
        
        #Cooldowns 8 * {Width} * {Height} 
        OWN_COOLDOWNS_ALL = auto(),
        OWN_COOLDOWN_CITYTILES = auto(),
        OWN_COOLDOWN_WORKERS = auto(),
        OWN_COOLDOWN_CARTS = auto(),
        ENEMY_COOLDOWNS_ALL = auto(),
        ENEMY_COOLDOWN_CITYTILES = auto(),
        ENEMY_COOLDOWN_WORKERS = auto(),
        ENEMY_COOLDOWN_CARTS = auto(),
        #number of spacial state variables
        NUM = auto(),
        
        
       

    #----------------    Constructor    ----------------

    def __init__( self, ic_game_state : Game ):
        """Construct perception class based on a game state
        Args:
            ic_game_state (Game): Current game state
        """
        #store locally the game state. Not visible from outside
        self._c_map = ic_game_state.map
        self._c_own = ic_game_state.players[ ic_game_state.id ]
        self._c_enemy = ic_game_state.players[ ic_game_state.opponent_id ]

        #initialize perception matricies
        self.mats = np.zeros( (20, GAME_CONSTANTS['MAP']['WIDTH_MAX'], GAME_CONSTANTS['MAP']['HEIGHT_MAX']) )
        #fill the perception matrix
        self.invalid = self._generate_perception()

        return

    #----------------    Overloads    ---------------

    ## Stringfy class for print method
    def __str__(self) -> str:
        return f"Perception{self._game}"

    #----------------    Protected    ---------------

    def _generate_citytile_fuel_matrix( self ) -> bool:
        """Combined CItytile Fuel map for both own and enemy
        Matrix size: MAP_WIDTH_MAX *MAP_HEIGHT_MAX
        Smaller maps are centered, with outer zeros
        1+City.Fuel         -> The cell is a Own Citytile, with an amount of fuel equal to City.Fuel=Value-1
        1                   -> The cell is a Own Citytile with 0 Fuel
        0                   -> The cell is not a Citytile
        -1                  -> The cell is an Enemy Citytile with 0 Fuel
        -1-City.Fuel        -> The cell is a Enemy Citytile, with an amount of fuel equal to City.Fuel=1-Value
        All citytiles belonging to a city share the same fuel reserve 

        Returns:
            bool: False=OK | True=FAIL
        """
        
        for c_city in self._c_own.cities:
            pass


        return False

    def _generate_perception( self ) -> bool:
        """Runs the generation of all perception matricies
        Returns:
            bool: False=OK | True=FAIL
        """
        
        if self._generate_citytile_fuel_matrix():
            return True

        return False

    #----------------    Public    ---------------

    def compute_perception( self ):


        return


