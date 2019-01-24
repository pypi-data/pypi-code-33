from collections import OrderedDict
import tensorflow as tf
import os

from ..utils import lazy_property
from .network import Network


class CheckPointable:
    @property
    def name(self):
        return self.__class__.__name__

    @property
    def path_ckpt(self):
        return './ckpts/%s/%s' % (self.name, self.name)

    @property
    def trainables(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @lazy_property
    def saver(self):
        return tf.train.Saver(var_list=self.trainables)

    def save(self, sess, epoch=None):
        os.makedirs(os.path.dirname(self.path_ckpt), exist_ok=True)
        self.saver.save(sess, self.path_ckpt, global_step=epoch)

    def load(self, sess):
        self.saver.restore(sess, self.path_ckpt)


class Explainable:
    class Explain:
        @staticmethod
        def sensitivity(logits, x):
            class_num = logits.get_shape()[-1]
            logits_splitted = tf.split(logits, class_num, axis=-1)
            gs = [tf.gradients(logit, x)[0][0] for logit in logits_splitted]
            sals = [tf.reduce_max(tf.abs(g), axis=-1) for g in gs]
            return tf.stack(sals)

        def get_sensitivity_map(self, sess, logits, x, image):
            sal = self.sensitivity(logits, x)
            return sess.run(sal, feed_dict={
                x: [image]
            })


class Architecture(CheckPointable, Explainable):
    def __init__(self, model_fn):
        super().__init__()

        self.is_built = False
        self.model_fn = model_fn

        self.weights = OrderedDict()
        self.building_net = None

    def __call__(self, *args, **kwargs):
        if self.is_built:
            return self._build_network(*args, **kwargs, reuse=True)
        else:
            result = self._build_network(*args, **kwargs, reuse=False)
            self.is_built = True
            return result

    def _build_network(self, *args, reuse=False, **kwargs):
        self.building_net = Network()
        outputs = self.model_fn(*args, **kwargs, reuse=reuse)

        network = self.building_net

        network.outputs = outputs
        network.inputs = list(args) + list(kwargs.values())

        self.building_net = None
        return network

    def register_layer(self, tensor, layer_name, monitor=False):
        self.building_net.register_layer(tensor, layer_name, monitor)

    def register_weight(self, variable, weight_name, monitor=False):
        if self.is_built:
            return

        self.weights[weight_name] = Weight(variable, weight_name, monitor)

    def get_weight(self, weight_name):
        return self.weights[weight_name].variable

    @lazy_property
    def summary(self):
        summarys = list()
        for weight in self.weights:
            if weight.monitor:
                summarys.append(
                    tf.summary.histogram(weight.name, weight.variable)
                )

        if len(summarys) > 0:
            return tf.summary.merge(summarys)
        else:
            return []


class Weight:
    def __init__(self, variable, name, monitor):
        self._variable = variable
        self.name = name
        self.monitor = monitor

    @property
    def variable(self):
        return self._variable
