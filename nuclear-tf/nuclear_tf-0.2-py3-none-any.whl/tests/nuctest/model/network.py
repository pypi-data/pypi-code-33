from collections import OrderedDict
from ..utils import lazy_property
import tensorflow as tf


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


class Layer:
    def __init__(self, tensor, name, monitor):
        self._tensor = tensor
        self.name = name
        self.monitor = monitor

    @property
    def tensor(self):
        return self._tensor

