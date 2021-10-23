# --------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
# --------------------------------------------------------------------------------------------------------------------------------

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

def bnb_model_tf(c_in: Perception, c_out: Action):
    # allocate dictionary of inputs
    d_input = {}
    d_input["status"] = Input(shape=c_in.status.shape, name="status", dtype=float32)
    d_input["mats"] = Input(shape=c_in.mats.shape, name="mats", dtype=float32)

    #c_out.mats.shape

    n_output_dim = 1
    for n_dim in c_out.mats.shape:
        n_output_dim *= n_dim


    c_body = Sequential()
    c_body.add( Input(shape=c_in.mats.shape, name="mats", dtype=float32) )
    c_body.add( layers.Flatten() ) 
    c_body.add( layers.Dense(64) )
    c_body.add( layers.Dense(n_output_dim) )

    c_body.compile(loss=losses.MeanSquaredError(), optimizer=optimizers.Adam())
    c_body.summary()
    
    return c_body
