import logging
import os
import numpy as np
import tensorflow as tf

#  Replay class takes care of loading and conversions from a replay.json created by lux-ai to Perception and Action classes
from big_no_brainer.perception import Perception
from big_no_brainer.action import Action
from big_no_brainer.replay import Replay

REPLAY_FOLDER = "replays"
REPLAY_FILE = "27879876.json"


# --------------------------------------------------------------------------------------------------------------------------------
#   Helper functions
# --------------------------------------------------------------------------------------------------------------------------------

def get_replays(is_folder: str) -> list:
    """ Search in a folder for replays and return a list of all replay files with .json extension
    Args:
        is_folder (str): folder with replays
    Returns:
        list: list of replay.json files
    """
    # folder with replays
    s_filepath = os.path.join(os.getcwd(), REPLAY_FOLDER)
    ls_files = os.listdir(s_filepath)
    # search for all filenames in the list for files with a .json extension
    ls_replays = [s_file for s_file in ls_files if s_file.find(".json") > -1]
    logging.debug(f"Replays found: {len(ls_replays)} | {ls_replays}")

    return ls_replays


# --------------------------------------------------------------------------------------------------------------------------------
#   BNB Big No Brainer imitation net
# --------------------------------------------------------------------------------------------------------------------------------
#   Replay.json are concatenated and fed to the training of the BNB net


###
### MISS THE DYNAMIC CHOICE FOR THE WINNER!!!!! i.e. It always get the output from player 1
###

def pipeline():
    #
    #   parse the json replays with the json_to_perception_action() method
    #
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(module)s:%(lineno)d %(levelname)s> %(message)s')
    # get a list of replay.json in the folder
    ls_replays_filename = get_replays(REPLAY_FOLDER)
    # allocate training set
    lc_train_perception = list()
    lc_train_action = list()
    # scan all replays
    for s_replay_filename in ls_replays_filename:
        # Construct Replay
        c_json_replay = Replay()
        # load the json file containing the replay
        c_json_replay.json_load(REPLAY_FOLDER, REPLAY_FILE)
        # From a replay.json extract a list of Perception and one list of Action per player. lists have one entry per
        # step (turn) in the game
        lc_perceptions, lc_action_p0, lc_action_p1 = c_json_replay.json_to_perception_action()
        # DUMB!!! COncantenate all Perception/Action from P0
        lc_train_perception += lc_perceptions
        lc_train_action += lc_action_p0
    #
    # Put the input and output in big and fat numpy arrays then in tf.data.Dataset
    #
    # Initializing numpy.array with zero
    in_mat = np.zeros(shape=(
        len(lc_train_perception), lc_train_perception[1].mats.shape[0], lc_train_perception[1].mats.shape[1],
        lc_train_perception[1].mats.shape[2]))
    in_stat = np.zeros(shape=(len(lc_train_perception), lc_train_perception[1].status.shape[0]))
    out_1 = np.zeros(shape=(len(lc_train_action), lc_train_action[1].mats.shape[0], lc_train_action[1].mats.shape[1],
                            lc_train_action[1].mats.shape[2]))

    # Fill the arrays
    for i in range(len(lc_train_perception)):
        in_mat[i] = np.array(lc_train_perception[i].mats)
        in_stat[i] = np.array(lc_train_perception[i].status)
        out_1[i] = np.array(lc_train_action[i].mats)

    ds = tf.data.Dataset.from_tensor_slices({"in_mat": in_mat, "in_status": in_stat, "out": out_1})
    ds.element_spec  # print info on 1 element in dataset
    tf.data.experimental.cardinality(ds).numpy()  # print number of element in ds a.k.a. game turns

    n_shuffle = 10  # This is arbitrary
    n_batch = len(ls_replays_filename) * 36  # This assure that we have always 10 turns in a batch

    ds_batches = ds.shuffle(n_shuffle).padded_batch(n_batch)
    tf.data.experimental.cardinality(ds_batches).numpy()  # print number of turns in a batch

    return in_mat, in_stat, out_1, ds_batches
