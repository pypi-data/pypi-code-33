import numpy as np
import tensorflow as tf

from ..utils import rescale_img


class Dataset:
    def train_batch(self, batch_size):
        return NotImplemented

    def test_batch(self, batch_size):
        return NotImplemented

    def valid_batch(self, batch_size):
        return NotImplemented

    @staticmethod
    def preprocess(datasets, class_num,
                   min_from, max_from, min_to, max_to,
                   shape, categorical):
        (x_train, y_train), (x_test, y_test) = datasets

        x_train = Dataset.rescale(x_train, min_from, max_from, min_to, max_to)
        x_test = Dataset.rescale(x_test, min_from, max_from, min_to, max_to)

        x_train = Dataset.reshape(x_train, shape)
        x_test = Dataset.reshape(x_test, shape)

        if categorical:
            y_train = tf.keras.utils.to_categorical(y_train, class_num)
            y_test = tf.keras.utils.to_categorical(y_test, class_num)

        return (x_train, y_train), (x_test, y_test)

    @staticmethod
    def reshape(x, shape=None):
        if shape is None:
            return x

        assert np.prod(x.shape[1:]) == np.prod(shape), 'Number of elements doesnt match.'

        new_shape = (-1,) + tuple(shape)
        return np.reshape(x, new_shape)

    @staticmethod
    def rescale(x, min_from, max_from, min_to, max_to):
        return rescale_img(x, min_from=min_from, max_from=max_from, min_to=min_to, max_to=max_to)

