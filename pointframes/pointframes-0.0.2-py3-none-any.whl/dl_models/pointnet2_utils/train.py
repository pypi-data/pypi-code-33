import argparse
import math
from datetime import datetime
import numpy as np
import tensorflow as tf
import socket
import importlib
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(base_dir)

sys.path.insert(0, base_dir)
sys.path.insert(0, base_dir+'/utils')

import provider
import tf_util2
import pc_util

import pointframes as pf

def pointnet2_preprocess_data(pointnet2, train_dataframes, test_split=0.2, weights=False):
    ''' Function to strip PointCloud object into a
        PointNet2_Data object. PointNet2.data should be a
        python list containing PointCloud object instances.
        args:
            pointnet2 : PointNet2 object
        returns:
            pointnet2_data : PointNet2_Data object
    '''

    pf.check_attributes(train_dataframes[0], ['X', 'Y', 'Z', 'class'])

    first_instance = True
    classes = []

    # Initialise empty train data and label arrays
    train_data = np.zeros((1, pointnet2.num_points, 3))
    train_labels = np.zeros((1, pointnet2.num_points))

    if weights == True:
        train_weights = np.zeros((1, pointnet2.num_points), dtype='float32')

    # Loop through all PointCloud objects and extract points and labels
    for pointcloud in train_dataframes:
        tmp_data = pointcloud[['X', 'Y', 'Z']].values
        tmp_labels = pointcloud[['class']].values
        if weights == True:
            tmp_weights = 1-pointcloud[['inv_prob']].values
            tmp_weights = 1/np.log(1.2+tmp_weights)

        if first_instance == True:
            train_data[0] = tmp_data
            train_labels[0] = tmp_labels.flatten()
            classes.append(np.unique(tmp_labels))
            if weights == True:
                train_weights[0] = tmp_weights.flatten()
            first_instance = False
        else:
            tmp_data = np.expand_dims(tmp_data, axis=0)
            tmp_labels = tmp_labels.flatten()
            train_data = np.vstack((train_data, tmp_data))
            train_labels = np.vstack((train_labels, tmp_labels))
            classes.append(np.unique(tmp_labels))
            if weights == True:
                tmp_weights = tmp_weights.flatten()
                train_weights = np.vstack((train_weights, tmp_weights))

    # I assume there is a more Pythonic way for doing this?
    # Extract all unique values from list of numpy arrays
    unique_list = []
    for arr in np.array(classes):
        [unique_list.append(val) for val in arr]

    unique_list = np.unique(unique_list)
    for i, arr in enumerate(train_labels):
        for j, val in enumerate(arr):
            train_labels[i][j] = np.where([val==unique_list])[1][0]

    # Initialise and populate a PointNet2_Data object instance
    training_data = pf.PointNet2_Data()
    training_data.test_data = train_data[-int(np.around(len(train_data)*test_split)):]
    training_data.test_labels = train_labels[-int(np.around(len(train_labels)*test_split)):]
    training_data.train_data = train_data[0:-int(np.around(len(train_data)*test_split))]
    training_data.train_labels = train_labels[0:-int(np.around(len(train_labels)*test_split))]
    training_data.num_classes = len(np.unique(unique_list))

    if weights == True:
        training_data.test_weights = train_weights[-int(np.around(len(train_weights)*test_split)):]
        training_data.train_weights = train_weights[0:-int(np.around(len(train_weights)*test_split))]
    else:
        training_data.test_weights = np.ones(test_labels.shape)
        training_data.train_weights = np.ones(train_labels.shape)

    return training_data

def log_string(out_str):
    log_fout.write(out_str+'\n')
    log_fout.flush()
    print(out_str)

def get_learning_rate(batch):
    learning_rate = tf.train.exponential_decay(
                        base_learning_rate,  # base learning rate.
                        batch * batch_size,  # current index into the dataset.
                        decay_step,          # decay step.
                        decay_rate,          # decay rate.
                        staircase=True)
    learing_rate = tf.maximum(learning_rate, 0.00001) # clip the learning rate!
    return learning_rate

