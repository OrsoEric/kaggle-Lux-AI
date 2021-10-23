# --------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
# --------------------------------------------------------------------------------------------------------------------------------

from tensorflow import float32
from tensorflow.keras import Input
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
    d_input["mats"] = Input(shape=(10, 32, 32), name="mats", dtype=float32)

    # body = Sequential( [ d_input, layers.Dense(64), layers.Dense(1) ] )
    body = Sequential()
    body.add(Input(shape=(10, 32, 32), name="mats", dtype=float32))
    body.add(layers.Dense(64))
    body.add(layers.Dense(1))
    # result = body()

    # c_model = Model(c_in.mats, result)

    body.compile(loss=losses.MeanSquaredError(), optimizer=optimizers.Adam())

    return body
