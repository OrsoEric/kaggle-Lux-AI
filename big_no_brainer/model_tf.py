# --------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
# --------------------------------------------------------------------------------------------------------------------------------
import tensorflow as tf
from tensorflow import float32
from tensorflow.keras import Input
from tensorflow.keras import Model
from tensorflow.keras import Sequential
from tensorflow.keras import layers
from tensorflow import losses
from tensorflow import optimizers
import pydot

from big_no_brainer.perception import Perception
from big_no_brainer.action import Action
import Pipeline


# --------------------------------------------------------------------------------------------------------------------------------
#   MODEL
# --------------------------------------------------------------------------------------------------------------------------------

def bnb_model_tf():

    input_mats = Input(shape=(8, 32, 32), name="in_mat", dtype=float32)
    input_mats_flat = layers.Flatten()(input_mats)
    first_dense = layers.Dense(8192, )(input_mats_flat)
    input_status = Input(shape=(9,), name="in_status", dtype=float32)
    # second_dense = layers.Dense(9,)(input_status)  # dunno if necessary
    merge = layers.concatenate([first_dense, input_status], axis=1)
    third_dense = layers.Dense(10240, name="out", dtype=float32)(merge)
    outp = layers.Reshape(target_shape=(10, 32, 32), input_shape=(10240,))(third_dense)

    body = Model(inputs=(input_mats, input_status), outputs=outp)

    body.compile(loss=losses.MeanSquaredError(), optimizer=optimizers.Adam())

    tf.keras.utils.plot_model(model=body, to_file="Model.png", rankdir="LR", dpi=72, show_shapes=True)

    return body