def get_bn_decay(batch):

    global bn_init_decay
    global batch_size
    global bn_decay_decay_step
    global bn_decay_decay_rate

    bn_momentum = tf.train.exponential_decay(
                      bn_init_decay,
                      batch*batch_size,
                      bn_decay_decay_step,
                      bn_decay_decay_rate,
                      staircase=True)
    bn_decay = tf.minimum(bn_decay_clip, 1 - bn_momentum)
    return bn_decay

def train_pointnet2(pointnet2):

    global batch_size
    global num_point
    global max_epoch
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

    epoch_cnt = 0

    batch_size = pointnet2.batch_size
    num_point = pointnet2.num_points
    max_epoch = pointnet2.max_epoch
    base_learning_rate = pointnet2.learning_rate
    gpu_index = pointnet2.gpu
    momentum = pointnet2.momentum
    optimizer = pointnet2.optimizer
    decay_step = pointnet2.decay_step
    decay_rate = pointnet2.decay_rate

    os.environ["cuda_device_order"] = "pci_bus_id"
    os.environ["cuda_visible_devices"] = str(gpu_index)

    model = importlib.import_module(pointnet2.model) # import network module
    model_file = os.path.join(base_dir, pointnet2.model+'.py')
    log_dir = pointnet2.log_dir
    if not os.path.exists(log_dir): os.mkdir(log_dir)
    if not os.path.exists(os.path.join(log_dir, "models")): os.mkdir(os.path.join(log_dir, "models"))
    log_fout = open(os.path.join(log_dir, 'log_train.txt'), 'w')

    bn_init_decay = 0.5
    bn_decay_decay_rate = 0.5
    bn_decay_decay_step = float(decay_step)
    bn_decay_clip = 0.99

    hostname = socket.gethostname()

    training_data = pointnet2.train_data
    num_classes = pointnet2.train_data.num_classes
    num_features = training_data.train_data.shape[-1]

    print ('[info] loaded dataset of size {:}'.format(training_data.train_data.shape))

    with tf.Graph().as_default():
        with tf.device('/gpu:'+str(gpu_index)):
            pointclouds_pl, labels_pl, smpws_pl = model.placeholder_inputs(batch_size, num_point)
            is_training_pl = tf.placeholder(tf.bool, shape=())
            print (is_training_pl)

            # note the global_step=batch parameter to minimize.
            # that tells the optimizer to helpfully increment the 'batch' parameter for you every time it trains.
            batch = tf.Variable(0)
            bn_decay = get_bn_decay(batch)
            tf.summary.scalar('bn_decay', bn_decay)

            print ("[info] getting model and loss")
            # get model and loss
            pred, end_points = model.get_model(pointclouds_pl, is_training_pl, num_classes, bn_decay=bn_decay)
            loss = model.get_loss(pred, labels_pl, smpws_pl)
            tf.summary.scalar('loss', loss)

            correct = tf.equal(tf.argmax(pred, 2), tf.to_int64(labels_pl))
            accuracy = tf.reduce_sum(tf.cast(correct, tf.float32)) / float(batch_size*num_point)
            tf.summary.scalar('accuracy', accuracy)

            print ("[info] getting training operator")
            # get training operator
            learning_rate = get_learning_rate(batch)
            tf.summary.scalar('learning_rate', learning_rate)
            if optimizer == 'momentum':
                optimizer = tf.train.MomentumOptimizer(learning_rate, momentum=momentum)
            elif optimizer == 'adam':
                optimizer = tf.train.AdamOptimizer(learning_rate)
            train_op = optimizer.minimize(loss, global_step=batch)

            # add ops to save and restore all the variables.
            saver = tf.train.Saver()

        # create a session
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.allow_soft_placement = True
        config.log_device_placement = False
        sess = tf.Session(config=config)

        # add summary writers
        merged = tf.summary.merge_all()
        train_writer = tf.summary.FileWriter(os.path.join(log_dir, 'train'), sess.graph)
        test_writer = tf.summary.FileWriter(os.path.join(log_dir, 'test'), sess.graph)

        # init variables
        init = tf.global_variables_initializer()
        sess.run(init)
        #sess.run(init, {is_training_pl: true})

        ops = {'pointclouds_pl': pointclouds_pl,
               'labels_pl': labels_pl,
	           'smpws_pl': smpws_pl,
               'is_training_pl': is_training_pl,
               'pred': pred,
               'loss': loss,
               'train_op': train_op,
               'merged': merged,
               'step': batch,
               'end_points': end_points}

        best_acc = -1
        for epoch in range(max_epoch):
            if epoch%10==0:
                log_string('**** epoch %03d ****' % (epoch))
            sys.stdout.flush()

            train_one_epoch(sess, ops, train_writer, training_data)
            if epoch%10==0:
                acc = eval_one_epoch(sess, ops, test_writer, training_data)
            #acc = eval_whole_scene_one_epoch(sess, ops, test_writer)
            if acc > best_acc:
                best_acc = acc
                save_path = saver.save(sess, os.path.join(log_dir, "models", "best_model_epoch_%03d.ckpt"%(epoch)))
                log_string("model saved in file: %s" % save_path)

            # save the variables to disk.
            if epoch % 10 == 0:
                save_path = saver.save(sess, os.path.join(log_dir, "models", "model.ckpt"))
                log_string("model saved in file: %s" % save_path)

