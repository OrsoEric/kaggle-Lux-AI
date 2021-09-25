## @package rule
#	encapsulates the rules and methods to compute actions

import math
import logging

#efficient nested loops
from itertools import product

from lux.constants import Constants
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from lux.game_map import GameMap, Position
from lux.game_map import Cell
from lux.game_objects import Player
from lux.game_objects import Unit


class Rule:
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

	#search in a list of cells, the closest one to the given position
	def __search_nearest( self, ic_position : Position, ilc_cells : list[Cell] ) -> Cell:

		pass


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



