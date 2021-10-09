import math
from typing import List
#import game constant and make them available to the program
from lux.constants import Constants
DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

class Position:
    """Position on the map. tuple (x,y) width height"""
    def __init__(self, x, y):
        self.x = x
        """coordinate"""
        self.y = y
        """coordinate"""

    def __sub__(self, pos ) -> int:
        """overloads LHS-RHS to return the manhattan distance between two Positions"""
        return abs(pos.x - self.x) + abs(pos.y - self.y)

    def distance_to(self, pos):
        """
        Returns Manhattan (L1/grid) distance to pos
        """
        return self - pos

    def is_adjacent(self, pos):
        """returns True when two positions are adjacent"""
        return (self - pos) <= 1

    def __eq__(self, pos) -> bool:
        return self.x == pos.x and self.y == pos.y

    def equals(self, pos):
        return self == pos

    def translate(self, direction, units) -> 'Position':
        if direction == DIRECTIONS.NORTH:
            return Position(self.x, self.y - units)
        elif direction == DIRECTIONS.EAST:
            return Position(self.x + units, self.y)
        elif direction == DIRECTIONS.SOUTH:
            return Position(self.x, self.y + units)
        elif direction == DIRECTIONS.WEST:
            return Position(self.x - units, self.y)
        elif direction == DIRECTIONS.CENTER:
            return Position(self.x, self.y)

    def direction_to(self, target_pos: 'Position') -> DIRECTIONS:
        """Return closest position to target_pos from this position"""
        check_dirs = [
            DIRECTIONS.NORTH,
            DIRECTIONS.EAST,
            DIRECTIONS.SOUTH,
            DIRECTIONS.WEST,
        ]
        closest_dist = self.distance_to(target_pos)
        closest_dir = DIRECTIONS.CENTER
        for direction in check_dirs:
            newpos = self.translate(direction, 1)
            dist = target_pos.distance_to(newpos)
            if dist < closest_dist:
                closest_dir = direction
                closest_dist = dist
        return closest_dir

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

class Resource:
	"""Enumerates the type and amount of a resource"""

	def __init__(self, r_type: str, amount: int):
		self.type = r_type
		"""type of the resource"""
		self.amount = amount
		"""amount of the resource"""

	def is_type( self, is_type : str ) -> bool:
		return self.type == is_type

	def __str__(self) -> str:
		return f"Resource | {self.type} | {self.amount}"

class Cell:
    """Enumerates the content of a single square in the map"""
    def __init__(self, x, y):
        self.pos = Position(x, y)
        """Coordinates of the square in the map"""
        self.resource: Resource = None
        """Resources on the square, if any"""
        self.citytile = None
        """Citytile on the square, if any"""
        self.road = 0
        """Road level of the tile"""

    def has_resource(self):
        return self.resource is not None and self.resource.amount > 0

    def __str__(self) -> str:
        #print position
        s_tmp = f"Cell {self.pos} |"
        #print resources, if any
        if (self.resource != None):
            s_tmp += f"{self.resource} |"
        #print city if any
        if (self.citytile != None):
            s_tmp += f"{self.citytile} |"
        s_tmp += f"Road: {self.road} |"
        return s_tmp

class GameMap:
    """Map stats. size, and list of cells"""

    def __init__(self, width, height):
        self.height = height
        """Height of the map in squares. Y dimension"""
        self.width = width
        """Width of the map in squares. X dimension"""
        self.map: List[List[Cell]] = [None] * height
        """List of list of cells that make up the map"""
        #Fill the list of cells
        for y in range(0, self.height):
            self.map[y] = [None] * width
            for x in range(0, self.width):
                self.map[y][x] = Cell(x, y)

    def get_cell_by_pos( self, pos : Position ) -> Cell:
        """Return the cell at a given position in the map
        Args:
            pos: tuple with .x and .y coordinate of the cell
        Returns:
            Cell: map square with all its content
        """
        return self.map[pos.y][pos.x]

    def get_cell(self, x, y) -> Cell:
        """Return the cell at a given position in the map
        Args:
            x: coordinate of the cell
            y: coordinate of the cell
        Returns:
            Cell: map square with all its content
        """
        return self.map[y][x]

    def _setResource(self, r_type, x, y, amount):
        """
        do not use this function, this is for internal tracking of state
        """
        cell = self.get_cell(x, y)
        cell.resource = Resource(r_type, amount)