def get_batch_train(train_data, train_label, train_weights, idxs, start_idx, end_idx):

    bsize = end_idx-start_idx
    batch_data = np.zeros((bsize, num_point, 3))
    batch_label = np.zeros((bsize, num_point), dtype=np.int32)
    batch_smpw = np.zeros((bsize, num_point), dtype=np.float32)
    for i in range(bsize):
        ps = train_data[start_idx+i,:]
        seg = train_label[start_idx+i,:]
        wei = train_weights[start_idx+i,:]
        batch_data[i,...] = ps
        batch_label[i,:] = seg
        batch_smpw[i,:] = wei

    dropout_ratio = np.random.random()*0.875 # 0-0.875
    drop_idx = np.where(np.random.random((ps.shape[0]))<=dropout_ratio)[0]
    batch_data[i,drop_idx,:] = batch_data[i,0,:]
    batch_label[i,drop_idx] = batch_label[i,0]
    batch_smpw[i,drop_idx] = batch_smpw[i,0]
    return batch_data, batch_label, batch_smpw

def get_batch_eval(test_data, test_label, test_weights, idxs, start_idx, end_idx):
    bsize = end_idx-start_idx
    batch_data = np.zeros((bsize, num_point, 3))
    batch_label = np.zeros((bsize, num_point), dtype=np.int32)
    batch_smpw = np.zeros((bsize, num_point), dtype=np.float32)
    for i in range(bsize):
        ps = test_data[start_idx+i,:]
        seg = test_label[start_idx+i,:]
        wei = test_weights[start_idx+i,:]
        batch_data[i,...] = ps
        batch_label[i,:] = seg
        batch_smpw[i,:] = wei
    return batch_data, batch_label, batch_smpw

