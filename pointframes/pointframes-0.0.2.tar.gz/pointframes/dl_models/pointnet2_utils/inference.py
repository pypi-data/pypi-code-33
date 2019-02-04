import argparse
import math
import numpy as np
import tensorflow as tf
import importlib
import os
import sys
import time
import string

base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(base_dir)

sys.path.append(base_dir) # model
sys.path.append(root_dir) # provider
sys.path.append(os.path.join(root_dir, 'utils'))

import provider
import tf_util2 as tf_util
import pc_util

import pointframes as pf

os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
tf.logging.set_verbosity(tf.logging.ERROR)

def pointnet2_eval_data(pointnet2, eval_dataframes):
    ''' Function to strip PointCloud object into a
        PointNet2_Predict object. PointNet2.eval_data should be a
        python list containing pandas dataframes. eval_dataframes
        should be a list of dataframes with the same input points
        and the model was training with.
        args:
            pointnet2       : PointNet2 object
            eval_dataframes : pandas dataframes
        returns:
            pointnet2_data : PointNet2_Data object
    '''

    pf.check_attributes(eval_dataframes[0], ['X', 'Y', 'Z'])

    first_instance = True
    classes = []

    data = np.zeros((1, pointnet2.num_points, 3))

    for pointcloud in eval_dataframes:
        tmp_data = pointcloud[['X', 'Y', 'Z']].values

        if first_instance == True:
            data[0] = tmp_data
            first_instance = False
        else:
            tmp_data = np.expand_dims(tmp_data, axis=0)
            data = np.vstack((data, tmp_data))

    eval_data = pf.PointNet2_Predict()
    eval_data.eval_data = data

    return eval_data


def pointnet2_prediction(pointnet2):

    global start
    start = time.time()

    global data
    global batch_size
    global num_point
    global num_classes
    global model_path
    global gpu_index
    global model
    global model_path

    model = importlib.import_module(pointnet2.model)

    batch_size = 1
    data = pointnet2.eval_data.eval_data
    num_classes = pointnet2.num_classes
    gpu_index = pointnet2.gpu
    output_file = pointnet2.output_file
    num_point = pointnet2.num_points
    model_path = pointnet2.trained_model

    inference_array = evaluate()
    return inference_array

def evaluate():
    is_training = False
    with tf.device('/gpu:'+str(gpu_index)):
        pointclouds_pl, labels_pl, smpws_pl = model.placeholder_inputs(batch_size, num_point)
        is_training_pl = tf.placeholder(tf.bool, shape=())
        batch = tf.Variable(0)

        pred, end_points = model.get_model(pointclouds_pl, is_training_pl, num_classes)
        saver = tf.train.Saver()

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    config.allow_soft_placement = True
    config.log_device_placement = False
    sess = tf.Session(config=config)

    saver.restore(sess, model_path)
    print ("[INFO] Model restored successfully.")

    ops = {'pointclouds_pl': pointclouds_pl,
           'is_training_pl': is_training_pl,
           'pred': pred,
           'end_points': end_points}

    print ("[INFO] Running inference on data...")

    inference_array = eval_one_epoch(sess, ops, data)

    print ('[INFO] Inference completed in {:.2f} seconds'.format(time.time()-start))

    return inference_array

def eval_one_epoch(sess, ops, data):
    is_training = False

    file_size = data.shape[0]
    num_batches = file_size // batch_size

    inference_array = []

    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = (batch_idx+1) * batch_size
        cur_batch_size = end_idx - start_idx

        feed_dict = {ops['pointclouds_pl']: data[start_idx:end_idx, :, :],
                     ops['is_training_pl']: is_training}

        pred_val = sess.run([ops['pred']], feed_dict=feed_dict)
        pred_val = np.squeeze(np.array(pred_val))
        pred_array = np.zeros((pred_val.shape[0], 1))
        pred_array[:,0] = np.argmax(pred_val, axis=1)

        for b in range(batch_size):
            pts = data[start_idx+b, :, :]
            for i in range(num_point):
                inference_array.append(np.append(pts[i], pred_array[i][0]))

    return np.array(inference_array)


if __name__ == '__main__':

    evaluate()
