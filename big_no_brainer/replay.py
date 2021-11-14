##  @package replay
#   Provide functions to convert from a json to Perception and Action
#   additionaly provides generation of a .gif to animate the content of Perception and action matricies

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

import logging

import json
import copy
import os

import numpy as np

from lux.game import Game
from lux.constants import GAME_CONSTANTS
from lux.constants import Constants
INPUT_CONSTANTS = Constants.INPUT_CONSTANTS

from big_no_brainer.perception import Perception
from big_no_brainer.action import Action

#plot
import matplotlib.pyplot as plt
import seaborn as sns
#convert input matricies into .gif
import matplotlib.animation as animation

#--------------------------------------------------------------------------------------------------------------------------------
#   REPLAY
#--------------------------------------------------------------------------------------------------------------------------------

class Replay():

    #----------------    Constructor    ----------------

    def __init__( self ):
        """Construct replay class
        """

        #initialize class vars
        #self.__init_vars()

        return

    #----------------    Private    ----------------

    def __init_vars( self ) -> bool:
        """Initialize class vars
        Returns:
            bool: False=OK | True=FAIL
        """

        self._replay_json = None
        self.lc_perception = None
        self.ld_units = None
        self.lc_actions_player0 = None
        self.lc_actions_player1 = None

        return False

    #----------------    Protected    ----------------

    def _json_observation( self, ic_json : json ):
        """From an opened replay.json extract a list of observations
        observation is a dictionary with the following fields e.g.
        'globalCityIDCount': 103, 'globalUnitIDCount': 145, 'height': 24, 'player': 0, 'remainingOverageTime': 60, 'reward': 40004, 'step': 275, 'updates':[''],  'width': 24
        Args:
            ic_json (json): replay json loaded from file and processed by json module
        Returns:
            list(str): list of observation strings. one for each step (turn in the game)
        """
        #Fetch the ID of the episode
        n_episode_id = ic_json["info"]["EpisodeId"]
        #???
        index = np.argmax([r or 0 for r in ic_json["rewards"]])
        logging.debug(f"ID: {n_episode_id} | Index: {index} | Teams: {ic_json['info']['TeamNames']}")

        #initialize list of observations
        lc_observations = list()

        #Scan every Step of the match (Turn)
        for n_step in range(len(ic_json["steps"])-1):
            #logging.debug(f"Step: {n_step} of {len(ic_json['steps'])-1}")
            #???
            if ic_json["steps"][n_step][index]["status"] == 'ACTIVE':
                #Fetch the observations of this turn
                c_observation = ic_json['steps'][n_step][0]['observation']
                #logging.debug(f"Step: {n_step} | Observations: {c_observation}")

                #append this step observations in the list of observations
                lc_observations.append( c_observation )

        logging.debug(f"Observations : {len(lc_observations)}")
        #return a list of oservations, one per Step (turn)
        return lc_observations

    def _observations_to_gamestates( self, ilc_observations : list ):
        """From game observations generate Game 
        Args:
            ilc_observations (list(observations)): [description]
        Returns:
            list(Game): List of gamestates. One per turn
        """
        global c_game_state
        lc_gamestates = list()
        #from a list of observations generates a list of Game()
        for c_observation in ilc_observations:

            if c_observation[INPUT_CONSTANTS.STEP] == 0:
                c_game_state = Game()
                c_game_state._initialize(c_observation[INPUT_CONSTANTS.UPDATES])
                c_game_state._update(c_observation[INPUT_CONSTANTS.UPDATES][2:])
                c_game_state._set_player_id( c_observation["player"] )

            else:
                c_game_state._update(c_observation[INPUT_CONSTANTS.UPDATES])

            #logging.debug(f"Step: {c_observation[INPUT_CONSTANTS.STEP]} | Gamestate: {c_game_state} ")
            lc_gamestates.append( copy.deepcopy( c_game_state ) )

        logging.debug(f"Gamestates : {len(lc_gamestates)}")
        return lc_gamestates
    
    def _generate_list_action( self, ic_json : json, in_player : int ) ->list:
        """From a JSON create a list of string actions
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

        if len(lls_player_action) != GAME_CONSTANTS["PARAMETERS"]["MAX_DAYS"]+1:
            logging.error(f"Unexpected length | List of string actions: {len(lls_player_action)}")
            return True

        #drop first string action. Perception(Step 0) <=> Action(Step = 1)
        lls_player_action.pop( 0 )

        logging.debug(f"Player {in_player} | Action strings decoded: {len(lls_player_action)}")
        return lls_player_action

    #----------------    Public    ----------------

    def json_load( self, is_folder : str, is_filename : str ) -> json:
        """Load a replay.json
        Args:
            is_folder (str): Source folder
            is_filename (str): Source name .json
        Returns:
            bool: False=OK | True=FAIL
        """
        s_filepath = os.path.join( os.getcwd(), is_folder, is_filename )
        try:
            with open(s_filepath) as c_file:
                self._replay_json = json.load( c_file )
        except:
            logging.error(f"Could not open JSON: {s_filepath}")
            return True

        #logging.debug(f"JSON: {c_opened_json}")
        return False

    def json_to_perceptions( self ):
        """From a loaded replay.json extract a list of observations
        Args:
            ic_json ([type]): [description]
        Returns:
            [type]: [description]
        """

        if self._replay_json is None:
            return None, None

        #from json loads a list of observations
        lc_observations = self._json_observation( self._replay_json )
        #from list of observations generate list of Game()
        lc_gamestates = self._observations_to_gamestates( lc_observations )
        #Allocate
        lc_perceptions = list()
        ld_units = list()
        #from a list of Game() generates a list of Perception()
        for c_gamestate in lc_gamestates:
            c_perception = Perception()
            c_perception.from_game( c_gamestate )
            logging.debug(f"Game: {c_gamestate}")
            logging.debug(f"Step: {c_perception.status[Perception.E_INPUT_STATUS_VECTOR.MAP_TURN.value]}  | Perceptions : {c_perception}")
            #add the percepton to the list of perceptions
            lc_perceptions.append( c_perception )
            #add the dictionary of units to a list of dictionaries. (redundant)
            ld_units.append( c_perception.d_unit )

        logging.debug(f"Perceptions : {len(lc_perceptions)}")
        logging.debug(f"Dictionary of units : {len(ld_units)}")
        
        self.lc_perception = lc_perceptions
        self.ld_units = ld_units

        return lc_perceptions, ld_units

    def json_to_perception_action( self ):
        """ Parse a replay.json into a list of observations and two list of actions
        The lists contain one row per step (turn) of the game

        """

        if self._replay_json is None:
            return None, None

        #from a json extract a list of perceptions, one per turn
        lc_perceptions, ld_units = self.json_to_perceptions()

        llc_actions = [None, None]
        #Scan player indexes
        for n_player_index in range(2):
            ls_actions = self._generate_list_action( self._replay_json, n_player_index )
            #initialize list of Action for Player 0
            lc_action = list()
            #scan dictionary of units and list of string actions for each step (turn) of the game
            for d_units, s_actions in zip( ld_units, ls_actions ):
                #for this step (turn), decode the Action that the Player took
                c_action = Action(  )
                c_action._set_map_size( lc_perceptions[0].status[ Perception.E_INPUT_STATUS_VECTOR.MAP_SIZE.value ] )
                c_action.fill_mats( d_units, s_actions )
                #add this step (turn) Action to the list of Action this player took over the whole game
                lc_action.append( c_action )
                #logging.debug(f"Player {n_player_index} | Action: {c_action}")
            #Sace actions for this player
            llc_actions[n_player_index] = lc_action

            #allocate sum vector
            an_sum = np.zeros( len( Action.E_OUTPUT_SPACIAL_MATRICIES ) )
            #for each action
            for c_action in lc_action:
                #scan all output spacial mats
                for e_mat_index in Action.E_OUTPUT_SPACIAL_MATRICIES:
                    an_sum[e_mat_index.value] += c_action.mats[e_mat_index.value].sum()

            #scan all actions
            for e_mat_index in Action.E_OUTPUT_SPACIAL_MATRICIES:
                #compute the total of such actions taken in the game
                logging.info(f"Player {n_player_index} | {e_mat_index.name} - Total Actions: {an_sum[ e_mat_index.value ]}")

        self.lc_actions_player0 = llc_actions[0]
        self.lc_actions_player1 = llc_actions[1]

        return lc_perceptions, llc_actions[0], llc_actions[1]

    #----------------    Public Plot    ----------------

    def perceptions_to_gif( self, is_filename : str, in_framerate : int, in_max_frames = -1 ):
        """Turn a list of perceptions into a Gif
        because of compression, there are going to be fewer frames, but the delay in them ensures the movie represent the correct output
        Args:
            ilc_list_perception (list): list of Perception classes
            is_filename (str): name of the output gif. must be a .gif
            in_framerate (int): Framerate in FPS
            in_max_frames(int): -1=gify ALL the frames | >0 gify only up to a given number of frames
        """
        logging.debug(f"saving heatmaps...")
        dimension = (32, 32)
        fig, axes = plt.subplots( nrows=3, ncols=3, figsize=(12, 12) )
        ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax31, ax32, ax33)) = axes
        
        def draw_heatmap( ic_perception: Perception ):
            #TODO only first time draw the colorbar

            #plt.clf()
            
            #CityTile/Fuel Mat
            data_citytile_fuel = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value ]
            ax1.title.set_text(f"Citytile/Fuel {data_citytile_fuel.sum()}")
            #sns.heatmap( data_citytile_fuel, center=0, vmin=-100, vmax=100, ax=ax1, cbar=False, cmap="coolwarm" )
            sns.heatmap( data_citytile_fuel, center=0, vmin=-100, vmax=100, ax=ax1, cbar=False )

            data_worker_resource = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.WORKER_RESOURCE.value ]
            ax2.title.set_text(f"Worker/Resource {data_worker_resource.sum()}")
            sns.heatmap( data_worker_resource, center=0, vmin=-100, vmax=100, ax=ax2, cbar=False )
            
            data_cart_resource = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CART_RESOURCE.value ]
            ax3.title.set_text(f"Cart/Resource {data_cart_resource.sum()}")
            sns.heatmap( data_cart_resource, center=0, vmin=-100, vmax=100, ax=ax3, cbar=False )
            
            data_raw_wood = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_WOOD.value ]
            data_raw_coal = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_COAL.value ]
            data_raw_uranium = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_URANIUM.value ]
            ax4.title.set_text(f"Raw Wood {data_raw_wood.sum()}")
            ax5.title.set_text(f"Raw Coal {data_raw_coal.sum()}")
            ax6.title.set_text(f"Raw Uranium {data_raw_uranium.sum()}")
            sns.heatmap( data_raw_wood, center=0, vmin=-100, vmax=100, ax=ax4, cbar=False )
            sns.heatmap( data_raw_coal, center=0, vmin=-100, vmax=100, ax=ax5, cbar=False )
            sns.heatmap( data_raw_uranium, center=0, vmin=-100, vmax=100, ax=ax6, cbar=False )
            
            #logging.info(f"ROADS: {Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value} | shape: {ic_perception.mats.shape}")
            data_road = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value ]
            ax31.title.set_text(f"Roads {data_road.sum()}")
            sns.heatmap( data_road, center=0, vmin=0, vmax=6, ax=ax31, cbar=False )

            data_cooldown = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.COOLDOWN.value ]
            ax32.title.set_text(f"Cooldown {data_cooldown.sum()}")
            n_cooldown_limit = GAME_CONSTANTS["PERCEPTION"]["INPUT_COOLDOWN_OFFSET"] +GAME_CONSTANTS["PARAMETERS"]["CITY_ACTION_COOLDOWN"]
            sns.heatmap( data_cooldown, center=0, vmin=-n_cooldown_limit, vmax=n_cooldown_limit, ax=ax32, cbar=False )

            return [ data_citytile_fuel.sum(), data_worker_resource.sum() ]

        draw_heatmap( self.lc_perception[0] )

        def init():
            
            draw_heatmap( self.lc_perception[0] )

        def animate(i):
            fig.suptitle(f"TURN: {i}", fontsize=16)
            l_sum = draw_heatmap( self.lc_perception[i] )
            logging.info(f"generating heatmap{i} ... {l_sum}")

        if (in_max_frames < 0):
            n_frames = len(self.lc_perception)
        elif in_max_frames >= len(self.lc_perception):
            n_frames = len(self.lc_perception)
        else:
            n_frames = in_max_frames

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=n_frames, repeat=False, save_count=n_frames)
        anim.save( is_filename, writer='pillow', fps=in_framerate )
        logging.debug(f"saving heatmaps as: {is_filename} | total frames: {n_frames}")

        return

    def perceptions_actions_to_gif( self, is_filename : str, in_framerate : int, in_max_frames = -1 ):
        """Turn a list of perceptions into a Gif
        because of compression, there are going to be fewer frames, but the delay in them ensures the movie represent the correct output
        Args:
            ilc_list_perception (list): list of Perception classes
            is_filename (str): name of the output gif. must be a .gif
            in_framerate (int): Framerate in FPS
            in_max_frames(int): -1=gify ALL the frames | >0 gify only up to a given number of frames
        """
        logging.debug(f"saving heatmaps...")
        dimension = (32, 32)
        fig, axes = plt.subplots( nrows=3, ncols=4, figsize=(4*4, 3*4) )
        ((ax11, ax12, ax13, ax14), (ax21, ax22, ax23, ax24), (ax31, ax32, ax33, ax34)) = axes
        
        def draw_heatmap( ic_perception: Perception, ic_actions_p0 : Action, ic_actions_p1 : Action ):
            #TODO only first time draw the colorbar

            #plt.clf()
            
            #CityTile/Fuel Mat
            data_citytile_fuel = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CITYTILE_FUEL.value ]
            ax11.title.set_text(f"Citytile/Fuel {data_citytile_fuel.sum()}")
            #sns.heatmap( data_citytile_fuel, center=0, vmin=-100, vmax=100, ax=ax11, cbar=False, cmap="coolwarm" )
            sns.heatmap( data_citytile_fuel, center=0, vmin=-100, vmax=100, ax=ax11, cbar=False )

            data_worker_resource = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.WORKER_RESOURCE.value ]
            ax12.title.set_text(f"Worker/Resource {data_worker_resource.sum()}")
            sns.heatmap( data_worker_resource, center=0, vmin=-100, vmax=100, ax=ax12, cbar=False )
            
            data_cart_resource = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.CART_RESOURCE.value ]
            ax13.title.set_text(f"Cart/Resource {data_cart_resource.sum()}")
            sns.heatmap( data_cart_resource, center=0, vmin=-100, vmax=100, ax=ax13, cbar=False )
            
            data_raw_wood = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_WOOD.value ]
            data_raw_coal = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_COAL.value ]
            data_raw_uranium = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.RAW_URANIUM.value ]
            ax21.title.set_text(f"Raw Wood {data_raw_wood.sum()}")
            ax22.title.set_text(f"Raw Coal {data_raw_coal.sum()}")
            ax23.title.set_text(f"Raw Uranium {data_raw_uranium.sum()}")
            sns.heatmap( data_raw_wood, center=0, vmin=-100, vmax=100, ax=ax21, cbar=False )
            sns.heatmap( data_raw_coal, center=0, vmin=-100, vmax=100, ax=ax22, cbar=False )
            sns.heatmap( data_raw_uranium, center=0, vmin=-100, vmax=100, ax=ax23, cbar=False )
            
            #logging.info(f"ROADS: {Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value} | shape: {ic_perception.mats.shape}")
            data_road = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.ROAD.value ]
            ax14.title.set_text(f"Roads {data_road.sum()}")
            sns.heatmap( data_road, center=0, vmin=0, vmax=6, ax=ax14, cbar=False )

            data_cooldown = ic_perception.mats[ Perception.E_INPUT_SPACIAL_MATRICIES.COOLDOWN.value ]
            ax24.title.set_text(f"Cooldown {data_cooldown.sum()}")
            n_cooldown_limit = GAME_CONSTANTS["PERCEPTION"]["INPUT_COOLDOWN_OFFSET"] +GAME_CONSTANTS["PARAMETERS"]["CITY_ACTION_COOLDOWN"]
            sns.heatmap( data_cooldown, center=0, vmin=-n_cooldown_limit, vmax=n_cooldown_limit, ax=ax24, cbar=False )

            
            #PLAYER0 ACTIONS
            c_actions = ic_actions_p0
            data_citytile = c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_RESEARCH.value] +2*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_BUILD_WORKER.value]  +4*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_BUILD_CITY.value]
            ax31.title.set_text(f"P0 Citytile Actions {data_citytile.sum()}")
            sns.heatmap( data_citytile, vmin=0, vmax=7, ax=ax31, cbar=False )

            data_unit = c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_NORTH.value] +2*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_EAST.value] +4*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_SOUTH.value] +8*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_WEST.value]
            ax32.title.set_text(f"P0 Unit Actions {data_unit.sum()}")
            sns.heatmap( data_unit, vmin=0, vmax=15, ax=ax32, cbar=False )

            #PLAYER1 ACTIONS
            c_actions = ic_actions_p1
            data_citytile = c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_RESEARCH.value] +2*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.CITYTILE_BUILD_WORKER.value]  +4*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_BUILD_CITY.value]
            ax33.title.set_text(f"P1 Citytile Actions {data_citytile.sum()}")
            sns.heatmap( data_citytile, vmin=0, vmax=7, ax=ax33, cbar=False )

            data_unit = c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_NORTH.value] +2*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_EAST.value] +4*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_SOUTH.value] +8*c_actions.mats[ Action.E_OUTPUT_SPACIAL_MATRICIES.UNIT_MOVE_WEST.value]
            ax34.title.set_text(f"P1 Unit Actions {data_unit.sum()}")
            sns.heatmap( data_unit, vmin=0, vmax=15, ax=ax34, cbar=False )


            return [ data_citytile_fuel.sum(), data_worker_resource.sum() ]

        draw_heatmap( self.lc_perception[0], self.lc_actions_player0[0], self.lc_actions_player1[0] )

        def init():
            
            draw_heatmap( self.lc_perception[0], self.lc_actions_player0[0], self.lc_actions_player1[0] )

        def animate(i):
            fig.suptitle(f"TURN: {i}", fontsize=16)
            l_sum = draw_heatmap( self.lc_perception[i], self.lc_actions_player0[i], self.lc_actions_player1[i] )
            logging.info(f"generating heatmap{i} ... {l_sum}")

        if (in_max_frames < 0):
            n_frames = len(self.lc_perception)
        elif in_max_frames >= len(self.lc_perception):
            n_frames = len(self.lc_perception)
        else:
            n_frames = in_max_frames

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=n_frames, repeat=False, save_count=n_frames)
        anim.save( is_filename, writer='pillow', fps=in_framerate )
        logging.debug(f"saving heatmaps as: {is_filename} | total frames: {n_frames}")

        return
