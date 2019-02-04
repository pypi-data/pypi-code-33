import argparse
import math
import h5py
import numpy as np
import tensorflow as tf
import socket
import os
import sys
import importlib

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)
#sys.path.insert(0, base_dir+'/utils')
import utils.provider
import utils.tf_util
import utils.pc_util

import pointframes as pf

os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
tf.logging.set_verbosity(tf.logging.ERROR)

def log_string(out_str):
    log_fout.write(out_str+'\n')
    log_fout.flush()
    print(out_str)


def get_learning_rate(batch):
    learning_rate = tf.train.exponential_decay(
                        base_learning_rate,  # Base learning rate.
                        batch * batch_size,  # Current index into the dataset.
                        decay_step,          # Decay step.
                        decay_rate,          # Decay rate.
                        staircase=True)
    learning_rate = tf.maximum(learning_rate, 0.00001) # CLIP THE LEARNING RATE!!
    return learning_rate


def get_bn_decay(batch):
    bn_momentum = tf.train.exponential_decay(
                      bn_init_decay,
                      batch*batch_size,
                      bn_decay_decay_step,
                      bn_decay_decay_rate,
                      staircase=True)
    bn_decay = tf.minimum(bn_decay_clip, 1 - bn_momentum)
    return bn_decay


def pointnet_preprocess_data(pointnet, train_dataframes, test_ratio=0.2):
    ''' Function to strip PointCloud object into a
        PointNet_Data object. PointNet.data should be a
        python list containing PointCloud object instances.
        args:
            pointnet : PointNet object
        returns:
            pointnet_data : PointNet_Data object
    '''

    pf.check_attributes(train_dataframes[0], ['X', 'Y', 'Z'])

    first_instance = True
    classes = []

    # Initialise empty train data and label arrays
    train_data = np.zeros((1, pointnet.num_points, train_dataframes[0].drop(['class'], axis=1).values.shape[-1]))
    train_labels = np.zeros((1, pointnet.num_points))

    # Loop through all PointCloud objects and extract points and labels
    for pointcloud in train_dataframes:
        tmp_labels = pointcloud[['class']].values
        tmp_data = pointcloud.drop(['class'], axis=1)

        if first_instance == True:
            train_data[0] = tmp_data
            train_labels[0] = tmp_labels.flatten()
            classes.append(np.unique(tmp_labels))
            first_instance = False
        else:
            tmp_data = np.expand_dims(tmp_data, axis=0)
            tmp_labels = tmp_labels.flatten()
            train_data = np.vstack((train_data, tmp_data))
            train_labels = np.vstack((train_labels, tmp_labels))
            classes.append(np.unique(tmp_labels))

    # I assume there is a more Pythonic way for doing this?
    # Extract all unique values from list of numpy arrays
    unique_list = []
    for arr in np.array(classes):
        [unique_list.append(val) for val in arr]

    unique_list = np.unique(unique_list)
    for i, arr in enumerate(train_labels):
        for j, val in enumerate(arr):
            train_labels[i][j] = np.where([val==unique_list])[1][0]

    # Initialise and populate a PointNet_Data object instance
    training_data = pf.PointNet_Data()
    training_data.test_data = train_data[-int(np.around(len(train_data)*test_ratio)):]
    training_data.test_labels = train_labels[-int(np.around(len(train_labels)*test_ratio)):]
    training_data.train_data = train_data[0:-int(np.around(len(train_data)*test_ratio))]
    training_data.train_labels = train_labels[0:-int(np.around(len(train_labels)*test_ratio))]
    training_data.num_classes = len(np.unique(unique_list))

    return training_data


