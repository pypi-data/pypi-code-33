import tensorflow as tf
from aether.libraries.contrib.nn.tf_layers import tf_layers
from aether.libraries.contrib.nn.learning import TensorFlowArchitecture, TensorFlowModel


class TensorFlowStackNet(TensorFlowArchitecture):

    def build(self, image_size, n_inputs, n_classes, featureLambda, scale64=1):
        inputs = tf.placeholder(tf.float32, [None, n_inputs, image_size[0], image_size[1], image_size[2]])
        labels = tf.placeholder(tf.float32, [None, n_classes])
        is_training = tf.placeholder(tf.bool)

        with tf.variable_scope("SiameseFeatures", reuse=tf.AUTO_REUSE):
            features = [featureLambda(inputs[:,input_i], is_training) for input_i in range(n_inputs)]
            x = tf.concat(features, axis=-1)

        logits = tf_layers.connectedModule(x, [1024*scale64, 1024*scale64], n_classes, "ConnectedModule", reduce2D=True)
        ops = tf_layers.simpleClassifier(logits, labels, n_classes)
        summaries = tf.summary.merge_all()
        ops.update(dict(
            inputs=inputs,
            is_training=is_training,
            summaries=summaries,
        ))

        self._operators = ops
        return self
TensorFlowArchitecture.register(TensorFlowStackNet)
