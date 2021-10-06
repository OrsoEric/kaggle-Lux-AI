class Constants:
    """enumerate game constants for parsing
    """
    #stdint constants
    class INPUT_CONSTANTS:
        """stdout agent command headers and stdin observation keywords"""
        RESEARCH_POINTS = "rp"
        RESOURCES = "r"
        UNITS = "u"
        CITY = "c"
        CITY_TILES = "ct"
        ROADS = "ccd"
        #this stdin string signals that the game is done sending environment information
        DONE = "D_DONE"
        #observation class default Dict() keywords
        UPDATES = "updates"
        STEP = "step"
        
    class DIRECTIONS:
        """stdout agent directions"""
        NORTH = "n"
        WEST = "w"
        SOUTH = "s"
        EAST = "e"
        CENTER = "c"

    class UNIT_TYPES:
        """index of unit types"""
        WORKER = 0
        CART = 1

    class RESOURCE_TYPES:
        """type of resource"""
        WOOD = "wood"
        URANIUM = "uranium"
        COAL = "coal"

import json
from os import path
dir_path = path.dirname(__file__)
constants_path = path.abspath(path.join(dir_path, "game_constants.json"))
with open(constants_path) as f:
    GAME_CONSTANTS = json.load(f)