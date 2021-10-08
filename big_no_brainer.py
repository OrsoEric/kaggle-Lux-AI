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
        CITYTILE_FUEL = 0,

        #Combined cooldown matrix
        COOLDOWN = 1,

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
        #scan all Own Cities in the dictionary of cities
        for s_city_name, c_city in self._c_own.cities.items():
            #scan all Citytiles in a City
            for c_citytile in c_city.citytiles:
                #get citytile position
                c_pos = c_citytile.pos
                #write city fuel information inside the Own Citytile Fuel mat
                logging.debug(Perception.E_INPUT_SPACIAL_MATRICIES["CITYTILE_FUEL"].value)
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value, c_pos.x, c_pos.y] = GAME_CONSTANTS["PERCEPTION"]["INPUT_CITYTILE_FUEL_OFFSET"] + c_city.fuel

            pass

        #scan all Enemy Cities in the dictionary of cities
        for s_city_name, c_city in self._c_enemy.cities.items():
            #scan all Citytiles in a City
            for c_citytile in c_city.citytiles:
                #get citytile position
                c_pos = c_citytile.pos
                #write city fuel information inside the Own Citytile Fuel mat
                logging.debug(Perception.E_INPUT_SPACIAL_MATRICIES["CITYTILE_FUEL"].value)
                self.mats[Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value, c_pos.x, c_pos.y] = -GAME_CONSTANTS["PERCEPTION"]["INPUT_CITYTILE_FUEL_OFFSET"] -c_city.fuel

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

#--------------------------------------------------------------------------------------------------------------------------------
#   Save Heatmaps
#--------------------------------------------------------------------------------------------------------------------------------

#plot
import matplotlib.pyplot as plt
import seaborn as sns
#convert input matricies into .gif
import matplotlib.animation as animation

def save_list_perception( ilc_list_perception : list, is_filename : str ):

    fig = plt.figure()
    dimension = (32, 32)
    data = np.random.rand(dimension[0], dimension[1])
    sns.heatmap(data, center=0, vmin=-100, vmax=100)

    def init():
        plt.clf()
        sns.heatmap(np.zeros(dimension), center=0, vmin=-100, vmax=100 )

    def animate(i):
        plt.clf()
        c_data = ilc_list_perception[i].mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value[0] ]
        #data = np.random.rand(dimension[0], dimension[1])
        sns.heatmap(c_data, center=0, vmin=-100, vmax=100 )

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(ilc_list_perception), repeat=False)
    anim.save( is_filename, writer='pillow', fps=2)
    
    return
