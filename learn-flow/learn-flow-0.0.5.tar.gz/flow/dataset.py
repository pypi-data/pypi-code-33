# coding=utf-8
"""
module dataset.py
____________________________
Base dataset wrapper definition.
"""
import tensorflow as tf


class Dataset(object):

    def __init__(self, app, partition="train", *args, **kwargs):
        # add to app datasets
        app.datasets[partition] = self

        # dataset partition name
        # possible values[train, test, validate]
        self._dataset = self.build_dataset()
        self._iterator_initializer = None
        self._iterator = None
        self.partition = partition.lower()
        if self.partition == "train":
            app.on_epoch_begin.connect(self.initialize_iterator, weak=False)
        elif self.partition == "validate":
            app.on_validate_begin.connect(self.initialize_iterator, weak=False)
        app.before_session_initialization.connect(self.get_iterator_initializer, weak=False)

    def get_iterator_initializer(self, sender):
        iterator = sender.iterator
        if self._iterator_initializer is None:
            self._iterator_initializer = iterator.make_initializer(self._dataset)
        return self._iterator_initializer

    def initialize_iterator(self, sender):
        if self._iterator_initializer is None:
            self._iterator = self.get_iterator()
            sender.iterator = self._iterator
            self._iterator_initializer = self.get_iterator_initializer(sender)

        current_session = tf.get_default_session()
        current_session.run(self._iterator_initializer)

    def get_iterator(self):
        # a function to be called when no other custom function is provided.
        if self._dataset is None:
            self._dataset = self.build_dataset()
        self._iterator = self._dataset.make_initializable_iterator()
        return self._iterator

    def build_dataset(self):
        raise NotImplementedError()
