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

#plot
import matplotlib.pyplot as plt
import seaborn as sns
#convert input matricies into .gif
import matplotlib.animation as animation

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
    ( ) Road matrix: road value per tile
    ( ) Cooldown matrix: Bot's cooldown with negative sign, opponent's cooldown positive
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
        #combined Citytile Fuel matrix
        CITYTILE_FUEL = 0,
        #Combined Worker Resource matrix
        WORKER_RESOURCE = 1,
        #Combined Cart Resource matrix
        CART_RESOURCE = 2,
        #Individual Resource Cell matricies
        RAW_WOOD = 3,
        RAW_COAL = 4,
        RAW_URANIUM = 5,
        #Roads Matrix
        ROAD = 6
        #Combined cooldown matrix for units/cities own/enemy
        COOLDOWN = 7,

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
        #tiles are shifted so that all map sizes are centered
        self._w_shift = (GAME_CONSTANTS['MAP']['WIDTH_MAX'] - ic_game_state.map_width) // 2
        self._h_shift = (GAME_CONSTANTS['MAP']['HEIGHT_MAX'] - ic_game_state.map_height) // 2
        #initialize perception matricies
        self.mats = np.zeros( (len(Perception.E_INPUT_SPACIAL_MATRICIES), GAME_CONSTANTS['MAP']['WIDTH_MAX'], GAME_CONSTANTS['MAP']['HEIGHT_MAX']) )
        logging.info(f"Allocating input spacial matricies: {len(Perception.E_INPUT_SPACIAL_MATRICIES)} | shape: {self.mats.shape}")
        #fill the perception matrix
        self.invalid = self._generate_perception()
        self.invalid |= self._generate_unit_resource_matrix()
        self.invalid |= self._generate_raw_resource_road_matrix()

        return

    #----------------    Overloads    ---------------

    ## Stringfy class for print method
    def __str__(self) -> str:
        return f"Perception{self.mats}"

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
                logging.debug(Perception.E_INPUT_SPACIAL_MATRICIES["CITYTILE_FUEL"].value)
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
                logging.debug(Perception.E_INPUT_SPACIAL_MATRICIES["CITYTILE_FUEL"].value)
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
        logging.info(f"Road: {self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value].sum()}")
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

#--------------------------------------------------------------------------------------------------------------------------------
#   Save Heatmaps as Gifs
#--------------------------------------------------------------------------------------------------------------------------------

def gify_list_perception( ilc_list_perception : list, is_filename : str, in_framerate : int ):
    """Turn a list of perceptions into a Gif
    because of compression, there are going to be fewer frames, but the delay in them ensures the movie represent the correct output
    Args:
        ilc_list_perception (list): [description]
        is_filename (str): [description]
        in_framerate (int): [description]
    """
    logging.debug(f"saving heatmaps...")
    dimension = (32, 32)
    fig, axes = plt.subplots( nrows=3, ncols=3, figsize=(12, 12) )
    ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax31, ax32, ax33)) = axes
    
    def draw_heatmap( ic_perception: Perception ):
        #TODO only first time draw the colorbar

        #plt.clf()
        
        #CityTile/Fuel Mat
        data_citytile_fuel = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value[0] ]
        ax1.title.set_text(f"Citytile/Fuel {data_citytile_fuel.sum()}")
        sns.heatmap( data_citytile_fuel, center=0, vmin=-100, vmax=100, ax=ax1, cbar=False )

        data_worker_resource = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.WORKER_RESOURCE.value[0] ]
        ax2.title.set_text(f"Worker/Resource {data_worker_resource.sum()}")
        sns.heatmap( data_worker_resource, center=0, vmin=-100, vmax=100, ax=ax2, cbar=False )
        
        data_cart_resource = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CART_RESOURCE.value[0] ]
        ax3.title.set_text(f"Cart/Resource {data_cart_resource.sum()}")
        sns.heatmap( data_cart_resource, center=0, vmin=-100, vmax=100, ax=ax3, cbar=False )
        
        data_raw_wood = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_WOOD.value[0] ]
        data_raw_coal = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_COAL.value[0] ]
        data_raw_uranium = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_URANIUM.value[0] ]
        ax4.title.set_text(f"Raw Wood {data_raw_wood.sum()}")
        ax5.title.set_text(f"Raw Coal {data_raw_coal.sum()}")
        ax6.title.set_text(f"Raw Uranium {data_raw_uranium.sum()}")
        sns.heatmap( data_raw_wood, center=0, vmin=-100, vmax=100, ax=ax4, cbar=False )
        sns.heatmap( data_raw_coal, center=0, vmin=-100, vmax=100, ax=ax5, cbar=False )
        sns.heatmap( data_raw_uranium, center=0, vmin=-100, vmax=100, ax=ax6, cbar=False )
        
        #????? Why ROAD has a different shape???
        #logging.info(f"ROADS: {Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value} | shape: {ic_perception.mats.shape}")
        data_road = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value ]
        ax31.title.set_text(f"Raw Wood {data_road.sum()}")
        sns.heatmap( data_road, center=0, vmin=0, vmax=6, ax=ax31, cbar=False )

        return [ data_citytile_fuel.sum(), data_worker_resource.sum() ]


    draw_heatmap( ilc_list_perception[0] )

    def init():
        
        draw_heatmap( ilc_list_perception[0] )

    def animate(i):
        fig.suptitle(f"TURN: {i}", fontsize=16)
        l_sum = draw_heatmap( ilc_list_perception[i] )
        logging.info(f"generating heatmap{i} ... {l_sum}")

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(ilc_list_perception), repeat=False, save_count=len(ilc_list_perception))
    anim.save( is_filename, writer='pillow', fps=in_framerate )
    logging.debug(f"saving heatmaps as: {is_filename} | total frames: {len(ilc_list_perception)}")

    return
