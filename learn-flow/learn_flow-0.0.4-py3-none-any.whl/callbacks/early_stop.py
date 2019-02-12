# -*- coding: utf-8 -*-
"""
module early_stop.py
-----------------------
Early Stop training Callback.
"""
import numpy as np
import tensorflow as tf
from . import ModeEnum

class EarlyStopping(object):
    """
    Stop training when a monitored quantity has stopped improving.
    """

    def __init__(
            self,
            app,
            monitor='loss', min_delta=0, patience=0, verbose=1,
            mode: ModeEnum=ModeEnum.MIN,
            baseline=None
    ):
        """
        callback initialization.

        :param app: Main class instance for which the callback is applied.

        :param monitor: quantity to be monitored.

        :param min_delta: minimum change in the monitored quantity
          to qualify as an improvement, i.e. an absolute
          change of less than min_delta, will count as no
          improvement.

        :param patience: number of epochs with no improvement
          after which training will be stopped.

        :param verbose: verbosity mode.

        :param mode: one of {min, max}. In `min` mode,
          training will stop when the quantity
          monitored has stopped decreasing; in `max`
          mode it will stop when the quantity
          monitored has stopped increasing; in `auto`
          mode, the direction is automatically inferred
          from the name of the monitored quantity.

        :param baseline: baseline value for the monitored quantity.
          Training will stop if the model doesn't show improvement over the
          baseline.
        """

        self.monitor = monitor
        self.patience = patience
        self.verbose = verbose
        self.baseline = baseline
        self.min_delta = abs(min_delta)
        self.wait = 0
        self.stopped_epoch = 0

        if mode is ModeEnum.MIN:
            self.monitor_op = np.less
            self.best = np.Inf
            self.min_delta *= 1
        elif mode is ModeEnum.MAX:
            self.monitor_op = np.greater
            self.best = -np.Inf
            self.min_delta *= -1

        # subscribing to callbacks
        app.on_train_begin.connect(self.on_train_begin, weak=False)
        app.on_epoch_end.connect(self.on_epoch_end, weak=False)
        app.on_train_end.connect(self.on_train_end, weak=False)

    def on_train_begin(self, sender):
        # Allow instances to be re-used
        self.wait = 0
        self.stopped_epoch = 0
        if self.baseline is not None:
            self.best = self.baseline

    def on_epoch_end(self, sender):
        # current = logs.get(self.monitor)
        epoch = sender.current_state["current_epoch"]
        current = sender.current_state.get(self.monitor)
        if current is None:
            raise ValueError(
                'Early stopping conditioned on metric `{}` '
                'which is not available. Available metrics are: %s'.format(
                    self.monitor,
                    ','.join(list(sender.current_state.keys()))
                )
            )
        if self.monitor_op(current - self.min_delta, self.best):
            self.best = current
            self.wait = 0
        else:
            self.wait += 1
            if self.wait >= self.patience:
                self.stopped_epoch = epoch
                sender.stop_train = True

    def on_train_end(self, sender):
        if self.stopped_epoch > 0 and self.verbose > 0:
            print('Epoch {:05d}: early stopping'.format((self.stopped_epoch + 1)))
