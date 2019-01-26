from yfml.layers import *
from yfml.utils import *


def stack(name, inputs, shapes, type='fully_connected', activation_fn='relu',
          last_activation_fn=None,
          use_batch_norm=False, if_training=False,
          kernel_init=normal_init, use_bias=True, reuse=False,
          use_dropout=False, dropout_rate=0.1,
          kernel_size=5, strides=1, padding='SAME', data_format='channels_last', dense_connect=False):
    layers_num = len(shapes)
    outputs = inputs
    with tf.variable_scope(name, reuse=reuse):
        for ly_num in range(1, layers_num + 1):
            if ly_num == layers_num:
                act_fn = last_activation_fn
            else:
                act_fn = activation_fn

            if type == 'fully_connected' or type == 'fc':
                outputs_ = fully_connected('fc_%i'%ly_num, outputs, shapes[ly_num-1], activation_fn=act_fn,
                                          use_batch_norm=use_batch_norm, if_training=if_training,
                                          use_dropout=use_dropout, dropout_rate=dropout_rate,
                                          kernel_init=kernel_init, use_bias=use_bias, reuse=reuse)
            elif type == 'convolution_2d' or type == 'conv2d':
                outputs_ = conv2d('conv2d_%i'%ly_num, outputs, shapes[ly_num-1], kernel_size=kernel_size, strides=strides,
                                 activation_fn=act_fn, padding=padding,
                                 use_batch_norm=use_batch_norm, if_training=False,
                                 use_dropout=use_dropout, dropout_rate=dropout_rate,
                                 kernel_init=kernel_init, use_bias=use_bias, reuse=reuse, data_format=data_format)
            elif type == 'convolution_3d' or type == 'conv3d':
                outputs_ = conv3d('conv3d_%i'%ly_num, outputs, shapes[ly_num-1], kernel_size=kernel_size, strides=strides,
                                 activation_fn=act_fn, padding=padding,
                                 use_batch_norm=use_batch_norm, if_training=False,
                                 use_dropout=use_dropout, dropout_rate=dropout_rate,
                                 kernel_init=kernel_init, use_bias=use_bias, reuse=reuse, data_format=data_format)
            else:
                raise Exception('Undefined layer type in stack')

            if dense_connect:
                outputs = tf.concat([outputs, outputs_], axis=-1)
            else:
                outputs = outputs_
        return outputs


def mix_stack(name, inputs, types, shapes, activation_fn='relu',
              last_activation_fn=None,
              use_batch_norm=False, if_training=False,
              kernel_init=normal_init, use_bias=True, reuse=False,
              use_dropout=False, dropout_rate=0.1,
              kernel_size=5, strides=1, padding='SAME', data_format='channels_last'
              ):
    layers_num = len(shapes)
    outputs = inputs
    with tf.variable_scope(name, reuse=reuse):
        if len(types) == layers_num:
            for ly_num in range(1, layers_num+1):
                if ly_num == layers_num:
                    act_fn = last_activation_fn
                else:
                    act_fn = activation_fn

                if types[ly_num-1] == 'fully_connected' or types[ly_num-1] == 'fc':
                    outputs = flatten(outputs)
                    outputs = fully_connected('fc_%i' % ly_num, outputs, shapes[ly_num - 1],
                                              activation_fn=act_fn,
                                              use_batch_norm=use_batch_norm, if_training=if_training,
                                              use_dropout=use_dropout, dropout_rate=dropout_rate,
                                              kernel_init=kernel_init, use_bias=use_bias, reuse=reuse)
                elif types[ly_num-1] == 'convolution_2d' or types[ly_num-1] == 'conv2d':
                    outputs = conv2d('conv2d_%i' % ly_num, outputs, shapes[ly_num - 1], kernel_size=kernel_size,
                                     strides=strides,
                                     activation_fn=act_fn, padding=padding,
                                     use_batch_norm=use_batch_norm, if_training=False,
                                     use_dropout=use_dropout, dropout_rate=dropout_rate,
                                     kernel_init=kernel_init, use_bias=use_bias, reuse=reuse, data_format=data_format)
                elif types[ly_num-1] == 'convolution_3d' or types[ly_num-1] == 'conv3d':
                    outputs = conv3d('conv3d_%i' % ly_num, outputs, shapes[ly_num - 1], kernel_size=kernel_size,
                                     strides=strides,
                                     activation_fn=act_fn, padding=padding,
                                     use_batch_norm=use_batch_norm, if_training=False,
                                     use_dropout=use_dropout, dropout_rate=dropout_rate,
                                     kernel_init=kernel_init, use_bias=use_bias, reuse=reuse, data_format=data_format)
                elif types[ly_num-1][-6:] == 'pool2d':
                    outputs = pooling2d(types[ly_num-1] + '_%i' % ly_num, outputs, shapes[ly_num - 1], strides,
                                        pool_type=types[ly_num-1][:-6], padding=padding, data_format=data_format)
                elif types[ly_num - 1][-6:] == 'pool3d':
                    outputs = pooling3d(types[ly_num-1] + '_%i' % ly_num, outputs, shapes[ly_num - 1], strides,
                                        pool_type=types[ly_num - 1][:-6], padding=padding, data_format=data_format)
                elif types[ly_num - 1][-10:] == 'pooling_2d':
                    outputs = pooling2d(types[ly_num - 1] + '_%i' % ly_num, outputs, shapes[ly_num - 1], strides,
                                        pool_type=types[ly_num - 1][:-11], padding=padding, data_format=data_format)
                elif types[ly_num - 1][-10:] == 'pooling_3d':
                    outputs = pooling3d(types[ly_num - 1] + '_%i' % ly_num, outputs, shapes[ly_num - 1], strides,
                                        pool_type=types[ly_num - 1][:-11], padding=padding, data_format=data_format)
                else:
                    raise Exception('Undefined layer type in mix_stack')
            return outputs
        else:
            raise Exception('Please make sure every layer has its defined shape/unit num in mix_stack')
