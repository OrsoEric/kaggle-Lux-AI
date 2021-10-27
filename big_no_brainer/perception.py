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

#--------------------------------------------------------------------------------------------------------------------------------
#   Perception
#--------------------------------------------------------------------------------------------------------------------------------

class Perception():
    """There are 8 matrices:

    (V) Cities matrix: every tile has a value of +fuel+1 for bot's cities and -fuel-1 for opponent's cities
    (V) Workers matrix: every tile has a value of +resources+1 for boot's workers and -resources-1 for opponent's ones
    (V) Cart matrix: as workers matrix
    (V) Wood matrix: amount of wood per tile
    (V) Coal matrix: as wood
    (V) Uranium matrix: as wood
    (V) Road matrix: road value per tile
    (V) Cooldown matrix: Bot's cooldown with negative sign, opponent's cooldown positive
    """
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
        MAP_SIZE = 0
        MAP_TURN = auto()
        MAP_IS_NIGHT = auto()
        OWN_RESEARCH = auto()
        OWN_RESEARCHED_COAL = auto()
        OWN_RESEARCHED_URANIUM = auto()
        ENEMY_RESEARCH = auto()
        ENEMY_RESEARCHED_COAL = auto()
        ENEMY_RESEARCHED_URANIUM = auto()

	#NOTE: the enum were tuple because i put a coma like a c++ enum.
    #enumerate possible types of cell {5+6+12+8=31} * {Width} * {Height}
    class E_INPUT_SPACIAL_MATRICIES( Enum ):
        #combined Citytile Fuel matrix
        CITYTILE_FUEL = 0
        #Combined Worker Resource matrix
        WORKER_RESOURCE = auto()
        #Combined Cart Resource matrix
        CART_RESOURCE = auto()
        #Individual Resource Cell matricies
        RAW_WOOD = auto()
        RAW_COAL = auto()
        RAW_URANIUM = auto()
        #Roads Matrix
        ROAD = auto()
        #Combined cooldown matrix for units/cities own/enemy
        COOLDOWN = auto()

    #----------------    Constructor    ----------------

    def __init__( self ):
        """Construct perception class based on a game state
        """

        #initialize class vars
        self.__init_vars()

        return

    #----------------    Private Members    ---------------

    def __init_vars( self ) -> bool:
        """Initialize class vars
        Returns:
            bool: False=OK | True=FAIL
        """

        #initialize to invalid
        self.invalid = True
        #allocate the status vector
        self.status = np.zeros( len(Perception.E_INPUT_STATUS_VECTOR) )
        #initialize perception matricies
        self.mats = np.zeros( (len(Perception.E_INPUT_SPACIAL_MATRICIES), GAME_CONSTANTS['MAP']['WIDTH_MAX'], GAME_CONSTANTS['MAP']['HEIGHT_MAX']) )
        #dictionary of units on the map
        self.d_unit = None

        return False

    #----------------    Overloads    ---------------

    ## Stringfy class for print method
    def __str__(self) -> str:
        return f"Perception | Raw Wood: {self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.RAW_WOOD.value].sum()} | "

    #----------------    Protected    ---------------

    def _check_bounds( self, in_x : int, in_y : int ) -> bool:
        """pedantic check if the position is within map boundaries
        Args:
            in_x (int): x/width position
            in_y (int): y/height position
        Returns:
            bool: False=OK | True=FAIL
        """
        if (self._w_shift +in_x) < 0 or (self._w_shift +in_x) >= GAME_CONSTANTS['MAP']['WIDTH_MAX']:
            logging.critical(f"XW dimension is out of bound | offset: {self._w_shift} | index: {in_x} | limit: {GAME_CONSTANTS['MAP']['WIDTH_MAX']}")
            return True
        if (self._h_shift +in_y) < 0 or (self._h_shift +in_y) >= GAME_CONSTANTS['MAP']['HEIGHT_MAX']:
            logging.critical(f"HY dimension is out of bound | offset: {self._h_shift} | index: {in_y} | limit: {GAME_CONSTANTS['MAP']['HEIGHT_MAX']}")
            return True
        return False

    def _check_bounds_pos( self, in_pos : Position ) -> bool:
        return self._check_bounds( in_pos.x, in_pos.y )

    def _generate_citytile_fuel_matrix( self ) -> bool:
        """Combined CItytile/Fuel matrix for both own and enemy
        Matrix size: MAP_WIDTH_MAX *MAP_HEIGHT_MAX
        Smaller maps are centered, with outer zeros
        Offset+City.Fuel        -> The cell is a Own Citytile, with an amount of fuel equal to City.Fuel=Value-Offset (+10=+11-1)
        Offset                  -> The cell is a Own Citytile with 0 Fuel
        0                       -> The cell is not a Citytile
        -Offset                 -> The cell is an Enemy Citytile with 0 Fuel
        -Offset-City.Fuel       -> The cell is an Enemy Citytile, with an amount of fuel equal to City.Fuel=-Value-Offset (+10=-(-11)-1)
        All citytiles belonging to a city share the same fuel reserve 
        Game constant GAME_CONSTANTS["PERCEPTION"]["INPUT_CITYTILE_FUEL_OFFSET"] specify what the offset is

        Returns:
            bool: False=OK | True=FAIL
        """
        #scan all Own Cities in the dictionary of cities
        for s_city_name, c_city in self._c_own.cities.items():
            #scan all Citytiles in a City
            for c_citytile in c_city.citytiles:
                #get citytile position
                c_pos = c_citytile.pos
                if self._check_bounds( c_pos.x, c_pos.y ) == True:
                    return True
                #write city fuel information inside the Own Citytile Fuel mat
                #logging.debug(Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value)
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] = GAME_CONSTANTS["PERCEPTION"]["INPUT_CITYTILE_FUEL_OFFSET"] + c_city.fuel
 
            pass

        #scan all Enemy Cities in the dictionary of cities
        for s_city_name, c_city in self._c_enemy.cities.items():
            #scan all Citytiles in a City
            for c_citytile in c_city.citytiles:
                #get citytile position
                c_pos = c_citytile.pos
                if self._check_bounds( c_pos.x, c_pos.y ) == True:
                    return True
                #write city fuel information inside the Own Citytile Fuel mat
                #logging.debug(Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value)
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] = -GAME_CONSTANTS["PERCEPTION"]["INPUT_CITYTILE_FUEL_OFFSET"] -c_city.fuel
        return False

    def _generate_unit_resource_matrix(self):
        """Combined Worker/Resource map for both own and enemy
        Combined Cart/Resource map for both own and enemy
        Matrix size: MAP_WIDTH_MAX *MAP_HEIGHT_MAX
        Smaller maps are centered, with outer values set to zero
        Offset+Unit.Resource    -> The cell is a Own Worker/Cart, with an amount of resources equal to Unit.Resource=Value-Offset
        Offset                  -> The cell is a Own Worker/Cart with 0 Resources
        0                       -> The cell is not a Worker/Cart
        -Offset                 -> The cell is an Enemy Worker/Cart with 0 Fuel
        -Offset-Unit.Resource   -> The cell is an Enemy Worker/Cart, with an amount of fuel equal to Unit.Resource=-Value-Offset
        All citytiles belonging to a city share the same fuel reserve 
        Game constant GAME_CONSTANTS["PERCEPTION"]["INPUT_CITYTILE_FUEL_OFFSET"] specify what the offset is

        Returns:
            bool: False=OK | True=FAIL
        """

        def push_unit( ic_unit : Unit, ix_is_enemy : bool ) -> bool:
            """helper function that push an unit in the appropriate matrix
            Args:
                ic_unit (Unit): [description]
            Returns:
                bool: False=OK | True=FAIL
            """
            #resources carried by the unit
            n_resources = c_unit.cargo.wood +c_unit.cargo.coal +c_unit.cargo.uranium
            #Own units have an offset and positive resources
            if ix_is_enemy == False:
                n_fill_value = GAME_CONSTANTS["PERCEPTION"]["INPUT_UNIT_RESOURCE_OFFSET"] +n_resources
            #Enemy units have negative offset and resources
            else:
                n_fill_value = -GAME_CONSTANTS["PERCEPTION"]["INPUT_UNIT_RESOURCE_OFFSET"] -n_resources
            #fetch unit position
            c_pos = c_unit.pos
            if self._check_bounds_pos( c_pos ) == True:
                return True            
            #Workers fit the combined Worker/Resource matrix
            if c_unit.is_worker():
                #accumulate this worker resource in the combined Worker/Resource matrix
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.WORKER_RESOURCE.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] += n_fill_value
            #Carts fit the combined Worker/Resource matrix
            elif c_unit.is_cart():
                #accumulate this worker resource in the combined Worker/Resource matrix
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.CART_RESOURCE.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] += n_fill_value
            #Default Case:
            else:
                #ERROR!!! Unknown unit
                logging.critical(f"Unit type is unknown: {c_unit}")
                return True
            return False

        #Scan all Own Unit
        for c_unit in self._c_own.units:
            #fit the unit in the appropriate matrix with +sign for resource
            push_unit(c_unit, False)
            
        #Scan all Enemy Unit
        for c_unit in self._c_enemy.units:
            #fit the unit in the appropriate matrix with +sign for resource
            push_unit(c_unit, True)

        return False

    def _generate_raw_resource_road_matrix( self ) -> bool:
        """Generate input spacial matrix, all map sizes are centered
        All roads are friendly and reduce CD. Roads below a city are 6 and disappear when the city does.
        Returns:
            bool: False=OK | True=FAIL
        """
        #scan every 2D coordinate on the map
        for w, h in product( range( self._c_map.width ), range( self._c_map.height ) ):
            #Fetch the cell
            c_cell = self._c_map.get_cell( w, h )
            #Fetch position
            c_pos = c_cell.pos
            if self._check_bounds_pos( c_pos ) == True:
                return True
            #if the cell is not a Raw resource
            if c_cell.has_resource() == False:
                pass
            #cell is a Raw Resource
            elif (c_cell.resource.type == RESOURCE_TYPES.WOOD ):
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.RAW_WOOD.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] = c_cell.resource.amount
            elif (c_cell.resource.type == RESOURCE_TYPES.COAL ):
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.RAW_COAL.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] = c_cell.resource.amount
            elif (c_cell.resource.type == RESOURCE_TYPES.URANIUM ):
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.RAW_URANIUM.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] = c_cell.resource.amount
            #cell is not a Raw Resource
            else:
                logging.critical(f"Cell is not a Resource but it should be. {c_cell}")
                pass

            #save the road level as well since I'm scanning the cells
            self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] = c_cell.road

        #logging.info(f"Resource: {self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.RAW_WOOD.value].sum()} {self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.RAW_COAL.value].sum()} {self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.RAW_URANIUM.value].sum()}")
        #logging.info(f"Road: {self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value].sum()}")
        return False

    def _generate_cooldown( self ) -> bool:
        """Generate input spacial matrix, all map sizes are centered
        own have positive CD, enemy have negative CD
        Returns:
            bool: False=OK | True=FAIL
        """
        def push_cooldown( c_pos : Position, in_cooldown : int, ix_is_enemy : bool ) -> bool:

            if in_cooldown < 0 or in_cooldown > GAME_CONSTANTS["PARAMETERS"]["CITY_ACTION_COOLDOWN"]:
                logging.critical(f"Cooldown is invalid {in_cooldown}")
                return True
            #Own units have an offset and positive resources
            if ix_is_enemy == False:
                n_fill_value = GAME_CONSTANTS["PERCEPTION"]["INPUT_COOLDOWN_OFFSET"] +in_cooldown
            #Enemy units have negative offset and resources
            else:
                n_fill_value = -GAME_CONSTANTS["PERCEPTION"]["INPUT_COOLDOWN_OFFSET"] -in_cooldown
            #fetch unit position
            c_pos = c_unit.pos
            if self._check_bounds_pos( c_pos ) == True:
                logging.critical(f"Position is invalid {c_pos}")
                return True            
            #accumulate cooldown in the cooldown matrix
            self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.COOLDOWN.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] += n_fill_value
            #logging.debug(f"Pos {self._w_shift +c_pos.x} {self._h_shift +c_pos.y} | {ix_is_enemy} | {n_fill_value}")

            return False

        #Scan all Own Unit
        for c_unit in self._c_own.units:
            #fit cooldown with +sign for resource
            push_cooldown( c_unit.pos, c_unit.cooldown, False )
            
        #Scan all Enemy Unit
        for c_unit in self._c_enemy.units:
            #fit cooldown with +sign for resource
            push_cooldown( c_unit.pos, c_unit.cooldown, True )

        #scan all Own Cities in the dictionary of cities
        for s_city_name, c_city in self._c_own.cities.items():
            #scan all Citytiles in a City
            for c_citytile in c_city.citytiles:
                #get citytile position
                c_pos = c_citytile.pos
                if self._check_bounds_pos( c_pos ) == True:
                    return True
                #write city cooldown information 
                push_cooldown( c_citytile.pos, c_citytile.cooldown, False )

        #scan all Enemy Cities in the dictionary of cities
        for s_city_name, c_city in self._c_enemy.cities.items():
            #scan all Citytiles in a City
            for c_citytile in c_city.citytiles:
                #get citytile position
                c_pos = c_citytile.pos
                if self._check_bounds_pos( c_pos ) == True:
                    return True
                #write city cooldown information 
                push_cooldown( c_citytile.pos, c_citytile.cooldown, True )

        #logging.debug(f"CD: {self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.COOLDOWN.value].sum()}") 
        return False

    def _generate_status_vector( self ):
        """Generate the status vector to be fed in input of the ML
        Returns:
            bool: False=OK | True=FAIL
        """

        #
        self.status[ Perception.E_INPUT_STATUS_VECTOR.MAP_SIZE.value ] = self._c_map.width
        self.status[ Perception.E_INPUT_STATUS_VECTOR.MAP_TURN.value ] = self.n_turn

        self.status[ Perception.E_INPUT_STATUS_VECTOR.OWN_RESEARCH.value ] = self._c_own.research_points
        self.status[ Perception.E_INPUT_STATUS_VECTOR.OWN_RESEARCHED_COAL.value ] = self._c_own.researched_coal()
        self.status[ Perception.E_INPUT_STATUS_VECTOR.OWN_RESEARCHED_URANIUM.value ] = self._c_own.researched_uranium()
        self.status[ Perception.E_INPUT_STATUS_VECTOR.ENEMY_RESEARCH.value ] = self._c_enemy.research_points
        self.status[ Perception.E_INPUT_STATUS_VECTOR.ENEMY_RESEARCHED_COAL.value ] = self._c_enemy.researched_coal()
        self.status[ Perception.E_INPUT_STATUS_VECTOR.ENEMY_RESEARCHED_URANIUM.value ] = self._c_enemy.researched_uranium()

        return False
    
    def _generate_dictionary_unit( self ) -> bool:
        """Generates a dictionary of units in the form:
        {
            u_1 : ( 11, 17 ),
            u_5 : ( 12, 17 ),
        }
        Action needs to translate ID of unit into its position.
        Returns:
            bool: False=OK | True=FAIL
        """

        d_unit = dict()

        #Scan all Own Unit
        for c_unit in self._c_own.units:
            d_unit[c_unit.id] = ( c_unit.pos.x, c_unit.pos.y )
            
        #Scan all Enemy Unit
        for c_unit in self._c_enemy.units:
            d_unit[c_unit.id] = ( c_unit.pos.x, c_unit.pos.y )
        
        self.d_unit = d_unit
        #logging.debug(f"Unit Dictionary: {d_unit}")
        return False

    #----------------    Public    ---------------

    def from_game( self, ic_game_state : Game ) -> bool:
        """fill the Perception class from a Game() class
        Args:
            ic_game_state (Game): Current game state
        Returns:
            bool: False=OK | True=FAIL
        """
        
        #turn index
        self.n_turn = ic_game_state.turn

        #store locally the game state. Not visible from outside
        self._c_map = ic_game_state.map
        self._c_own = ic_game_state.players[ ic_game_state.id ]
        self._c_enemy = ic_game_state.players[ ic_game_state.opponent_id ]
        #tiles are shifted so that all map sizes are centered
        self._w_shift = (GAME_CONSTANTS['MAP']['WIDTH_MAX'] -ic_game_state.map_width) // 2
        self._h_shift = (GAME_CONSTANTS['MAP']['HEIGHT_MAX'] -ic_game_state.map_height) // 2

        #reset to valid
        self.invalid = False
        #fill the ML input status vector
        self.invalid |= self._generate_status_vector()
        #fill the ML input spacial matricies
        self.invalid |= self._generate_unit_resource_matrix()
        self.invalid |= self._generate_raw_resource_road_matrix()
        self.invalid |= self._generate_cooldown()
        self.invalid |= self._generate_dictionary_unit()

        return False

#--------------------------------------------------------------------------------------------------------------------------------
#   Save/Load Pickle
#--------------------------------------------------------------------------------------------------------------------------------

def save_perceptions( ilc_perceptions : list, is_file_name : str ) -> bool:
    """save a game state to file
    Args:
        ilc_perceptions (list(Game)): perceptions to be saved
        is_file_name (str): destination file name 
    Returns:
        bool: false: success | true: fail
    """
    
    try:
        with open(is_file_name, "wb") as opened_file:
            pickle.dump( ilc_perceptions, opened_file )

    except OSError as problem:
        logging.critical(f"Pickle: {problem}")
        return True

    return False

##  load a game state to file
#   uses pickle
def load_perceptions( is_file_name : str ):
    """load a game state to file
    Args:
        is_file_name (str): source file name 
    Returns:
        Game: loaded game state
    """
    
    try:
        with open(is_file_name, "rb") as opened_file:
            logging.debug(f"opened: {opened_file}")
            lc_perceptions = pickle.load( opened_file )

    except OSError as problem:
        logging.critical(f"Pickle: {problem}")
        return None

    return lc_perceptions