def train_one_epoch(sess, ops, train_writer, training_data):
    """ ops: dict mapping from string to tf ops """
    is_training = True

    # shuffle train samples
    train_idxs = np.arange(0, len(training_data.train_data))
    np.random.shuffle(train_idxs)
    num_batches = len(training_data.train_data)/batch_size

    total_correct = 0
    total_seen = 0
    loss_sum = 0
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = (batch_idx+1) * batch_size
        batch_data, batch_label, batch_smpw = get_batch_train(training_data.train_data,
                                                              training_data.train_labels,
                                                              training_data.train_weights,
                                                              train_idxs,
                                                              start_idx,
                                                              end_idx)
        # augment batched point clouds by rotation
        #aug_data = provider.rotate_point_cloud_z(batch_data)
        feed_dict = {ops['pointclouds_pl']: batch_data,
                     ops['labels_pl']: batch_label,
		             ops['smpws_pl']:batch_smpw,
                     ops['is_training_pl']: is_training,}
        summary, step, _, loss_val, pred_val = sess.run([ops['merged'], ops['step'],
                                                         ops['train_op'], ops['loss'],
                                                         ops['pred']], feed_dict=feed_dict)
        log_string("step: {:} loss: {:}".format(step, loss_val))
        train_writer.add_summary(summary, step)
        pred_val = np.argmax(pred_val, 2)
        correct = np.sum(pred_val == batch_label)
        total_correct += correct
        total_seen += (batch_size*num_point)
        loss_sum += loss_val
        if (batch_idx+1)%100 == 0:
            log_string('mean loss: %f' % (loss_sum / 10))
            log_string('accuracy: %f' % (total_correct / float(total_seen)))
            total_correct = 0
            total_seen = 0
            loss_sum = 0

# evaluate on randomly chopped scenes
def eval_one_epoch(sess, ops, test_writer, training_data):
    """ ops: dict mapping from string to tf ops """
    global epoch_cnt
    is_training = False
    test_idxs = np.arange(0, len(training_data.test_data))
    num_batches = len(training_data.test_data)/batch_size

    total_correct = 0
    total_seen = 0
    loss_sum = 0
    total_seen_class = [0 for _ in range(training_data.num_classes)]
    total_correct_class = [0 for _ in range(training_data.num_classes)]

    total_correct_vox = 0
    total_seen_vox = 0
    total_seen_class_vox = [0 for _ in range(training_data.num_classes)]
    total_correct_class_vox = [0 for _ in range(training_data.num_classes)]

    log_string('--- evaluation ---')

    labelweights = np.zeros(21)
    labelweights_vox = np.zeros(21)
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = (batch_idx+1) * batch_size
        batch_data, batch_label, batch_smpw = get_batch_eval(training_data.test_data,
                                                             training_data.test_labels,
                                                             training_data.test_weights,
                                                             test_idxs,
                                                             start_idx,
                                                             end_idx)

        #aug_data = provider.rotate_point_cloud_z(batch_data)

        feed_dict = {ops['pointclouds_pl']: batch_data,
                     ops['labels_pl']: batch_label,
	  	             ops['smpws_pl']: batch_smpw,
                     ops['is_training_pl']: is_training}
        summary, step, loss_val, pred_val = sess.run([ops['merged'],
                                                      ops['step'],
                                                      ops['loss'],
                                                      ops['pred']], feed_dict=feed_dict)
        test_writer.add_summary(summary, step)
        pred_val = np.argmax(pred_val, 2) # bxn

        correct = np.sum(pred_val == batch_label[start_idx:end_idx])
        total_correct += correct
        total_seen += (batch_size*num_point)
        loss_sum += (loss_val*batch_size)
        for i in range(start_idx, end_idx):
            for j in range(num_point):
                l = batch_label[i, j]
                total_seen_class[l] += 1
                total_correct_class[l] += (pred_val[i-start_idx, j] == l)

        total_correct_class = np.array(total_correct_class)
        total_seen_class = np.array(total_seen_class,dtype=np.float)
        zero_instance = np.where(total_seen_class==0)
        if len(zero_instance[0]) > 0:
            total_seen_class = np.delete(total_seen_class, zero_instance[0])
            total_correct_class = np.delete(total_correct_class, zero_instance[0])

        log_string('eval mean loss: %f' % (loss_sum / float(total_seen/num_point)))
        log_string('eval accuracy: %f'% (total_correct / float(total_seen)))
        log_string('eval avg class acc: %f' % (np.mean(total_correct_class/total_seen_class)))
        log_string('--- --- --- --- ---')

        epoch_cnt += 1

        return total_correct / float(total_seen)

if __name__ == "__main__":
    log_string('pid: %s'%(str(os.getpid())))
    train()
    log_fout.close()
