#	Useful:
#		Execute BOT
#	lux-ai-2021 main.py main.py --out=replay.json 
#		See replay in action
#	https://2021vis.lux-ai.org/

#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

from typing import Dict
#import sys
import logging

#import the stdin constants and make them available 
from lux.constants import Constants
INPUT_CONSTANTS = Constants.INPUT_CONSTANTS
#AI agent
from agent import agent
from lux.game import Game

from big_no_brainer import Perception
from big_no_brainer import save_list_perception

#--------------------------------------------------------------------------------------------------------------------------------
#   MAIN
#--------------------------------------------------------------------------------------------------------------------------------

#   if interpreter has the intent of executing this file
if __name__ == "__main__":

	logging.basicConfig(
		#level of debug to show
		level=logging.INFO,
		#header of the debug message
		format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s',
	)

	def read_input():
		"""fetch inputs from stdin
		Raises:
			SystemExit: [description]
		Returns:
			[type]: [description]
		"""
		try:
			return input()
		except EOFError as eof:
			raise SystemExit(eof)

	class Observation( Dict[str, any] ):
		"""
		Args:
			Dict ([type]): [description]
		"""
		def __init__(self, player=0) -> None:
			self.player = player
			"""int ID of the player the agent is controlling"""
			# self.updates = []
			# self.step = 0

	#Observations about the map
	observation = Observation()
	observation[INPUT_CONSTANTS.UPDATES] = []
	observation[INPUT_CONSTANTS.STEP] = 0
	
	#parallel states used to print game state as gifs
	gif_game_state = None
	lc_gif_perception = list()

	#while init
	step = 0
	player = 0
	#forever
	while True:
		#logging.info(f"XXX {step} {player}")
		#the game will send environment data via stdin
		inputs = read_input()
		#add game engine input observation to the observations
		observation[INPUT_CONSTANTS.UPDATES].append(inputs)
		#Observations are being collected
		if step == 0:
			#compute the ID of the player this agent is controlling
			player_id = int( observation[INPUT_CONSTANTS.UPDATES][0] )
			observation.player = player_id

		#When observations have been fully collected
		if inputs == INPUT_CONSTANTS.DONE:
			#ask the agent for a list of actions based on observations
			actions, c_perception = agent( observation, None )
			#append perception to list of perceptions
			lc_gif_perception.append(c_perception)
			observation["updates"] = []
			step += 1
			observation["step"] = step
			#inform the game engine that actions are done.
			print(",".join(actions))
			print("D_FINISH")
		
		if (step==360):
			save_list_perception( lc_gif_perception, f"citytile_fuel{gif_game_state.id}.gif")


