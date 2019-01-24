import tensorflow as tf
from ..model import Experiment, Architecture
from ..dataset import Datasets


class MNISTCNNExperiment(Experiment):
    def __init__(self):
        self.model = MNISTCNN()
        super().__init__()

    def main_train(self):
        (x_train, y_train), (x_test, y_test) = Datasets.mnist(shape=[28, 28, 1])
        batch_size = 128

        x = tf.placeholder(tf.float32, [None, 28, 28, 1])
        y = tf.placeholder(tf.float32, [None, 10])
        is_training = tf.placeholder(tf.bool, [])
        lr = tf.placeholder(tf.float32, [])

        network = self.model(x)
        probs, logits = network.outputs
        loss = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits)
        accuracy = self.accuracy(y, probs)
        train_op = tf.train.AdamOptimizer().minimize(loss)

        with tf.Session(config=self.sess_config) as sess:
            sess.run(tf.global_variables_initializer())

            for i_epoch in range(10):
                self.train_epoch(sess, x_train, y_train, i_epoch, batch_size,
                                 train_op, loss, accuracy, x, y, is_training, lr)
                self.evaluate(sess, x_test, y_test, 256, loss, accuracy,
                              x, y, is_training)

            self.model.save(sess)

    def main_test(self):
        _, (x_test, y_test) = Datasets().get_mnist(shape=[28, 28, 1])

        x = tf.placeholder(tf.float32, [None, 28, 28, 1])
        y = tf.placeholder(tf.float32, [None, 10])
        is_training = tf.placeholder(tf.bool, [])

        network = self.model(x)
        probs, logits = network.outputs
        loss = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits)
        accuracy = self.accuracy(y, probs)

        with tf.Session(config=self.sess_config) as sess:
            self.model.load(sess)
            self.evaluate(sess, x_test, y_test, 256, loss, accuracy,
                          x, y, is_training)


class MNISTCNN(Architecture):
    def __init__(self):
        super().__init__(model_fn=self.C)

    def C(self, x, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            h = x

            self.register_layer(h, layer_name='input')

            with tf.variable_scope('layer1'):
                h = tf.contrib.layers.conv2d(h, 8, 3)
                h = tf.contrib.layers.max_pool2d(h, (2, 2))

                self.register_layer(h, layer_name='layer1')

            with tf.variable_scope('layer2'):
                h = tf.contrib.layers.conv2d(h, 16, 3)
                h = tf.contrib.layers.max_pool2d(h, (2, 2))

                self.register_layer(h, layer_name='layer2')

            with tf.variable_scope('layer3'):
                h = tf.contrib.layers.conv2d(h, 16, 3)
                h = tf.contrib.layers.max_pool2d(h, (2, 2))

                self.register_layer(h, layer_name='layer3')

            with tf.variable_scope('layer4'):
                h = tf.contrib.layers.flatten(h)
                h = tf.contrib.layers.fully_connected(h, 128)

                self.register_layer(h, layer_name='layer4')

            with tf.variable_scope('layer5'):
                logits = tf.contrib.layers.fully_connected(h, 10, activation_fn=None)
                output = tf.nn.softmax(logits)

                self.register_layer(logits, layer_name='logits')
                self.register_layer(output, layer_name='output')

                return output, logits
