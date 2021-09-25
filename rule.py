## @package rule
#	encapsulates the rules and methods to compute actions

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
from lux.game_objects import Player
from lux.game_objects import Unit


class Rule:
	#enumerate possible types of cell
	class E_CELL_TARGET( Enum ):
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
		#processed observations
		self.__lc_resource_cells = self.__search_resource_cells( self.c_map )
		self.__lc_buildable_cells = list()

	def __search_resource_cells(self, ic_map : GameMap ) -> list[Cell]:
		"""
		Args: search the map for cells with resources on them. Returns them as a list.
			self(Rule): self
			c_map(GameMap): map where the search is executed
		Returns:
			list(Cell): list of Cell with resources on them
		"""
		#initialize a list of squares with resources to empty
		lc_cells_with_resources: list[Cell] = list()
		#scan every 2D coordinate on the map
		for w, h in product( range( ic_map.width ), range( ic_map.height ) ):
			#compute the content of the cell at the given coordinate
			c_cell = ic_map.get_cell( w, h )
			#if the square has resources on it
			if c_cell.has_resource():
				#add the square to the list of squares with resouces
				lc_cells_with_resources.append( c_cell )
		#return list of Cell with resources on them
		return lc_cells_with_resources


	def __is_cell_type( self, ic_cell : Cell, ie_type : E_CELL_TARGET ) -> bool:

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
		if ie_type == Rule.E_CELL_TARGET.ANY:
			return True
		elif ie_type == Rule.E_CELL_TARGET.CITYTILE:
			return x_citytile
		elif ie_type == Rule.E_CELL_TARGET.CITYTILE_PLAYER:
			return x_citytile_player
		elif ie_type == Rule.E_CELL_TARGET.CITYTILE_OPPONENT:
			return x_citytile_opponent
		elif ie_type == Rule.E_CELL_TARGET.RESOURCE:
			return x_resource
		elif ie_type == Rule.E_CELL_TARGET.WOOD:
			return x_resource_wood
		elif ie_type == Rule.E_CELL_TARGET.COAL:
			return x_resource_coal
		elif ie_type == Rule.E_CELL_TARGET.URANIUM:
			return x_resource_uranium

		#an empty cell has no units, city tiles or resources
		#elif ie_type == Rule.E_CELL_TARGET.EMPTY:
			#return False
		#default case
		else:
			logging.critical(f"TODO: Implement search type: {ie_type}")
			return False

		return False

	def search_nearest( self, ic_map : GameMap, ie_target: E_CELL_TARGET , ic_position : Position ) -> Cell:
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


	def __compute_worker_actions(self, ic_player : Player, ic_worker : Unit ) -> list[str]:
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
					nearest_resource_cell = self.search_nearest( self.c_map, Rule.E_CELL_TARGET.URANIUM, ic_worker.pos )
				elif ( ic_player.researched(RESOURCE_TYPES.COAL) ):
					nearest_resource_cell = self.search_nearest( self.c_map, Rule.E_CELL_TARGET.COAL, ic_worker.pos )
				elif ( ic_player.researched(RESOURCE_TYPES.WOOD) ):
					nearest_resource_cell = self.search_nearest( self.c_map, Rule.E_CELL_TARGET.WOOD, ic_worker.pos )
				else:
					logging.critical(f"No resource is researched. Collection impossible.")
				#if a resource cell has been found
				if nearest_resource_cell is not None:
					#move toward resource
					logging.debug(f"Worker->Resource | Worker: {ic_worker} | Resource: {nearest_resource_cell}")
					ls_worker_actions.append( ic_worker.move( ic_worker.pos.direction_to( nearest_resource_cell.pos ) ) )


				"""
				closest_dist = math.inf
				closest_resource_tile = None
				# if the unit is a worker and we have space in cargo, lets find the nearest resource tile and try to mine it
				for resource_tile in self.__lc_resource_cells:
					if resource_tile.resource.type == RESOURCE_TYPES.WOOD:
						if not ic_player.researched(resource_tile.resource.type):
							continue
						else:
							dist = resource_tile.pos.distance_to(ic_worker.pos)
							if dist < closest_dist:
								closest_dist = dist
								closest_resource_tile = resource_tile
					elif resource_tile.resource.type == RESOURCE_TYPES.COAL:
						continue
					elif resource_tile.resource.type == RESOURCE_TYPES.URANIUM:
						continue
					#resource type is invalid. algorithmic error!
					else:
						logging.critical(f"Unknown resource {resource_tile}")
					
				if closest_resource_tile is not None:
					logging.debug(f"Worker->Resource | Worker: {ic_worker} | Resource: {closest_resource_tile}")
					ls_worker_actions.append( ic_worker.move( ic_worker.pos.direction_to( closest_resource_tile.pos ) ) )
				"""
			#worker cargo is full
			else:
				#worker satisfies the conditions to build a CityTile
				if False: #ic_worker.can_build( game_state.map ):
					logging.debug(f"Worker->Build City | Worker: {ic_worker}")
					ls_worker_actions.append( ic_worker.build_city() )

				#player has cities left
				elif len(ic_player.cities) > 0:
					#search for the closest city
					closest_dist = math.inf
					closest_city_tile = None
					for k, city in ic_player.cities.items():
						for city_tile in city.citytiles:
							dist = city_tile.pos.distance_to(ic_worker.pos)
							if dist < closest_dist:
								closest_dist = dist
								closest_city_tile = city_tile
					if closest_city_tile is not None:
						logging.debug(f"Worker->City Tile | Worker: {ic_worker} | CityTile {closest_city_tile}")
						move_dir = ic_worker.pos.direction_to(closest_city_tile.pos)
						ls_worker_actions.append(ic_worker.move(move_dir))

				#worker unable to build and player has no cities left
				else:
					#TODO move the worker where he can put down a new city
					pass

		#WORKER can't act
		else:
			pass

		return ls_worker_actions
	
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



		return self.ls_actions



