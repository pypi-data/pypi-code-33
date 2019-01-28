import aether as ae
import tensorflow as tf
import numpy as np
import abc
import math
import random
import time
import logging
logger = logging.getLogger(__name__)


class TensorFlowArchitecture(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._operators = dict()

    def _print_all_variables(self):
        for i in tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES):
            print i

    @abc.abstractmethod
    def build(self):
        pass

class TensorFlowMlpArchitecture(TensorFlowArchitecture):

    def build(self, n_inputs, n_classes, n_hidden=None, keep_prob=1.0):
        if n_hidden is None:
            n_hidden = [32]

        inputs = tf.placeholder(tf.float32, [None, n_inputs])
        labels = tf.placeholder(tf.float32, [None, n_classes])
        is_training = tf.placeholder(tf.bool)

        x = tf.layers.dense(inputs=inputs, units=n_hidden[0], activation=tf.nn.sigmoid)
        x = tf.layers.dropout(inputs=x, rate=1.0-keep_prob, training=is_training)
        for h_i in range(1, len(n_hidden)):
            x = tf.layers.dense(inputs=x, units=n_hidden[h_i], activation=tf.nn.sigmoid)
            x = tf.layers.dropout(inputs=x, rate=1.0-keep_prob, training=is_training)

        logits = tf.layers.dense(inputs=x, units=n_classes)
        probabilities = tf.nn.softmax(logits)
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=logits, labels=labels))
        train_step = tf.train.AdamOptimizer().minimize(loss)

        # Add our TensorBoard summaries
        tf.summary.scalar('loss', loss)

        label_ids = tf.cast(tf.argmax(labels, 1), tf.int32)
        for k in [1, 2, 3, 5, 10]:
            if k >= n_classes:
                continue
            top_n = tf.reduce_mean(tf.cast(tf.nn.in_top_k(predictions=logits, targets=label_ids, k=k), tf.int32))
            tf.summary.scalar('top_{}_acc'.format(k), top_n)

        summaries = tf.summary.merge_all()

        self._operators = dict(
            inputs=inputs,
            labels=labels,
            is_training=is_training,
            loss=loss,
            train_step=train_step,
            probabilities=probabilities,
            summaries=summaries,
        )

        return self
TensorFlowArchitecture.register(TensorFlowMlpArchitecture)



class TensorFlowRnnArchitecture(TensorFlowArchitecture):

    def build(self, n_lookback, n_classes, num_layers=3, n_hidden=None, keep_prob=1.0):
        if n_hidden is None:
            n_hidden = 512

        time_inputs = tf.placeholder(tf.float32, [None, n_lookback])
        value_inputs = tf.placeholder(tf.float32, [None, n_lookback])
        label_inputs = tf.placeholder(tf.float32, [None, n_classes])
        is_training = tf.placeholder(tf.bool)

        # The dimension 2 represents the cell and the hidden state, respectively.
        # The cell state will generally be the input logits.
        # The hidden state will be zero.
        initial_state = tf.placeholder(tf.float32, [2, None, n_classes])
        # To get initial state into the tuple of LSTMStateTuples we need to do this:
        unrolled_state = tuple([tf.nn.rnn_cell.LSTMStateTuple(initial_state[0], initial_state[1])
                               for idx in range(num_layers)])

        inputs = tf.stack([time_inputs, value_inputs], axis=2)
        cell = [tf.nn.rnn_cell.LSTMCell(n_classes, state_is_tuple=True) for _ in range(num_layers)]
        cell = tf.nn.rnn_cell.MultiRNNCell(cell, state_is_tuple=True)
        rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, inputs, initial_state=unrolled_state)

        x = tf.layers.dropout(inputs=rnn_outputs, rate=1.0-keep_prob, training=is_training)
        x = tf.layers.dense(inputs=x, units=n_hidden, activation=tf.nn.softsign)
        logits = tf.layers.dense(inputs=x, units=n_classes)
        probabilities = tf.nn.softmax(logits)

        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(
            logits=logits, labels=tf.tile(tf.expand_dims(label_inputs, axis=1), [1, n_lookback, 1])))
        train_step = tf.train.AdamOptimizer().minimize(loss)

        # Add our TensorBoard summaries
        tf.summary.scalar('loss', loss)

        label_ids = tf.cast(tf.argmax(label_inputs, 1), tf.int32)
        for way_through in [0.3334, 0.6667, 1.0]:
            idx = int(n_lookback * way_through) - 1
            for k in [1, 2, 3, 5, 10]:
                if k >= n_classes:
                    continue
                top_n = tf.reduce_mean(tf.cast(tf.nn.in_top_k(predictions=logits[:,idx,:], targets=label_ids, k=k), tf.int32))
                tf.summary.scalar('top_{}_acc_{}'.format(k, way_through), top_n)

        summaries = tf.summary.merge_all()

        self._operators = dict(
            time_inputs=time_inputs,
            value_inputs=value_inputs,
            label_inputs=label_inputs,
            initial_state=initial_state,
            is_training=is_training,
            loss=loss,
            train_step=train_step,
            final_state=final_state,
            rnn_outputs=rnn_outputs,
            logits=logits,
            probabilities=probabilities,
            summaries=summaries,
        )

        return self
