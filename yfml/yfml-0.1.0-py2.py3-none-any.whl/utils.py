import tensorflow as tf
import numpy as np
import random


class Data:
    def __init__(self, data, label=None):
        self.data = data
        self.label = label
        self.num = len(data)
        self.ind = 0
        self.order = [i for i in range(self.num)]

    def shuffle(self):
        random.shuffle(self.order)

    def next_batch(self, batch_size):
        if self.ind + batch_size > self.num:
            self.ind = 0
        batch_data = [self.data[i] for i in self.order[self.ind: self.ind + batch_size]]
        if self.label is not None:
            batch_label = [self.label[i] for i in self.order[self.ind: self.ind + batch_size]]
            self.ind += batch_size
            return batch_data, batch_label
        else:
            self.ind += batch_size
            return batch_data

    def get_data(self, start_ind, stop_ind):
        if self.label is not None:
            return self.data[start_ind: stop_ind], self.label[start_ind:stop_ind]
        else:
            return self.data[start_ind: stop_ind]


def flatten(inputs):
    return tf.layers.flatten(inputs)


def reshape(inputs, new_shape):
    return tf.reshape(inputs, new_shape)


def static_shape(inputs):
    return inputs.get_shape(inputs)


def dynamic_shape(inputs):
    return tf.shape(inputs)


def shuffle_data(inputs, labels=None):
    length = len(inputs)
    order_ = [i for i in range(length)]
    random.shuffle(order_)
    sf_inputs = np.asarray([inputs[i] for i in order_])
    if labels is not None:
        sf_labels = np.asarray([labels[i] for i in order_])
        return sf_inputs, sf_labels
    else:
        return sf_inputs


def compute_accuracy(outputs, labels):
    correct_prediction = tf.equal(tf.argmax(outputs, 1), tf.argmax(labels, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    return accuracy


def int_holder(shape):
    return tf.placeholder(tf.int32, shape)


def fl_holder(shape):
    return tf.placeholder(tf.float32, shape)


def bool_holder(shape=None):
    return tf.placeholder(tf.bool, shape)