import tensorflow as tf


def accuracy(labels, preds):
    return tf.reduce_mean(
        tf.cast(tf.equal(
            tf.cast(tf.argmax(preds, axis=1), tf.int32),
            tf.cast(tf.argmax(labels, axis=1), tf.int32)
        ), tf.float32)
    )
