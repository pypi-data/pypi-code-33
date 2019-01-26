import tensorflow as tf
import numpy as np
import random

eps = 1e-10


def optimize(loss, step_size, var_scope=None, optimizer='adam', regularizer=('l2', 0.0), global_step=None,
             beta1=0.9, momentum=0.9):
    var_list = tf.trainable_variables(var_scope)
    if regularizer[0] == 'l1':
        regularizer = tf.contrib.layers.l1_regularizer(
            scale=regularizer[1], scope=None
        )
    elif regularizer[0] == 'l2':
        regularizer = tf.contrib.layers.l2_regularizer(
            scale=regularizer[1], scope=None
        )
    regularization_penalty = tf.contrib.layers.apply_regularization(regularizer, var_list)
    total_loss = loss + regularization_penalty
    with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
        if optimizer == 'adam':
            return tf.train.AdamOptimizer(step_size, beta1=beta1).minimize(total_loss,
                                                                           var_list=var_list,
                                                                           global_step=global_step)
        elif optimizer == 'momentum':
            return tf.train.MomentumOptimizer(step_size, momentum=momentum).minimize(total_loss,
                                                                                     var_list=var_list,
                                                                                     global_step=global_step)
        elif optimizer == 'sgd':
            return tf.train.GradientDescentOptimizer(step_size).minimize(total_loss,
                                                                         var_list=var_list,
                                                                         global_step=global_step)
        else:
            raise Exception('Undefined optimization method')


def loss_fn(outputs, labels, obj_type='cross_entropy'):
    if obj_type == 'cross_entropy':
        if tf.shape(labels)[-1] == 1:
            loss = - (labels * tf.log(outputs + eps) + (1 - labels) * tf.log(1 - outputs + eps))
        else:
            loss = - labels * tf.log(outputs + eps)
    elif obj_type == 'mse':
        loss = tf.square(outputs - labels)
    else:
        raise Exception('Undefined loss function')
    return tf.reduce_mean(tf.reduce_sum(loss, axis=-1))