def train_pointnet(pointnet):

    global batch_size
    global num_point
    global max_epoch
    global num_classes
    global base_learning_rate
    global gpu_index
    global momentum
    global optimizer
    global decay_step
    global decay_rate
    global epoch_cnt
    global bn_init_decay
    global bn_decay_decay_rate
    global bn_decay_decay_step
    global bn_decay_clip
    global log_fout

    batch_size = pointnet.batch_size
    num_point = pointnet.num_points
    max_epoch = pointnet.max_epoch
    base_learning_rate = pointnet.learning_rate
    gpu_index = pointnet.gpu
    momentum = pointnet.momentum
    optimizer = pointnet.optimizer
    decay_step = pointnet.decay_step
    decay_rate = pointnet.decay_rate

    os.environ["cuda_device_order"] = "pci_bus_id"
    os.environ["cuda_visible_devices"] = str(gpu_index)

    model = importlib.import_module(pointnet.model) # import network module
    log_dir = pointnet.log_dir
    if not os.path.exists(log_dir): os.mkdir(log_dir)
    if not os.path.exists(os.path.join(log_dir, "models")): os.mkdir(os.path.join(log_dir, "models"))
    log_fout = open(os.path.join(log_dir, 'log_train.txt'), 'w')

    bn_init_decay = 0.5
    bn_decay_decay_rate = 0.5
    bn_decay_decay_step = float(decay_step)
    bn_decay_clip = 0.99

    hostname = socket.gethostname()

    training_data = pointnet.train_data
    num_classes = pointnet.train_data.num_classes
    num_features = training_data.train_data.shape[-1]

    print ('[info] loaded dataset of size {:} with {:} classes'.format(training_data.train_data.shape, num_classes))

    with tf.Graph().as_default():
        with tf.device('/gpu:'+str(gpu_index)):
            pointclouds_pl, labels_pl = model.placeholder_inputs(batch_size, num_point, num_features)
            is_training_pl = tf.placeholder(tf.bool, shape=())

            # Note the global_step=batch parameter to minimize.
            # That tells the optimizer to helpfully increment the 'batch' parameter for you every time it trains.
            batch = tf.Variable(0)
            bn_decay = get_bn_decay(batch)
            tf.summary.scalar('bn_decay', bn_decay)

            # Get model and loss
            pred = model.get_model(pointclouds_pl, is_training_pl, bn_decay=bn_decay, \
                             num_classes=num_classes, num_features=num_features)
            loss = model.get_loss(pred, labels_pl)
            tf.summary.scalar('loss', loss)

            correct = tf.equal(tf.argmax(pred, 2), tf.to_int64(labels_pl))
            accuracy = tf.reduce_sum(tf.cast(correct, tf.float32)) / float(batch_size*num_point)
            tf.summary.scalar('accuracy', accuracy)

            # Get training operator
            learning_rate = get_learning_rate(batch)
            tf.summary.scalar('learning_rate', learning_rate)
            if optimizer == 'momentum':
                optimizer = tf.train.MomentumOptimizer(learning_rate, momentum=momentum)
            elif optimizer == 'adam':
                optimizer = tf.train.AdamOptimizer(learning_rate)
            train_op = optimizer.minimize(loss, global_step=batch)

            # Add ops to save and restore all the variables.
            saver = tf.train.Saver()

        # Create a session
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.allow_soft_placement = True
        config.log_device_placement = True
        sess = tf.Session(config=config)

        # Add summary writers
        merged = tf.summary.merge_all()
        train_writer = tf.summary.FileWriter(os.path.join(log_dir, 'train'),
                                  sess.graph)
        test_writer = tf.summary.FileWriter(os.path.join(log_dir, 'test'))

        # Init variables
        init = tf.global_variables_initializer()
        sess.run(init, {is_training_pl:True})

        ops = {'pointclouds_pl': pointclouds_pl,
               'labels_pl': labels_pl,
               'is_training_pl': is_training_pl,
               'pred': pred,
               'loss': loss,
               'train_op': train_op,
               'merged': merged,
               'step': batch}

        best_acc = -1

        for epoch in range(max_epoch):
            log_string('**** epoch %03d ****' % (epoch))
            sys.stdout.flush()

            train_one_epoch(sess, ops, train_writer, training_data)

            if epoch%10==0:
                acc = eval_one_epoch(sess, ops, test_writer, training_data)
                save_path = saver.save(sess, os.path.join(log_dir, "model.ckpt"))
                log_string("Model saved in file: %s" % save_path)
            if acc > best_acc:
                best_acc = acc
                save_path = saver.save(sess, os.path.join(log_dir, "models", "best_model_epoch_%03d.ckpt"%(epoch)))


    log_fout.close()


