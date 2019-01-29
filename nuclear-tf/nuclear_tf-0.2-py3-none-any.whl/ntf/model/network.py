from collections import OrderedDict
from ..utils import lazy_property, calc_num_batch
import tensorflow as tf
import numpy as np


class Network:
    def __init__(self, name=''):
        self.layers = OrderedDict()
        self.inputs = None
        self.outputs = None

    def register_layer(self, tensor, layer_name,
                       monitor=False):
        self.layers[layer_name] = Layer(tensor, layer_name, monitor)

    def get_layer(self, layer_name):
        return self.layers[layer_name].tensor

    @lazy_property
    def summary(self):
        summarys = list()
        for layer in self.layers:
            if layer.monitor:
                summarys.append(
                    tf.summary.histogram(layer.name, layer.tensor)
                )

        if len(summarys) > 0:
            return tf.summary.merge(summarys)
        else:
            return []

    @property
    def input_default(self):
        return NotImplemented

    def feedforward1(self, sess, Xs, batch_size=32):
        batch_num = calc_num_batch(Xs.shape[0], batch_size)
        results = [sess.run(self.outputs, feed_dict={self.inputs[0]: Xs[i * batch_size: (i + 1) * batch_size]})
                   for i in range(batch_num)]

        result = list()
        for i in range(len(self.outputs)):
            result_one = np.concatenate([r[i] for r in results], axis=0)
            result.append(result_one)

        return result


class Layer:
    def __init__(self, tensor, name, monitor):
        self._tensor = tensor
        self.name = name
        self.monitor = monitor

    @property
    def tensor(self):
        return self._tensor
