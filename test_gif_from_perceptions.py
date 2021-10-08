import logging

from big_no_brainer import Perception
from big_no_brainer import load_perceptions
from big_no_brainer import gify_list_perception

def preception_to_gif( is_filename : str() ):

    filename_pkl = f"{is_filename}.pkl"
    print(f"loading {filename_pkl}")

    lc_perception = load_perceptions( filename_pkl )
    print(f"loaded {len(lc_perception)} perceptions for {filename_pkl}")

    filename_gif = f"{is_filename}.gif"
    gify_list_perception( lc_perception, filename_gif, 10 )

    return

#   if interpreter has the intent of executing this file
if __name__ == "__main__":

	logging.basicConfig(
		#level of debug to show
		level=logging.DEBUG,
		#header of the debug message
		format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s',
	)

preception_to_gif("citytile_agent0")
