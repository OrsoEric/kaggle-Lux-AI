## @package rule
#	encapsulates the rules and methods to compute actions

## @TODO
#	worker with full inventory should move to nearest EMPTY and put down a city
#	search_nearest( EMPTY )
#	worker.can_build_city

import math
import logging
from enum import Enum, auto
from pprint import pprint

#efficient nested loops
from itertools import product

from lux.constants import Constants
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from lux.game_map import GameMap, Position
from lux.game_map import Cell
from lux.game_objects import City, Player
from lux.game_objects import Unit


class Rule:
	#enumerate possible types of cell
	class E_CELL_TYPE( Enum ):
		ANY = auto(),
		EMPTY = auto(),
		CITYTILE = auto(),
		CITYTILE_PLAYER = auto(),
		CITYTILE_OPPONENT = auto(),
		RESOURCE = auto(),
		WOOD = auto(),
		COAL = auto(),
		URANIUM = auto()

	def __init__(self, ic_map : GameMap, ic_player : Player, ic_opponent : Player ):
		"""Initialize Rule processor by feeding it the game observations
		Args:
			ic_map (GameMap): Map
			ic_player (Player): Player the agent is playing as
			ic_opponent (Player): Player the agent is playing against
		"""
		#observations
		self.c_map = ic_map
		self.c_player = ic_player
		self.c_opponent = ic_opponent
		#actions
		self.ls_actions = list()

	def __is_cell_type( self, ic_cell : Cell, ie_type : E_CELL_TYPE ) -> bool:
		"""returns True if a given cell is of a given type
		Args:
			ic_cell (Cell): cell under test
			ie_type (E_CELL_TYPE): cell type enum Rule.E_CELL_TYPE
		Returns:
			bool: False: error or cell doesn't match E_CELL_TYPE | True: cell matches E_CELL_TYPE
		"""
		x_resource = False
		x_resource_wood = False
		x_resource_coal = False
		x_resource_uranium = False
		#cell has resources
		if ic_cell.has_resource() == False:
			pass
		else:
			x_resource = True
			if ( ic_cell.resource.is_type(RESOURCE_TYPES.WOOD) ):
				x_resource_wood = True
			elif ( ic_cell.resource.is_type(RESOURCE_TYPES.COAL) ):
				x_resource_coal = True
			elif ( ic_cell.resource.is_type(RESOURCE_TYPES.URANIUM) ):
				x_resource_uranium = True
			else:
				logging.critical(f"invalid Resource Type {ic_cell.resource}")
				return False

		#cell has a city. differentiate ownership
		x_citytile = False
		x_citytile_player = False
		x_citytile_opponent = False
		if (ic_cell.citytile == None):
			pass
		else:
			x_citytile = True
			if ic_cell.citytile.team == self.c_player.team:
				x_citytile_player = True
			elif ic_cell.citytile.team == self.c_opponent.team:
				x_citytile_opponent = True
			else:
				logging.critical(f"invalid CityTile team {ic_cell.citytile.team} {self.c_player.team} {self.c_opponent.team}")
				return False

		#any cell will match ANY
		if ie_type == Rule.E_CELL_TYPE.ANY:
			return True
		elif ie_type == Rule.E_CELL_TYPE.CITYTILE:
			return x_citytile
		elif ie_type == Rule.E_CELL_TYPE.CITYTILE_PLAYER:
			return x_citytile_player
		elif ie_type == Rule.E_CELL_TYPE.CITYTILE_OPPONENT:
			return x_citytile_opponent
		elif ie_type == Rule.E_CELL_TYPE.RESOURCE:
			return x_resource
		elif ie_type == Rule.E_CELL_TYPE.WOOD:
			return x_resource_wood
		elif ie_type == Rule.E_CELL_TYPE.COAL:
			return x_resource_coal
		elif ie_type == Rule.E_CELL_TYPE.URANIUM:
			return x_resource_uranium

		#an empty cell has no units, city tiles or resources
		elif ie_type == Rule.E_CELL_TYPE.EMPTY:
			#@TODO empty condition is more complex as it involves units
			return not any([ x_citytile, x_resource ])
		#default case
		else:
			logging.critical(f"TODO: Implement search type: {ie_type}")
			return False

		return False

	def __search_nearest( self, ic_map : GameMap, ie_target: E_CELL_TYPE , ic_position : Position ) -> Cell:
		"""search the map for a cell of given characteristics nearest to a given position, if any are found
		Args:
		ic_map (GameMap): map where the search is conducted
		is_target (str): content to search for. contained in the enum E_TARGETS
		ic_position (Position): pivot position where search is conducted
		Returns:
		Cell: None=cell wasn't found | cell that satisfies the given conditions
		"""

		#initialize search
		nearest_dist = math.inf
		nearest_cell = None
		#scan every 2D coordinate on the map
		for w, h in product( range( ic_map.width ), range( ic_map.height ) ):
			#compute the content of the cell at the given coordinate
			c_cell = ic_map.get_cell( w, h )
			#if i found a cell of the right characteristics
			if ( self.__is_cell_type( c_cell, ie_target ) ):
				#if the cell is the nearest yet
				n_distance = c_cell.pos.distance_to( ic_position )
				if (n_distance < nearest_dist):
					#i found a closer cell of the right type
					nearest_dist = n_distance
					nearest_cell = c_cell
		#return the nearest cell, if any
		return nearest_cell


	def __compute_worker_actions(self, ic_player : Player, ic_worker : Unit ) -> list:
		"""compute the actions a single worker will take
		Args:
			self (Rule): self
			ic_player (Player): player that owns the worker
			ic_worker (Unit): worker for which actions are to be computed
		Returns:
			list[str]: list of actions
		"""
		#initialize worker actions 
		ls_worker_actions = list()
		#Worker is out of cooldown
		if ic_worker.can_act():
			#worker can collect more resources
			if ic_worker.get_cargo_space_left() > 0:
				nearest_resource_cell = None
				#search the closest researched resource tile for collection
				if ( ic_player.researched(RESOURCE_TYPES.URANIUM) ):
					nearest_resource_cell = self.__search_nearest( self.c_map, Rule.E_CELL_TYPE.URANIUM, ic_worker.pos )
				elif ( ic_player.researched(RESOURCE_TYPES.COAL) ):
					nearest_resource_cell = self.__search_nearest( self.c_map, Rule.E_CELL_TYPE.COAL, ic_worker.pos )
				elif ( ic_player.researched(RESOURCE_TYPES.WOOD) ):
					nearest_resource_cell = self.__search_nearest( self.c_map, Rule.E_CELL_TYPE.WOOD, ic_worker.pos )
				else:
					logging.critical(f"No resource is researched. Collection impossible.")
				#if a resource cell has been found
				if nearest_resource_cell is not None:
					#move toward resource
					logging.debug(f"Action Worker->Resource | Worker: {ic_worker} | Resource: {nearest_resource_cell}")
					ls_worker_actions.append( ic_worker.move( ic_worker.pos.direction_to( nearest_resource_cell.pos ) ) )

			#worker cargo is full
			else:
				#search the nearest allied citytile to the worker
				nearest_citytile_player = self.__search_nearest( self.c_map, Rule.E_CELL_TYPE.CITYTILE_PLAYER, ic_worker.pos )
				#search the nearest empty tile where a city can be built
				nearest_empty = self.__search_nearest( self.c_map, Rule.E_CELL_TYPE.EMPTY, ic_worker.pos )
				#an empty tile exist
				if nearest_empty != None:
					#if worker is already on an empty tile
					if nearest_empty.pos == ic_worker.pos:
						#worker build citytile
						logging.debug(f"Action Worker->Build City | Worker: {ic_worker}")
						ls_worker_actions.append( ic_worker.build_city() )
					else:
						#worker moves to empty tile
						logging.debug(f"Action Worker->Empty | Worker: {ic_worker} | Resource: {nearest_empty}")
						ls_worker_actions.append( ic_worker.move( ic_worker.pos.direction_to( nearest_empty.pos ) ) )

				#if citytile found exist
				elif nearest_citytile_player != None:
					#move toward citytile
					logging.debug(f"Action Worker->City Tile | Worker: {ic_worker} | CityTile {nearest_citytile_player}")
					move_dir = ic_worker.pos.direction_to(nearest_citytile_player.pos)
					ls_worker_actions.append( ic_worker.move( move_dir ) )

				

		#WORKER can't act
		else:
			pass

		return ls_worker_actions
	
	def __compute_city_actions( self, ic_player_city : City ) -> list:
		#initialize list of city actions
		ls_city_actions = list()
		#iterate over all city tiles that make up an individual city
		for my_city_tile in ic_player_city.citytiles:
			#if the city can act
			if my_city_tile.can_act() == True:
				#ACTION: have the city tile research
				logging.debug(f"Action Research: {my_city_tile}")
				ls_city_actions.append( my_city_tile.research() )
		return ls_city_actions

	def compute_actions( self ) -> list():

		#iterate over all units
		for my_unit in self.c_player.units:
			#WORKER RULES
			if my_unit.is_worker():
				#compute and add the actions of this worker to the list of actions
				self.ls_actions += self.__compute_worker_actions( self.c_player, my_unit )

			#Handle carts
			elif my_unit.is_cart():
				pass

			#Default Case:
			else:
				#ERROR!!! Unknown unit
				logging.critical(f"Unit type is unknown: {my_unit}")

		#iterate over all cities owned by the player
		for s_city, c_city in self.c_player.cities.items():
			#compute and add the actions of this worker to the list of actions
			self.ls_actions += self.__compute_city_actions( c_city )

		return self.ls_actions



