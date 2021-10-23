# --------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
# --------------------------------------------------------------------------------------------------------------------------------

import logging

import numpy as np

from tensorflow import float32
from tensorflow.keras import Input
#from tensorflow.keras import Output
from tensorflow.keras import Model
from tensorflow.keras import Sequential
from tensorflow.keras import layers
from tensorflow import losses
from tensorflow import optimizers

from big_no_brainer.perception import Perception
from big_no_brainer.action import Action

# --------------------------------------------------------------------------------------------------------------------------------
#   MODEL
# --------------------------------------------------------------------------------------------------------------------------------

class Bnb_model:

    #----------------    Constructor    ----------------

    def __init__( self ):

        #initialize Model
        self.c_model = None

        return

    #----------------    Public Methods    ----------------

    def build( self, c_in: Perception, c_out: Action ) -> bool:
        """Construct a ML model based on the shape of a single instance of Perception and Action classes
        Args:
            c_in (Perception): Perception class. shape is used to define the input size of the model
            c_out (Action): Action class. shape is used to define the input size of the model
        Returns:
            bool: False=OK | True=FAIL
        """
        # allocate dictionary of inputs
        d_input = {}
        d_input["status"] = Input(shape=c_in.status.shape, name="status", dtype=float32)
        d_input["mats"] = Input(shape=c_in.mats.shape, name="mats", dtype=float32)

        n_output_dim = 1
        for n_dim in c_out.mats.shape:
            n_output_dim *= n_dim

        c_body = Sequential()
        c_body.add( Input(shape=c_in.mats.shape, name="mats", dtype=float32) )
        c_body.add( layers.Flatten() ) 
        c_body.add( layers.Dense( 64 ) )
        c_body.add( layers.Dense( n_output_dim ) )

        c_body.compile(loss=losses.MeanSquaredError(), optimizer=optimizers.Adam())
        c_body.summary()

        #save the model inside the class
        self.c_model = c_body

        return False

    def train( self, lc_step_in : list, lc_step_out : list, n_max_epochs = 10 ) -> bool:
        """Train model based on a input list of Perceptions and an input list of actions.
        each entry in each list is one turn, detailing which move was taken based on game state
        Args:
            lc_features (list): list of Perception, one for each step (turn). Perception.mats shape: feature*size*size
            lc_labels (list): list of Action, one for each step (turn). Action.mats shape: actions*size*size
        Returns:
            bool: False=OK | True=FAIL
        """

        #Convert from a list of Perception to slabs of numbers inside a NP array
        cnp_step_in = self._build_training_input_mats( lc_step_in ) 
        logging.debug(f"NP IN: {cnp_step_in.shape}")
        #Convert from a list of Action to slabs of numbers inside a NP array
        cnp_step_out = self._build_training_output_mats( lc_step_out ) 
        logging.debug(f"NP OUR: {cnp_step_out.shape}")


        #Needs a NP TURNSx8x32x32
        #Needs a NP TURNSx15x32x32
        self.c_model.fit( cnp_step_in, cnp_step_out, epochs=n_max_epochs )
        

        return False


    def save( self, s_path : str ) -> bool:
        """
        Args:
            s_path (str): [description]
        Returns:
            bool: [description]
        """
        if self.c_model is None:
            return True

        self.c_model.save_weights("shaka")

        return False

    def load( self, s_path : str ) -> bool:

        self.c_model.load_weights("shaka")

        return False

    def bnb_model_inference( c_in: Perception, c_out: Action ):
        return


    #----------------    Protected Methods    ----------------

    def _build_training_input_mats( self, lc_source ):
        """From a list of objects with "mats" attribute, generate a numpy array
        e.g. 720x mats(8x32x32) -> 720*8*32*32
        e.g. 720x mats(15*32*32) -> 720*15*32*32
        Args:
            lc_source ([type]): [description]
        Returns:
            list: [description]
        """
        n_turns = len( lc_source )
        t_shape = lc_source[0].mats.shape
        logging.debug(f" Turns: {n_turns} | Shape: {t_shape}")

        r_shape = [n_turns]
        for n_tmp in t_shape:
            r_shape.append(n_tmp)
        logging.debug(f"Resulting Shape: {r_shape}")
        
        #generate a np array from a list
        cnp_result = np.zeros( r_shape )
        for index, entry in enumerate( lc_source ):
            cnp_result[index] = entry.mats

        logging.debug(f"Result IN: {cnp_result.shape}")

        return cnp_result

    def _build_training_output_mats( self, lc_source ):
        """From a list of objects with "mats" attribute, generate a numpy array
        e.g. 720x mats(8x32x32) -> 720*8*32*32
        e.g. 720x mats(15*32*32) -> 720*15*32*32
        Args:
            lc_source ([type]): [description]
        Returns:
            list: [description]
        """
        n_turns = len( lc_source )
        t_shape = lc_source[0].mats.shape
        logging.debug(f" Turns: {n_turns} | Shape: {t_shape}")

        r_shape = [n_turns]
        f_shape = 1
        for n_tmp in t_shape:
            f_shape *= n_tmp
        r_shape.append(f_shape)
        logging.debug(f"Resulting Shape: {r_shape}")
        
        #generate a np array from a list
        cnp_result = np.zeros( r_shape )
        for index, entry in enumerate( lc_source ):
            cnp_reshaped = entry.mats.reshape([-1])
            cnp_result[index] = cnp_reshaped

        logging.debug(f"Result OUT: {cnp_result.shape}")

        return cnp_result
