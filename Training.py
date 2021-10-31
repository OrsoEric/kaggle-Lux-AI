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
from big_no_brainer import model_tf

if __name__ == "__main__":
    in_mat, in_stat, out_1, ds_batches = Pipeline.pipeline()
    model = model_tf.bnb_model_tf()
    model.compile(loss=losses.MeanSquaredError(), optimizer=optimizers.Adam())

    model.fit(x=(in_mat, in_stat), y=out_1, batch_size=72, epochs=5)
    model.save("test")

