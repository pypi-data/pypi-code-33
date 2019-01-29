# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
Extends keras Callbacks. Provides automatic logging and tracking with Comet.ml
"""

import logging

import six

try:
    from keras import callbacks
except ImportError:
    from tensorflow.contrib.keras import callbacks


LOGGER = logging.getLogger(__name__)


class EmptyKerasCallback(callbacks.Callback):
    """
    Empty Keras callback. TODO(gidim): remove this
    """

    def __init__(self):
        super(EmptyKerasCallback, self).__init__()

    def on_epoch_begin(self, epoch, logs=None):
        pass

    def on_epoch_end(self, epoch, logs=None):
        pass

    def on_batch_begin(self, batch, logs=None):
        pass

    def on_batch_end(self, batch, logs=None):
        pass

    def on_train_begin(self, logs=None):
        pass

    def on_train_end(self, logs=None):
        pass


class KerasCallback(callbacks.Callback):
    """ Keras callback to report params, metrics to Comet.ml Experiemnt()"""

    def __init__(self, experiment, log_params=True, log_metrics=True, log_graph=True):
        """
        Create a new experiment and submit source code.
        :param api_key: User's API key. Required.
        """
        super(KerasCallback, self).__init__()

        # Inits the experiment with reference to the name of this class. Required for loading the correct
        # script file
        self.experiment = experiment
        self.log_params = log_params
        self.log_metrics = log_metrics
        self.log_graph = log_graph
        self.our_step = 0
        self._ignores = ["verbose", "do_validation", "validation_steps"]

    def on_epoch_begin(self, epoch, logs=None):
        LOGGER.debug("On epoch begin %s %s", epoch, logs)

    def on_epoch_end(self, epoch, logs=None):
        LOGGER.debug("On epoch end %s %s", epoch, logs)
        if self.log_metrics:
            self.experiment.log_epoch_end(epoch, step=self.our_step)
            if logs:
                for name, val in logs.items():
                    self.experiment.log_metric(name, val, step=self.our_step)

    def on_batch_begin(self, batch, logs=None):
        LOGGER.debug("On batch begin %s %s", batch, logs)

    def on_batch_end(self, batch, logs=None):
        """
        Logs training metrics.
        """
        LOGGER.debug("On batch end %s %s", batch, logs)

        self.our_step += 1

        if batch is not None and isinstance(batch, six.integer_types):
            if batch % 10 == 0:
                self._send_batch_messages(logs)
        else:
            self._send_batch_messages(logs)

    def _send_batch_messages(self, logs):
        if logs and self.log_metrics:
            for name, val in logs.items():
                self.experiment.log_metric(name, val, step=self.our_step)

    def on_train_begin(self, logs=None):
        """
        Sets model graph.
        """
        LOGGER.debug("On train begin %s", logs)

        if self.log_graph:
            self.experiment.set_model_graph(
                get_keras_json_model(self.experiment, self.model)
            )
        self.experiment.log_other("trainable_params", self.model.count_params())

        if self.log_params:
            if logs:
                for k, v in logs.items():
                    self.experiment.log_parameter(k, v)

            # Keras Callback doesn't set this parameter at creation by default
            if hasattr(self, "params") and self.params:
                for k, v in self.params.items():
                    if k != "metrics" and k not in self._ignores:
                        self.experiment.log_parameter(k, v)

            try:
                optimizer_name = self.model.optimizer.__class__.__name__
                self.experiment.log_parameters(
                    self.model.optimizer.get_config(), prefix=optimizer_name
                )
            except Exception:
                LOGGER.debug("Failed to extract optimizer information", exc_info=True)

    def on_train_end(self, *args, **kwargs):
        LOGGER.debug("On train end %r", locals())


def get_keras_json_model(experiment, model):
    # With multi-gpu models we save the original model in the experiment
    # storage
    storage_key = "gpu_model_%s" % id(model)
    json_model = experiment._storage["keras"].get(storage_key, None)

    if json_model is not None:
        return json_model

    else:
        try:
            return model.to_json()

        except Exception:
            LOGGER.warning("Failed to save keras graph model")
