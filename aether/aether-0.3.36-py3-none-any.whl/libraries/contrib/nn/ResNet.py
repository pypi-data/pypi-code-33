from __future__ import absolute_import
import tensorflow as tf
from aether.libraries.contrib.nn.learning import TensorFlowArchitecture, TensorflowMlpModel
from aether.libraries.contrib.nn.tf_layers import tf_layers
from aether.libraries.contrib.nn.tf_summaries import tf_summaries
from six.moves import range


import logging
logger = logging.getLogger(__name__)


# Inspired by the original "Deep Residual Learning for Image Recognition" CVPR 2016 Paper

class ResNetBuilder(object):

    @staticmethod
    def _conv2d_fixed_padding(x, filters, num_row, num_col, padding='same', strides=(1, 1)):
        """Strided 2-D convolution with explicit padding."""
        # The padding is consistent and is based only on `kernel_size`, not on the
        # dimensions of `inputs` (as opposed to using `tf.layers.conv2d` alone).
        return tf.layers.conv2d(
            inputs=x, filters=filters, kernel_size=(num_row, num_col), strides=strides,
            padding=padding, use_bias=False, activation=None,
            kernel_initializer=tf.variance_scaling_initializer())


    @staticmethod
    def _ResNetBuildingBlock(x, filters, num_row, num_col, is_train, name, conv1x1=False, padding='same', strides=(1, 1)):
        with tf.variable_scope(name):
            y = ResNetBuilder._conv2d_fixed_padding(x, filters, num_row, num_col, strides=strides, padding=padding)
            y = tf.layers.batch_normalization(y, training=is_train)
            y = tf.nn.relu(y)
            y = ResNetBuilder._conv2d_fixed_padding(y, filters, num_row, num_col, strides=strides, padding=padding)
            if conv1x1:
                x = ResNetBuilder._conv2d_fixed_padding(x, filters, 1, 1, strides=strides, padding=padding)
            y = y + x
            y = tf.layers.batch_normalization(y, training=is_train)
            y = tf.nn.relu(y)
        return y

    @staticmethod
    def _ResNetBottleneckBlock(x, filters, num_row, num_col, is_train, name, conv1x1=True, padding='same', strides=(1, 1)):
        with tf.variable_scope(name):
            y = tf.layers.conv2d(x, filters, (1, 1), strides=strides, activation=None, padding=padding, kernel_initializer=tf.contrib.layers.xavier_initializer(uniform=False))
            y = tf.layers.batch_normalization(y, training=is_train)
            y = tf.nn.relu(y)
            y = tf.layers.conv2d(y, filters, (num_row, num_col), strides=strides, activation=None, padding=padding)
            y = tf.layers.batch_normalization(y, training=is_train)
            y = tf.nn.relu(y)
            y = tf.layers.conv2d(y, 4 * filters, (1, 1), strides=strides, activation=None, padding=padding)
            if conv1x1:
                x = tf.layers.conv2d(x, 4 * filters, (1, 1), strides=strides, activation=None, padding=padding)
            y = y + x
            y = tf.layers.batch_normalization(y, training=is_train)
            y = tf.nn.relu(y)
        return y

    @staticmethod
    def _ResNetStemModule(inputs, filters, is_train, name, padding='same'):
        with tf.variable_scope(name):
            y = tf.layers.conv2d(inputs, filters, (7, 7), strides=(2, 2), activation=None, padding=padding)
            y = tf.layers.batch_normalization(y, training=is_train)
            y = tf.nn.relu(y)
            y = tf.layers.max_pooling2d(y, (3, 3), strides=(2, 2), padding=padding)
        return y

    @staticmethod
    def _ResNetConnectedModule(x, filters, n_classes, name):
        return tf_layers.connectedModule(x, [filters], n_classes, name, reduce2D=True)


class TensorFlowResNet(TensorFlowArchitecture):

    _layer_depths = {
        "18": [2, 2, 2, 2],
        "34": [3, 4, 6, 3],
        "50": [3, 4, 6, 3],
        "101": [3, 4, 23, 3],
        "152": [3, 8, 36, 3],
    }

    _layer_features = [64, 128, 256, 512]

    _use_bottleneck = {
        "18": False,
        "34": False,
        "50": True,
        "101": True,
        "152": True,
    }

    def featureNetwork(self, inputs, is_training, scale64=1, layers="18"):
        use_bottleneck = self._use_bottleneck[layers]
        layer_depths = self._layer_depths[layers]

        # Because ResNet adds rather than concats, as feature numbers change, a 1x1 Conv is needed to upsample the
        # number of features. This happens across layer changes.
        x = ResNetBuilder._ResNetStemModule(inputs, 64*scale64, is_training, "ResNet_Conv1")
        for layer_i, layer in enumerate(layer_depths):
            filters = self._layer_features[layer_i] * scale64
            for block_i in range(layer_depths[layer_i]):
                name = "ResNet_Conv{}_Block{}".format(layer_i+2, block_i+1)
                if use_bottleneck:
                    conv1x1 = (block_i == 0)
                    x = ResNetBuilder._ResNetBottleneckBlock(x, filters, 3, 3, is_training, name, conv1x1=conv1x1)
                else:
                    conv1x1 = (block_i == 0 and layer_i != 0)
                    x = ResNetBuilder._ResNetBuildingBlock(x, filters, 3, 3, is_training, name, conv1x1=conv1x1)
            x = tf.layers.max_pooling2d(inputs=x, pool_size=(2, 2), strides=2)
        return x

    def build(self, image_size, n_classes, keep_prob=1.0, scale64=1, layers="18"):
        inputs = tf.placeholder(tf.float32, [None, image_size[0], image_size[1], image_size[2]])
        labels = tf.placeholder(tf.float32, [None, n_classes])
        is_training = tf.placeholder(tf.bool) # This is a dummy variable

        # Because Dropout have different behavior at training and prediction time, we
        # need to create 2 distinct computation graphs that still share the same weights.
        with tf.variable_scope("ResNetModel", reuse=tf.AUTO_REUSE):
            x = self.featureNetwork(inputs, is_training=True, scale64=scale64, layers=layers)
            logits_train = ResNetBuilder._ResNetConnectedModule(x, 1024, n_classes, name="ResNet_FC")
            x = self.featureNetwork(inputs, is_training=False, scale64=scale64, layers=layers)
            logits_test = ResNetBuilder._ResNetConnectedModule(x, 1024, n_classes, name="ResNet_FC")

        # These use test logits
        probabilities = tf.nn.softmax(logits_test)

        # These use train logits
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=logits_train, labels=labels))
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            train_step = tf.train.AdamOptimizer().minimize(loss)

        # Add our TensorBoard summaries
        tf.summary.scalar('loss', loss)
        tf_summaries.top_k_summaries(labels, logits_train, n_classes)
        summaries = tf.summary.merge_all()

        ops = dict(
            inputs=inputs,
            is_training=is_training,
            summaries=summaries,
            labels=labels,
            logits_train=logits_train,
            logits_test=logits_test,
            probabilities=probabilities,
            loss=loss,
            train_step=train_step
        )
        self._operators = ops
        return self
TensorFlowArchitecture.register(TensorFlowResNet)