def train_one_epoch(sess, ops, train_writer, training_data):
    """ ops: dict mapping from string to tf ops """
    is_training = True

    log_string('-----')
    current_data, current_label, _ = provider.shuffle_data(training_data.train_data[:,0:num_point,:], training_data.train_labels)

    file_size = current_data.shape[0]
    num_batches = file_size // batch_size

    total_correct = 0
    total_seen = 0
    loss_sum = 0

    for batch_idx in range(num_batches):
        if batch_idx % 500 == 0:
            print('Current batch/total batch num: {:}/{:}'.format(batch_idx, num_batches))
        start_idx = batch_idx * batch_size
        end_idx = (batch_idx+1) * batch_size

        feed_dict = {ops['pointclouds_pl']: current_data[start_idx:end_idx, :, :],
                     ops['labels_pl']: current_label[start_idx:end_idx],
                     ops['is_training_pl']: is_training,}
        summary, step, _, loss_val, pred_val = sess.run([ops['merged'], ops['step'], ops['train_op'], ops['loss'], ops['pred']],
                                         feed_dict=feed_dict)
        train_writer.add_summary(summary, step)
        pred_val = np.argmax(pred_val, 2)
        correct = np.sum(pred_val == current_label[start_idx:end_idx])
        total_correct += correct
        total_seen += (batch_size*num_point)
        loss_sum += loss_val
        if batch_idx % 10 == 0:
            print ('step: {0}: loss = {1}').format(batch_idx, loss_val)

    log_string('mean loss: %f' % (loss_sum / float(num_batches)))
    log_string('accuracy: %f' % (total_correct / float(total_seen)))


def eval_one_epoch(sess, ops, test_writer, training_data):
    """ ops: dict mapping from string to tf ops """
    is_training = False
    total_correct = 0
    total_seen = 0
    loss_sum = 0
    total_seen_class = [0 for _ in range(num_classes)]
    total_correct_class = [0 for _ in range(num_classes)]

    log_string('----')
    current_data = training_data.test_data[:,0:num_point,:]
    current_label = np.squeeze(training_data.test_labels)

    file_size = current_data.shape[0]
    num_batches = file_size // batch_size

    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = (batch_idx+1) * batch_size

        feed_dict = {ops['pointclouds_pl']: current_data[start_idx:end_idx, :, :],
                     ops['labels_pl']: current_label[start_idx:end_idx],
                     ops['is_training_pl']: is_training}
        summary, step, loss_val, pred_val = sess.run([ops['merged'], ops['step'], ops['loss'], ops['pred']],
                                      feed_dict=feed_dict)
        test_writer.add_summary(summary, step)
        pred_val = np.argmax(pred_val, 2)
        correct = np.sum(pred_val == current_label[start_idx:end_idx])
        total_correct += correct
        total_seen += (batch_size*num_point)
        loss_sum += (loss_val*batch_size)
        for i in range(start_idx, end_idx):
            for j in range(num_point):
                l = int(current_label[i, j])
                total_seen_class[l] += 1
                total_correct_class[l] += (pred_val[i-start_idx, j] == l)

    # Added this section in to avoid division by 0 when a class is not seen
    total_correct_class = np.array(total_correct_class)
    total_seen_class = np.array(total_seen_class,dtype=np.float)
    zero_instance = np.where(total_seen_class==0)
    if len(zero_instance[0]) > 0:
        total_seen_class = np.delete(total_seen_class, zero_instance[0])
        total_correct_class = np.delete(total_correct_class, zero_instance[0])

    log_string('eval mean loss: %f' % (loss_sum / float(total_seen/num_point)))
    log_string('eval accuracy: %f'% (total_correct / float(total_seen)))
    log_string('eval avg class acc: %f' % (np.mean(total_correct_class/total_seen_class)))
    return (total_correct / float(total_seen))
