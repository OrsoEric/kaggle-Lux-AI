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
import pickle

import numpy as np

#LUX-AI-2021
from lux.constants import GAME_CONSTANTS
from lux.game import Game
from lux.game_map import Position

#plot
import matplotlib.pyplot as plt
import seaborn as sns
#convert input matricies into .gif
import matplotlib.animation as animation

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
        #combined Citytile Fuel matrix
        CITYTILE_FUEL = 0,

        #Combined Worker Resource matrix
        WORKER_RESOURCE = 1,

        #Combined Cart Resource matrix
        CART_RESOURCE = 2,

        #Combined cooldown matrix
        #COOLDOWN = 4,


        
        
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
        logging.debug(f"Allocating input spacial matricies: {len(Perception.E_INPUT_SPACIAL_MATRICIES)} | shape: {self.mats.shape}")
        #fill the perception matrix
        self.invalid = self._generate_perception()
        Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL
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
        #Scan all Own Unit
        for c_unit in self._c_own.units:
            #resources carried by the unit
            n_resources = c_unit.cargo.wood +c_unit.cargo.coal +c_unit.cargo.uranium
            #unit position
            c_pos = c_unit.pos
            if self._check_bounds_pos( c_pos ) == True:
                    return True
            #Workers fit the combined Worker/Resource matrix
            if c_unit.is_worker():
                #accumulate this worker resource in the combined Worker/Resource matrix
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.WORKER_RESOURCE.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] += +GAME_CONSTANTS["PERCEPTION"]["INPUT_UNIT_RESOURCE_OFFSET"] +n_resources

            #Handle carts
            elif c_unit.is_cart():
                #accumulate this worker resource in the combined Worker/Resource matrix
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.CART_RESOURCE.value, self._w_shift +c_pos.x, self._h_shift +c_pos.y] += +GAME_CONSTANTS["PERCEPTION"]["INPUT_UNIT_RESOURCE_OFFSET"] +n_resources

            #Default Case:
            else:
                #ERROR!!! Unknown unit
                logging.critical(f"Unit type is unknown: {c_unit}")
                return True

                #iterate over all units


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
    fig = plt.figure()
    dimension = (32, 32)

    def draw_heatmap( data ):
        plt.clf()
        sns.heatmap(data, center=0, vmin=-100, vmax=100)

    draw_heatmap( np.zeros(dimension) )

    def init():
        
        draw_heatmap( np.zeros(dimension)  )

    def animate(i):
        draw_heatmap( ilc_list_perception[i].mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value[0] ] )
        logging.debug(f"generating heatmap{i} ...")

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(ilc_list_perception), repeat=False, save_count=len(ilc_list_perception))
    anim.save( is_filename, writer='pillow', fps=in_framerate )
    logging.debug(f"saving heatmaps as: {is_filename} | total frames: {len(ilc_list_perception)}")

    return
