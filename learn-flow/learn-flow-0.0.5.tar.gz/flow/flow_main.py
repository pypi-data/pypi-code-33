# -*- coding: utf-8 -*-
"""
module flow_main.py
--------------------
Main flow application module.
"""
import os
import sys
import tensorflow as tf
from .config import Config
import numpy as np
import pickle
import time
from blinker import signal

# class Inputs(object):
#     def __init__(self):
#         pass
#
#
# class Outputs(object):
#     def __init__(self):
#         pass


class FlowMain(object):
    """ Project main class.
    """
    __config_path__ = "../settings/flow.cfg"

    def __init__(self, session: tf.Session=None):
        """Main module initialization."""
        self.config = self.get_config()
        if session is None:
            self.tf_sess = tf.Session()
        else:
            self.tf_sess = session

        tf.keras.backend.set_session(self.tf_sess)
        self.datasets = dict()
        # set in _losses
        self.loss = None
        # set in _metrics
        self.metrics = list()
        self.iterator = None
        self.stop_train = False
        self.history = None
        self.current_state = dict()
        # callbacks initialization
        self._initialize_train_callbacks()

    def _initialize_train_callbacks(self):
        """self training callbacks initialization."""
        self.on_epoch_begin = signal("on_epoch_begin")
        self.on_epoch_end = signal("on_epoch_end")
        self.on_batch_begin = signal("on_batch_begin")
        self.on_batch_end = signal("on_batch_end")
        self.on_train_begin = signal("on_train_begin")
        self.on_train_end = signal("on_train_end")
        self.on_validate_begin = signal("on_validate_end")
        self.on_validate_end = signal("on_validate_end")
        self.before_session_initialization = signal("before_session_initialization")

    @classmethod
    def get_config(cls):
        """ A configuration loader function.
        Builds the configuration object, loads the configuration from the specified files
        and then returns it.
        :return: a Config object.
        """
        config = Config()
        config.add_path(cls.__config_path__)
        # load tripod configuration
        config.load_config()
        return config

    def _losses(self, model):
        pass

    def _metrics(self, model):
        pass

    def _callbacks(self):
        pass

    def get_model(self, *args, **kwargs):
        """
        Layers and model definition
        :return: a compiled model
        """
        pass

    def _optimizer(self):
        pass

    def train(self, *args, **kwargs):
        pass

    def evaluate(self):
        sess = tf.get_default_session()
        outputs = list()
        output_names = list()
        for m in self.metrics:
            name = m.name.split(":")[0]
            outputs.append(m)
            if name.startswith("valid_"):
                output_names.append(name)
            else:
                output_names.append("valid_"+name)

        accumulators = self._prepare_accumulators(output_names)

        try:
            while True:
                ret = sess.run(
                    fetches=outputs
                )
                # accumulate outputs
                for i in range(len(accumulators)):
                    accumulators[i].append(ret[i])

        except tf.errors.OutOfRangeError:
            pass

        for i in range(len(accumulators)):
            self.current_state[output_names[i]] = np.mean(accumulators[i])

    def _train_loop(self):
        tf.keras.backend.set_learning_phase(1)
        train_ds = self.datasets["train"]
        ds_iterator = tf.data.Iterator.from_structure(train_ds._dataset.output_types, train_ds._dataset.output_shapes)
        self.iterator = ds_iterator
        inputs = ds_iterator.get_next()
        model = self.get_model(inputs)

        # loss initialization
        self._losses(model)
        # metrics initialization
        self._metrics(model)
        self._callbacks()

        optimizer = self._optimizer()
        update_op = optimizer.minimize(self.loss)
        outputs_names = ["loss"]
        outputs = [self.loss]

        for m in self.metrics:
            name = m.name.split(":")[0]
            if not name.startswith("valid_"):
                outputs.append(m)
                outputs_names.append(name)

        outputs.append(update_op)
        # before session initialization callback
        self.before_session_initialization.send(self)
        # tf global variables initialization (session variables initialization)
        sess = tf.get_default_session()
        sess.run(tf.global_variables_initializer())

        batch_size = int(self.config["FLOW.batch_size"])

        # on train begin triggers
        self.on_train_begin.send(self)
        for epoch_i in range(int(self.config["FLOW.N_EPOCHS"])):
            self.current_state["current_epoch"] = epoch_i
            batch_begin = time.time()
            accumulators = self._prepare_accumulators(outputs_names)
            # epoch begin trigger
            self.on_epoch_begin.send(self)
            try:
                while True:
                    # on batch begin triggers
                    self.on_batch_begin.send(self)

                    ret = sess.run(
                        fetches=outputs
                    )
                    # accumulate outputs
                    for i in range(len(accumulators)):
                        accumulators[i].append(ret[i])
                    # on batch end triggers
                    self.on_batch_end.send(self)
            except tf.errors.OutOfRangeError:
                pass

            batch_end = time.time()
            # on epoch end triggers
            for i in range(len(accumulators)):
                self.current_state[outputs_names[i]] = np.mean(accumulators[i])
            self.current_state["learning_rate"] = self._get_current_lr(optimizer)

            if "validate" in self.datasets:
                self.on_validate_begin.send(self)
                self.evaluate()
                self.on_validate_end.send(self)

            self.on_epoch_end.send(self)
            print(
                "Ephoc '{i}'=> loss: {loss:0.5f}, ".format(
                    i=epoch_i+1,
                    loss=self.current_state["loss"]
                ), self.current_state
            )

            # checks when the stop train flag is set to true
            # and break the main training loop when it happens
            if self.stop_train:
                break

        # on train end triggers
        self.on_train_end.send(self)

    def _prepare_accumulators(self, output_names):
        accumulators = list()
        for i in range(len(output_names)):
            accumulators.append(list())
        return accumulators

    def _get_current_lr(self, optimizer):
        """
        Returns the current learning rate and learning_rate tensor.
        :param optimizer: tensorflow optimizer.
        """
        if hasattr(optimizer, "_lr_t"):
            # lr_t = optimizer._lr_t
            lr_t = optimizer._lr
        elif hasattr(optimizer, "_learning_rate_tensor"):
            # lr_t = optimizer._learning_rate_tensor
            lr_t = optimizer._learning_rate
        else:
            raise AttributeError("Could not fint learning rate attribute on the optimizer.")
        sess = tf.get_default_session()
        lr, = sess.run(
            fetches=[lr_t],
        )

        return lr, lr_t

