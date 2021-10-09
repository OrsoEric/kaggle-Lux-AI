import logging

from typing import Dict

#import game constant and make them available to the program
from lux.constants import Constants
from lux.constants import GAME_CONSTANTS
UNIT_TYPES = Constants.UNIT_TYPES
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from lux.game_map import Position
from lux.game_map import GameMap


class Player:
    """ Encapsulates all player relevant objects, like units, cities and research points.
    """
    def __init__(self, team):
        self.team = team
        """"???"""
        self.research_points = 0
        """total research points. research point milestones are needed to mine higher resources."""
        self.units: list[Unit] = []
        """list of units of the player."""
        self.cities: Dict[str, City] = {}
        """dictionary of cities of the player."""
        self.city_tile_count = 0
        """total city tiles owned by the player. first factor for victory condition."""

    def researched(self, s_type : str() ) -> bool:
        """returns true if the resource is researched. logs an error if the type is not compatible
        Args:
            s_type (str): resource type
        Returns:
            bool: false: resource not researched or unknown | true: resource researched
        """
        #if resource type is unknown
        if all( [s_type != RESOURCE_TYPES.WOOD, s_type != RESOURCE_TYPES.COAL, s_type != RESOURCE_TYPES.URANIUM] ):
            logging.error(f"Unknown resource type: {s_type}")
            return False
        #return true if resource is known. the json constant file needs capital strings
        return self.research_points >= GAME_CONSTANTS["PARAMETERS"]["RESEARCH_REQUIREMENTS"][s_type.upper()]

    def researched_wood(self) -> bool:
        """Returns: true: player has enough research points to collect the resource"""
        return self.research_points >= GAME_CONSTANTS["PARAMETERS"]["RESEARCH_REQUIREMENTS"]["WOOD"]

    def researched_coal(self) -> bool:
        """Returns: true: player has enough research points to collect the resource"""
        return self.research_points >= GAME_CONSTANTS["PARAMETERS"]["RESEARCH_REQUIREMENTS"]["COAL"]

    def researched_uranium(self) -> bool:
        """Returns: true: player has enough research points to collect the resource"""
        return self.research_points >= GAME_CONSTANTS["PARAMETERS"]["RESEARCH_REQUIREMENTS"]["URANIUM"]

    def __str__(self) -> str:
        return f"Player {self.research_points} | #cities {len(self.cities)} | #city tiles {self.city_tile_count} | #units {len(self.units)} | #workers {0} | #carts {0} |"


class City:
    """A city is made of adjacient city tiles"""
    def __init__(self, teamid, cityid, fuel, light_upkeep):
        self.cityid = cityid
        """Adjacent citytile belong to the same city, sharing fuel."""
        self.team = teamid
        """ID of the player the agent is assigned to"""
        self.fuel = fuel
        """Total fuel stored inside the city. All city tiles shares one storage."""
        self.citytiles: list[CityTile] = []
        """List of CityTile that make up the city"""
        self.light_upkeep = light_upkeep
        """TOTAL light upkeep of the city. Increases with #CityTile and decreases with adjacency bonuses"""

    def _add_city_tile(self, x, y, cooldown):
        """add a CityTile to a City. adjacent CityTile make up a city."""
        ct = CityTile(self.team, self.cityid, x, y, cooldown)
        self.citytiles.append(ct)
        return ct

    def get_light_upkeep(self):
        """total light upkeep of the city"""
        return self.light_upkeep

    def __str__(self) -> str:
        return f"City {self.cityid} | fuel {self.fuel}"

class CityTile:
    """Enumerates all attributes and actions of a CityTile"""

    def __init__(self, teamid, cityid, x, y, cooldown):
        self.cityid = cityid
        """???"""
        self.team = teamid
        """???"""
        self.pos = Position(x, y)
        """position on the map"""
        self.cooldown = cooldown
        """#of turns before the city can do an action. Cities have no CD reduction."""

    def can_act(self) -> bool:
        """Whether or not this unit can research or build"""
        return self.cooldown <= 0

    def research(self) -> str:
        """returns command to ask this tile to research this turn"""
        return "r {} {}".format(self.pos.x, self.pos.y)

    def build_worker(self) -> str:
        """returns command to ask this tile to build a worker this turn"""
        return "bw {} {}".format(self.pos.x, self.pos.y)

    def build_cart(self) -> str:
        """returns command to ask this tile to build a cart this turn"""
        return "bc {} {}".format(self.pos.x, self.pos.y)

    def __str__(self) -> str:
        return f"CityTile {self.pos} | Player {self.team} | CD: {self.cooldown}"

class Cargo:
    """Enumerates resources stored"""
    def __init__(self):
        self.wood = 0
        """units of resource"""
        self.coal = 0
        """units of resource"""
        self.uranium = 0
        """units of resource"""

    def __str__(self) -> str:
        return f"Cargo | Wood: {self.wood}, Coal: {self.coal}, Uranium: {self.uranium}"

class Unit:
    """Enumerates attributes and actions of a unit"""
    def __init__(self, teamid, u_type, unitid, x, y, cooldown, wood, coal, uranium):
        
        self.pos = Position(x, y)
        """position on the map"""
        self.team = teamid
        """???"""
        self.id = unitid
        """???"""
        self.type = u_type
        """type of unit. type is enumerated in Constants.UNIT_TYPES"""
        self.cooldown = cooldown
        """#of turns before unit can execute an action. """
        self.cargo = Cargo()
        """cargo. resources stored."""
        self.cargo.wood = wood
        self.cargo.coal = coal
        self.cargo.uranium = uranium

    def is_worker(self) -> bool:
        """Returns true if the unit is a worker"""
        return self.type == UNIT_TYPES.WORKER

    def is_cart(self) -> bool:
        """Returns true if the unit is a cart"""
        return self.type == UNIT_TYPES.CART

    def get_cargo_space_left(self):
        """
        get cargo space left in this unit
        """
        spaceused = self.cargo.wood + self.cargo.coal + self.cargo.uranium
        if self.type == UNIT_TYPES.WORKER:
            return GAME_CONSTANTS["PARAMETERS"]["RESOURCE_CAPACITY"]["WORKER"] - spaceused
        else:
            return GAME_CONSTANTS["PARAMETERS"]["RESOURCE_CAPACITY"]["CART"] - spaceused
    
    def can_build(self, game_map : GameMap ) -> bool:
        
        cell = game_map.get_cell_by_pos(self.pos)
        if not cell.has_resource() and self.can_act() and (self.cargo.wood + self.cargo.coal + self.cargo.uranium) >= GAME_CONSTANTS["PARAMETERS"]["CITY_BUILD_COST"]:
            return True

        return False

    def can_act(self) -> bool:
        """
        whether or not the unit can move or not. This does not check for potential collisions into other units or enemy cities
        """
        return self.cooldown < 1

    def move(self, dir) -> str:
        """
        return the command to move unit in the given direction
        """
        return "m {} {}".format(self.id, dir)

    def transfer(self, dest_id, resourceType, amount) -> str:
        """
        return the command to transfer a resource from a source unit to a destination unit as specified by their ids
        """
        return "t {} {} {} {}".format(self.id, dest_id, resourceType, amount)

    def build_city(self) -> str:
        """
        return the command to build a city right under the worker
        """
        return "bcity {}".format(self.id)

    def pillage(self) -> str:
        """
        return the command to pillage whatever is underneath the worker
        """
        return "p {}".format(self.id)

    def __str__(self) -> str:
        return f"Unit {self.pos} | Type: {self.type} | Cargo: {self.cargo} | CD: {self.cooldown}"