TensorFlowArchitecture.register(TensorFlowRnnArchitecture)


class TensorFlowModel(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, network):
        self._network = network

    def initialize(self, experiment_name, model_dir=None):
        logger.info("Initializing model and session.")
        config = tf.ConfigProto(allow_soft_placement = True)
        config.gpu_options.allow_growth=True
        session = tf.Session(config = config)
        tf.global_variables_initializer().run(session=session)

        self._model_dir = model_dir
        self._session = session
        self._saver = tf.train.Saver()
        self._reporter = ae.contrib.nn.session_reporter(experiment_name)

        if model_dir is None:
            self._summary_writer = None
        else:
            self._summary_writer = tf.summary.FileWriter(self._model_dir, self._session.graph)
        logger.info("Initializing model and session complete.")
        return self

    @abc.abstractmethod
    def train_on(self):
        pass

    def _is_checkpoint_epoch(self, epoch, checkpoint_interval, n_epochs):
        # self._reporter.save_report(self._gfs_config.runtime_save_directory)
        if not (checkpoint_interval is None or self._model_dir is None):
            if (checkpoint_interval == 1) or \
                    (epoch % (checkpoint_interval+1) and epoch is not 0 == 0) or \
                    (epoch == n_epochs):
                return True
        return False

    def batch_finish(self, batch, epoch, checkpoint_interval, n_epochs, summaries):
        if self._is_checkpoint_epoch(epoch, checkpoint_interval, n_epochs):
            self._summary_writer.add_summary(summaries, epoch)

    def epoch_finish(self, epoch, checkpoint_interval, n_epochs):
        # Epoch-end reporting
        self._reporter.epoch_report(epoch)

        # self._reporter.save_report(self._gfs_config.runtime_save_directory)
        if self._is_checkpoint_epoch(epoch, checkpoint_interval, n_epochs):
            self._saver.save(self._session, self._model_dir + "model.ckpt")


    @abc.abstractmethod
    def infer_on(self):
        pass

    def load_from_checkpoint(self, model_dir):
        logger.info("Loading Tensorflow Model from Checkpoint.")
        sess = tf.Session()
        load_saver = tf.train.import_meta_graph(model_dir + 'model.ckpt.meta')
        load_saver.restore(sess, tf.train.latest_checkpoint(model_dir))
        self._session = sess
        logger.info("Loading Tensorflow Model from Checkpoint Finished.")


class TensorflowRnnModel(TensorFlowModel):

    def train_on(self, data_x, data_y, data_c, n_lookback, batch_size=5, n_epochs=1, epoch_start=0, checkpoint_interval=None):
        n_instances = data_x.shape[0]
        n_batches = int(math.ceil(float(n_instances) / batch_size))

        # Training cycle.  Every sample will be trained on per epoch.
        for epoch in range(epoch_start, epoch_start + n_epochs):
            batch_order = [x for x in range(0, n_batches)]
            random.shuffle(batch_order)

            for batch_index in range(0, len(batch_order)):
                batch = batch_order[batch_index]
                batch_bounds = [batch * batch_size, min((batch+1) * batch_size, n_instances)]

                n_timestamps = data_x.shape[1]
                n_classes = data_c.shape[1]
                initial_state = np.stack([
                    np.array([[1./n_classes] * n_classes] * batch_size),
                    np.zeros((batch_size, n_classes))], axis=0)
                for ts_i in range(0, n_timestamps-n_lookback+1, n_lookback):
                    training_start = time.time()
                    time_inputs = data_x[batch_bounds[0]:batch_bounds[1], ts_i:ts_i+n_lookback]
                    value_inputs = data_y[batch_bounds[0]:batch_bounds[1], ts_i:ts_i+n_lookback]
                    label_inputs = data_c[batch_bounds[0]:batch_bounds[1]]
                    feed_dict = {self._network._operators["time_inputs"]: time_inputs,
                                 self._network._operators["value_inputs"]: value_inputs,
                                 self._network._operators["label_inputs"]: label_inputs,
                                 self._network._operators["is_training"]: True,
                                 self._network._operators["initial_state"]: initial_state,
                                 }

                    loss, summaries, _, final_state, = self._session.run([
                        self._network._operators["loss"],
                        self._network._operators["summaries"],
                        self._network._operators["train_step"],
                        self._network._operators["final_state"]
                    ], feed_dict=feed_dict)
                    initial_state = final_state[0]
                    training_end = time.time()
                    self._reporter.batch_report_add(epoch, batch, batch_index, len(batch_order),
                                                    dict(loss=loss),
                                                    training_end - training_start)
                    self.batch_finish(batch, epoch, checkpoint_interval, n_epochs, summaries)

            # Epoch-end reporting
            self.epoch_finish(epoch, checkpoint_interval, n_epochs)


    def infer_on(self, data_x):
        inference_start = time.time()
        feed_dict = {self._network._operators["time_inputs"]: data_x,
                     self._network._operators["is_training"]: False,
                     }
        xv, l, l2k = self._session.run([
            self._network._operators["coordinates"],
            self._network._operators["lagrangian"],
            self._network._operators["lagrangian_eq_second_kind"],
        ], feed_dict=feed_dict)
        inference_end = time.time()

        logger.info("Evaluation time:{}".format(inference_end - inference_start))
        return xv, l, l2k

