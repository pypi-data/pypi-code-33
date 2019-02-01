# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np


def model_fn(features, labels, mode):
    feature = features["x"]
    result = {"y": feature * 2}
    with tf.name_scope("dummy_train"):
        dummy_train_variable = tf.get_variable("dummy", [])
        if mode == tf.estimator.ModeKeys.TRAIN:
            loss_op = tf.losses.absolute_difference(dummy_train_variable, features['x'][0])
            optimizer = tf.train.GradientDescentOptimizer(0.1)
            train_op = optimizer.minimize(loss_op, global_step=tf.train.get_global_step())

            return tf.estimator.EstimatorSpec(mode, train_op=train_op, loss=loss_op)
        else:
            return tf.estimator.EstimatorSpec(mode=mode, predictions=result, export_outputs={"serving_default": tf.estimator.export.PredictOutput(result)})


def serving_input_receiver_fn():
    x = tf.placeholder(dtype=tf.float32, shape=(None), name="x")
    features = {'x': x}
    receiver_tensors = {'x': x}

    return tf.estimator.export.ServingInputReceiver(features, receiver_tensors)


from modelhub.framework import TFApiModel


class Model(TFApiModel):
    INPUTS_SAMPLE = {"x": 1}
    OUTPUTS_SAMPLE = {"y": 2.}
    model_name = "watch_dog"
    model_version = 2


if __name__ == '__main__':
    estimator = tf.estimator.Estimator(model_fn=model_fn, model_dir='watch_dog_model')
    train_input_fn = tf.estimator.inputs.numpy_input_fn(x={"x": np.array([1])}, num_epochs=None, shuffle=False)
    estimator.train(train_input_fn, max_steps=1)
    estimator.export_savedmodel('watch_dog_model', serving_input_receiver_fn)
