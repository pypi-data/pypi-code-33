import tensorflow as tf
from aether.libraries.contrib.nn.tf_summaries import tf_summaries

class tf_layers(object):

    @staticmethod
    def connectedModule(x, filters_arr, n_classes, name, reduce2D=True):
        with tf.variable_scope(name):
            # Classification block
            if reduce2D:
                x = tf.reduce_mean(x, axis=(1,2))
            for filters in filters_arr:
                x = tf.layers.dense(inputs=x, units=filters, activation=tf.nn.relu)
            x = tf.layers.dense(inputs=x, units=n_classes)
        return x

    @staticmethod
    def simpleClassifier(logits, labels, n_classes, update_ops=None):
        probabilities = tf.nn.softmax(logits)
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=logits, labels=labels))

        if update_ops is not None:
            with tf.control_dependencies(update_ops):
                train_step = tf.train.AdamOptimizer().minimize(loss)
        else:
            train_step = tf.train.AdamOptimizer().minimize(loss)

        # Add our TensorBoard summaries
        tf.summary.scalar('loss', loss)
        tf_summaries.top_k_summaries(labels, logits, n_classes)

        ops = dict(
            labels=labels,
            logits=logits,
            probabilities=probabilities,
            loss=loss,
            train_step=train_step
        )
        return ops
