#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

from tensorflow import float32
from tensorflow.keras import Input
from tensorflow.keras import Model
from tensorflow.keras import Sequential
from tensorflow.keras import layers
from tensorflow import losses
from tensorflow import optimizers

from big_no_brainer.perception import Perception
from big_no_brainer.action import Action

#--------------------------------------------------------------------------------------------------------------------------------
#   MODEL
#--------------------------------------------------------------------------------------------------------------------------------
# Game() -> Perception() [status(9) mats(10 32 32)] -> model -> Action() [mats(15 32 32)]

def bnb_model_tf(c_in : Perception, c_out : Action):
    #allocate dictionary of inputs

    c_model = Model( c_in.mats, Sequential( [ Input( shape=(10,32,32), name="mats", dtype=float32 ), layers.Dense(64), layers.Dense(1) ] )  )
    c_model.compile( loss=losses.MeanSquaredError(), optimizer=optimizers.Adam() )

    return c_model