TensorFlowModel.register(TensorflowRnnModel)


class TensorflowMlpModel(TensorFlowModel):

    def train_on(self, data_x, data_y, batch_size=5, n_epochs=1, epoch_start=0, checkpoint_interval=None, model_dir=None):
        n_instances = data_x.shape[0]
        n_batches = int(math.ceil(float(n_instances) / batch_size))

        # Training cycle.  Every sample will be trained on per epoch.
        for epoch in range(epoch_start, epoch_start + n_epochs):
            batch_order = [x for x in range(0, n_batches)]
            random.shuffle(batch_order)

            for batch_index in range(0, len(batch_order)):
                batch = batch_order[batch_index]
                batch_bounds = [batch * batch_size, min((batch+1) * batch_size, n_instances)]
                training_start = time.time()

                inputs = data_x[batch_bounds[0]:batch_bounds[1]]
                labels = data_y[batch_bounds[0]:batch_bounds[1]]
                feed_dict = {self._network._operators["inputs"]: inputs,
                             self._network._operators["labels"]: labels,
                             self._network._operators["is_training"]: True,
                             }

                loss, summaries, _, = self._session.run([
                    self._network._operators["loss"],
                    self._network._operators["summaries"],
                    self._network._operators["train_step"],
                ], feed_dict=feed_dict)
                training_end = time.time()
                self._reporter.batch_report_add(epoch, batch, batch_index, len(batch_order),
                                                dict(loss=loss),
                                                training_end - training_start)
                self.batch_finish(batch, epoch, checkpoint_interval, n_epochs, summaries)

            # Epoch-end reporting
            self.epoch_finish(epoch, checkpoint_interval, n_epochs)


    def infer_on(self, data_x):
        inference_start = time.time()
        feed_dict = {self._network._operators["time_inputs"]: data_x,
                     self._network._operators["is_training"]: False,
                     }
        xv, l, l2k = self._session.run([
            self._network._operators["coordinates"],
            self._network._operators["lagrangian"],
            self._network._operators["lagrangian_eq_second_kind"],
        ], feed_dict=feed_dict)
        inference_end = time.time()

        logger.info("Evaluation time:{}".format(inference_end - inference_start))
        return xv, l, l2k

TensorFlowModel.register(TensorflowMlpModel)

#
# def func1(x):
#     return np.random.uniform(0) * np.sin(x)
#
# def func2(x):
#     return np.random.uniform(0) * np.cos(x)
#
# n_points = 50
# n_data = 1000
# x_train = np.random.uniform(0.0, 2.0 * np.pi, size=[n_data, n_points])
# x_train = np.array([list(sorted(x_train[i])) for i in range(n_data)])
# y_train = [func1(x) for x in x_train[0:n_data/2]] +\
#           [func2(x) for x in x_train[n_data/2:]]
# y_train = np.array(y_train)
# c_train = np.array([[1,0]] * (n_data/2) + [[0,1]] * (n_data/2))
#
# s = np.random.choice(range(n_data), n_data, replace=False)
# x_train = x_train[s]
# y_train = y_train[s]
# c_train = c_train[s]
#
# n_lookback = n_points
# n_classes = 2
# num_layers = 3
# n_hidden = 512
# keep_prob = 1.0
#
# model_dir = "data/crop_classifier/"
#
# network = TensorFlowRnnArchitecture().build(n_lookback, n_classes, num_layers, n_hidden=n_hidden, keep_prob=keep_prob)
# model = TensorflowRnnModel(network).initialize("crop_classification", model_dir=model_dir)
# model.train_on(x_train, y_train, c_train, n_lookback, n_epochs=200, batch_size=1, checkpoint_interval=1)

# data_x = np.concatenate([x_train, y_train], axis=1)
# data_y = c_train
# network = TensorFlowMlpArchitecture().build(n_points * 2, n_classes, n_hidden=[n_hidden], keep_prob=keep_prob)
# model = TensorflowMlpModel(network).initialize("crop_classification", model_dir=model_dir)
# model.train_on(data_x, data_y, n_epochs=200, batch_size=25, checkpoint_interval=1)