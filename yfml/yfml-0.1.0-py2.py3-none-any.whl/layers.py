import tensorflow as tf
import numpy as np
import random


normal_init = tf.contrib.layers.variance_scaling_initializer(
    factor=2.0, mode='FAN_IN', uniform=False, seed=None, dtype=tf.float32
    )


xavier_init = tf.contrib.layers.xavier_initializer(
    uniform=True,
    seed=None,
    dtype=tf.float32
)


def batch_norm(name, if_training, input_tensor, reuse=False):
    with tf.variable_scope(name, reuse=reuse):
        return tf.layers.batch_normalization(input_tensor, momentum=0.9, epsilon=1e-5, training=if_training)


def non_linear_op(inputs, activation_fn='relu'):
    if activation_fn == 'relu':
        return tf.nn.relu(inputs)
    elif activation_fn == 'tanh':
        return tf.nn.tanh(inputs)
    elif activation_fn == 'softmax':
        return tf.nn.softmax(inputs)
    elif activation_fn == 'sigmoid':
        return tf.nn.sigmoid(inputs)
    elif activation_fn == None:
        return inputs
    else:
        raise Exception('Some error in activation function')


def fully_connected(name, inputs, output_dim, activation_fn='relu',
                    use_batch_norm=False, if_training=False,
                    use_dropout=False, dropout_rate=0.5,
                    kernel_init=normal_init, use_bias=True, reuse=False):
    with tf.variable_scope(name, reuse=reuse):
        activator = tf.layers.dense(inputs, output_dim,
                                    activation=None,
                                    use_bias=use_bias,
                                    kernel_initializer=kernel_init)
        if use_batch_norm:
            outputs = non_linear_op(batch_norm('bn', if_training, activator, reuse), activation_fn)
        else:
            outputs = non_linear_op(activator, activation_fn)
        if use_dropout:
            return tf.layers.dropout(outputs, rate=dropout_rate, training=if_training)
        else:
            return outputs


def conv2d(name, inputs, filters, kernel_size=5, strides=1,
           activation_fn='relu', padding='SAME',
           use_batch_norm=False, if_training=False,
           use_dropout=False, dropout_rate=0.1,
           kernel_init=normal_init, use_bias=True, reuse=False,
           data_format='channels_last', opt_order='conv_first'):  # opt_order='conv_last' is used in DenseNet
    with tf.variable_scope(name, reuse=reuse):
        if opt_order == 'conv_first':
            activator = tf.layers.conv2d(inputs, filters, kernel_size,
                                         strides=strides,
                                         padding=padding,
                                         activation=None,
                                         use_bias=use_bias,
                                         kernel_initializer=kernel_init,
                                         data_format=data_format)
            if use_batch_norm:
                outputs = non_linear_op(batch_norm('bn', if_training, activator, reuse), activation_fn)
            else:
                outputs = non_linear_op(activator, activation_fn)
            if use_dropout:
                return tf.layers.dropout(outputs, rate=dropout_rate, training=if_training)
            else:
                return outputs
        elif opt_order == 'conv_last':
            if use_batch_norm:
                outputs = non_linear_op(batch_norm('bn', if_training, inputs, reuse), activation_fn)
            else:
                outputs = non_linear_op(inputs, activation_fn)
            if use_dropout:
                outputs = tf.layers.dropout(outputs, rate=dropout_rate, training=if_training)
            else:
                outputs = outputs
            outputs = tf.layers.conv2d(outputs, filters, kernel_size,
                                       strides=strides,
                                       padding=padding,
                                       activation=None,
                                       use_bias=use_bias,
                                       kernel_initializer=kernel_init,
                                       data_format=data_format)
            return outputs

        else:
            raise Exception('opt_order can only be \'conv_last\' or \'conv_first\'')


def conv3d(name, inputs, filters, kernel_size=5, strides=1,
           activation_fn='relu', padding='SAME',
           use_batch_norm=False, if_training=False,
           use_dropout=False, dropout_rate=0.5,
           kernel_init=normal_init, use_bias=True, reuse=False,
           data_format='channels_last', opt_order='conv_first'):  # opt_order='conv_last' is used in DenseNet
    with tf.variable_scope(name, reuse=reuse):
        if opt_order == 'conv_first':
            activator = tf.layers.conv3d(inputs, filters, kernel_size,
                                         strides=strides,
                                         padding=padding,
                                         activation=None,
                                         use_bias=use_bias,
                                         kernel_initializer=kernel_init,
                                         data_format=data_format)
            if use_batch_norm:
                outputs = non_linear_op(batch_norm('bn', if_training, activator, reuse), activation_fn)
            else:
                outputs = non_linear_op(activator, activation_fn)
            if use_dropout:
                return tf.layers.dropout(outputs, rate=dropout_rate, training=if_training)
            else:
                return outputs
        elif opt_order == 'conv_last':
            if use_batch_norm:
                outputs = non_linear_op(batch_norm('bn', if_training, inputs, reuse), activation_fn)
            else:
                outputs = non_linear_op(inputs, activation_fn)
            if use_dropout:
                outputs = tf.layers.dropout(outputs, rate=dropout_rate, training=if_training)
            else:
                outputs = outputs
            outputs = tf.layers.conv3d(outputs, filters, kernel_size,
                                       strides=strides,
                                       padding=padding,
                                       activation=None,
                                       use_bias=use_bias,
                                       kernel_initializer=kernel_init,
                                       data_format=data_format)
            return outputs
        else:
            raise Exception('opt_order can only be \'conv_last\' or \'conv_first\'')


def pooling2d(name, inputs, pool_size, strides, pool_type='max', padding='SAME', data_format='channels_last'):
    if pool_type == 'max':
        return tf.layers.max_pooling2d(inputs, pool_size, strides,
                                       padding=padding, data_format=data_format, name=name)
    elif pool_type == 'avg':
        return tf.layers.average_pooling2d(inputs, pool_size, strides,
                                           padding=padding, data_format=data_format, name=name)
    elif pool_type == 'global':
        width = tf.shape(inputs)[1]
        height = tf.shape(inputs)[2]
        pool_size_ = [width, height]
        return pooling2d(name, inputs, pool_size_, strides=1, pool_type='avg', padding=padding, data_format=data_format)
    else:
        raise Exception('Undefined pooling type')


def pooling3d(name, inputs, pool_size, strides, pool_type='max', padding='SAME', data_format='channels_last'):
    if pool_type == 'max':
        return tf.layers.max_pooling3d(inputs, pool_size, strides,
                                       padding=padding, data_format=data_format, name=name)
    elif pool_type == 'avg':
        return tf.layers.average_pooling3d(inputs, pool_size, strides,
                                           padding=padding, data_format=data_format, name=name)
    elif pool_type == 'global':
        width = tf.shape(inputs)[1]
        height = tf.shape(inputs)[2]
        depth = tf.shape(inputs)[3]
        pool_size_ = [width, height, depth]
        return pooling2d(name, inputs, pool_size_, strides=1, pool_type='avg', padding=padding, data_format=data_format)
    else:
        raise Exception('Undefined pooling type')