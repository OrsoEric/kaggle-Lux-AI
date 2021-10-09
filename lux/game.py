import logging

#import game constant and make them available to the program
from lux.constants import Constants
INPUT_CONSTANTS = Constants.INPUT_CONSTANTS

from lux.game_map import GameMap
from lux.game_objects import Player
from lux.game_objects import Unit
from lux.game_objects import City

class Game:

    #----------------    Overloads    ---------------

    ## Stringfy class for print method
    def __str__(self) -> str:
        return f"Game | Turn: {self.turn} | Map Size: {self.map_width}*{self.map_height} | Unit P0: {len(self.players[0].units)} | Unit P1: {len(self.players[1].units)} |"

    def _initialize(self, messages):
        """
        initialize state
        """
        self.id = int(messages[0])
        self.turn = -1
        """turn index"""
        # get some other necessary initial input
        mapInfo = messages[1].split(" ")
        self.map_width = int(mapInfo[0])
        self.map_height = int(mapInfo[1])
        self.map = GameMap(self.map_width, self.map_height)
        self.players = [Player(0), Player(1)]

    def _end_turn(self):
        print("D_FINISH")

    def _reset_player_states(self):
        self.players[0].units = []
        self.players[0].cities = {}
        self.players[0].city_tile_count = 0
        self.players[1].units = []
        self.players[1].cities = {}
        self.players[1].city_tile_count = 0

    def _update(self, messages: str() ):
        """process observations into a game state
        Args:
            messages ([type]): [description]
        """
        self.map = GameMap(self.map_width, self.map_height)
        self.turn += 1
        self._reset_player_states()

        for update in messages:
            if update == INPUT_CONSTANTS.DONE:
                break
            strs = update.split(" ")
            input_identifier = strs[0]
            if input_identifier == INPUT_CONSTANTS.RESEARCH_POINTS:
                team = int(strs[1])
                self.players[team].research_points = int(strs[2])
            elif input_identifier == INPUT_CONSTANTS.RESOURCES:
                r_type = strs[1]
                x = int(strs[2])
                y = int(strs[3])
                amt = int(float(strs[4]))
                self.map._setResource(r_type, x, y, amt)
            elif input_identifier == INPUT_CONSTANTS.UNITS:
                #Add unit to game state
                unittype = int(strs[1])
                team = int(strs[2])
                unitid = strs[3]
                x = int(strs[4])
                y = int(strs[5])
                cooldown = float(strs[6])
                wood = int(strs[7])
                coal = int(strs[8])
                uranium = int(strs[9])
                #
                self.players[team].units.append(Unit(team, unittype, unitid, x, y, cooldown, wood, coal, uranium))

            elif input_identifier == INPUT_CONSTANTS.CITY:
                team = int(strs[1])
                cityid = strs[2]
                fuel = float(strs[3])
                lightupkeep = float(strs[4])
                self.players[team].cities[cityid] = City(team, cityid, fuel, lightupkeep)
            elif input_identifier == INPUT_CONSTANTS.CITY_TILES:
                team = int(strs[1])
                cityid = strs[2]
                x = int(strs[3])
                y = int(strs[4])
                cooldown = float(strs[5])
                city = self.players[team].cities[cityid]
                citytile = city._add_city_tile(x, y, cooldown)
                self.map.get_cell(x, y).citytile = citytile
                self.players[team].city_tile_count += 1;
            elif input_identifier == INPUT_CONSTANTS.ROADS:
                x = int(strs[1])
                y = int(strs[2])
                road = float(strs[3])
                self.map.get_cell(x, y).road = road

    def _set_player_id( self, in_player_id : int ) -> bool:
        """Tells the game state whichplayer is being controlled by the agent
        Args:
            in_player_id (number): ID of the palyer the agent is controlling
        Returns:
            bool: False: success | True: fails because ID is out of range
        """
        if ((in_player_id < 0) or (in_player_id > 1)):
            logging.critical(f"Invalid player ID: {in_player_id}")
            return True

        self.id = in_player_id
        """ID of the player the agent is controlling"""
        self.opponent_id = (in_player_id+1)%2
        """ID of the player the opponent is controlling"""

        return False