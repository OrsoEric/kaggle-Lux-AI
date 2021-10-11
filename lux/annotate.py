#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORTS
#--------------------------------------------------------------------------------------------------------------------------------

from lux.game_map import Position

#--------------------------------------------------------------------------------------------------------------------------------
#   CONSTANTS
#--------------------------------------------------------------------------------------------------------------------------------

CONFIGURATION_ANNOTATE_ENABLED = True

#--------------------------------------------------------------------------------------------------------------------------------
#   ACTIONS
#--------------------------------------------------------------------------------------------------------------------------------
#	annotate actions are used to draw shapes on the game map

def circle(in_x: int, in_y: int) -> str:
	"""draw a circle on the game map"""
	if CONFIGURATION_ANNOTATE_ENABLED == False:
		return ""
	return f"dc {in_x} {in_y}"

def circle(ic_pos : Position) -> str:
	"""draw a circle on the game map"""
	if CONFIGURATION_ANNOTATE_ENABLED == False:
		return ""
	return f"dc {ic_pos.x} {ic_pos.y}"

def target(x: int, y: int) -> str:
	"""draw a X on the game map"""
	if CONFIGURATION_ANNOTATE_ENABLED == False:
		return ""
	return f"dx {x} {y}"

def target(ic_pos : Position) -> str:
	"""draw a X on the game map"""
	if CONFIGURATION_ANNOTATE_ENABLED == False:
		return ""
	return f"dx {ic_pos.x} {ic_pos.y}"

def line(x1: int, y1: int, x2: int, y2: int) -> str:
	"""draw a line between two squares"""
	if CONFIGURATION_ANNOTATE_ENABLED == False:
		return ""
	return f"dl {x1} {y1} {x2} {y2}"

def line( ic_pos_start : Position, ic_pos_stop : Position ) -> str:
	"""draw a line between two squares"""
	if CONFIGURATION_ANNOTATE_ENABLED == False:
		return ""
	return f"dl {ic_pos_start.x} {ic_pos_start.y} {ic_pos_stop.x} {ic_pos_stop.y}"

def text(x: int, y: int, message: str, fontsize: int = 16) -> str:
	"""write on cell"""
	return f"dt {x} {y} {fontsize} '{message}'"

def sidetext(message: str) -> str:
	"""write on the side"""
	return f"dst '{message}'"
