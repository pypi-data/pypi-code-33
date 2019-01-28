#!/usr/bin/env python
'''
component
Created by Seria at 25/11/2018 2:58 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-

from functools import partial
import tensorflow as tf
from copy import deepcopy
import os
from ..toolkit.utility import recordConfig

class Pod:
    def __init__(self, comp, symbol, name, msg=[]):
        self.component = comp
        self.symbol = symbol
        self.message = msg
        self.name = name

    def __rshift__(self, other):
        return Pod([self, other], '>', 'CASCADE')

    def __add__(self, other):
        return Pod([self, other], '+', 'ADD')

    def __sub__(self, other):
        return Pod([self, other], '-', 'SUB')

    def __mul__(self, other):
        return Pod([self, other], '*', 'MUL')

    def __matmul__(self, other):
        return Pod([self, other], '@', 'MATMUL')

    def __and__(self, other):
        return Pod([self, other], '&', 'CONCAT')

    def __pow__(self, power, modulo=None):
        assert isinstance(power, int)
        pod = deepcopy(self)
        pod._appendSerialNo('0')
        for p in range(1, power):
            pod_temp = deepcopy(self)
            pod_temp._appendSerialNo(str(p))
            pod = pod >> pod_temp
        return pod

    def _appendSerialNo(self, serial_no):
        if isinstance(self.component, list):
            self.component[0]._appendSerialNo(serial_no)
            self.component[1]._appendSerialNo(serial_no)
        else:
            self.name += '_' + serial_no

    def show(self):
        if isinstance(self.component, list):
            self.component[0].show()
            self.component[1].show()
        else:
            print(self.name)



class Component(object):
    def __init__(self):
        self.warehouse = ['CONV_1D', 'CONV', 'CONV_3D', 'CONV_TRANS', 'CONV_SEP', 'CONV_ATROUS',
                          'SIGMOID', 'TANH', 'SOFTMAX', 'RELU', 'RELU_LEAKY', 'RELU_EXP',
                          'MAX_POOL', 'AVG_POOL',
                          'DROPOUT', 'BATCH_NORM', 'EMBEDDING',
                          'RESHAPE', 'FLAT', 'SLICE',
                          'CLIP', 'DENSE',
                          'RESIZE',
                          'DUPLICATE', 'CONVERT',
                          'WEIGHT_DECAY', 'SIGM_XENTROPY', 'SFTM_XENTROPY', 'MSE', 'MAE',
                          'MOMENTUM', 'NESTEROV', 'ADAM']
        # Convolution
        self.CONV_1D = 0
        self.CONV = self.conv_2d
        self.CONV_3D = 2
        self.CONV_TRANS = 3
        self.CONV_SEP = 4
        self.CONV_ATROUS = 5
        # Activation
        self.SIGMOID = self.sigmoid
        self.TANH = self.tanh
        self.SOFTMAX = self.softmax
        self.RELU = self.relu
        self.RELU_LEAKY = self.relu_leaky
        self.RELU_EXP = 15
        # Pooling
        self.MAX_POOL = self.max_pool_2d
        self.AVG_POOL = self.avg_pool_2d
        # Distributing
        self.DROPOUT = self.dropout
        self.BATCH_NORM = self.batch_norm
        self.EMBEDDING = self.embedding
        # Reshape
        self.RESHAPE = self.reshape
        self.FLAT = self.flat
        self.SLICE = self.slice
        self.PAD = self.pad
        # Arithmetic
        self.CLIP = self.clip
        self.DENSE = self.dense
        self.ARGMAX = self.argmax
        # Image Manipulation
        self.RESIZE = self.resize
        # Copy or Rename
        self.DUPLICATE = self.duplicate
        self.CONVERT = self.convert
        # Loss
        self.WEIGHT_DECAY = self.weight_decay
        self.SIGM_XENTROPY = self.sigm_xentropy
        self.SFTM_XENTROPY = self.sftm_xentropy
        self.MSE = self.mse
        self.MAE = self.mae
        # Optimizer
        self.MOMENTUM = self.momentum
        self.NESTEROV = self.nesterov
        self.ADAM = self.adam
        # Metric
        self.ACC_CLS = self.accuracy_cls



    def addComp(self, name, comp, is_complete=False):
        name = name.upper()
        if name in self.warehouse:
            raise Exception('%s is an existing component in warehouse.' % name)
        if is_complete:
            def customizedComp(name):
                return Pod(partial(comp.component, name=name), comp.symbol, name, comp.message)
        else:
            assert not isinstance(comp.component, list)
            def customizedComp(**kwargs):
                symbol = kwargs.get(comp.symbol[1:], comp.symbol)
                return Pod(partial(comp.component, **kwargs), symbol, kwargs['name'], comp.message)
        exec('self.%s = customizedComp' % name)

    # ------------------------------------ Convolution ------------------------------------ #

    def _createVar(self, name, shape, initializer, param, regularizer=None):
        init_err = Exception('%s initializer is not defined or supported.' % initializer)
        # with tf.device('/gpu:0'):
        if initializer == 'xavier':
            if param is None:
                param = False
            var = tf.get_variable(name, shape, initializer=tf.contrib.layers.xavier_initializer(uniform=param))
        elif initializer == 'trunc_norm':
            if param is None:
                param = [0, 0.1]
            var = tf.get_variable(name, shape,
                                  initializer=tf.truncated_normal_initializer(mean=param[0], stddev=param[1]))
        elif initializer == 'rand_norm':
            if param is None:
                param = [0, 0.1]
            var = tf.get_variable(name,
                                  initializer=tf.random_normal(shape, mean=param[0], stddev=param[1]))
        elif initializer == 'zero':
            var = tf.get_variable(name, shape, initializer=tf.zeros_initializer())
        elif initializer == 'one':
            var = tf.get_variable(name, shape, initializer=tf.ones_initializer())
        else:
            raise init_err

        if regularizer == 'l2':
            weight_decay = tf.nn.l2_loss(var, name=name+'/regularizer')
            tf.add_to_collection(tf.GraphKeys.REGULARIZATION_LOSSES, weight_decay)
        elif regularizer is None:
            pass
        else:
            raise Exception('%s regularizer is not defined or supported.' % regularizer)

        return var

    def conv_2d(self, **kwargs):
        if 'input' in kwargs.keys():
            symbol = kwargs['input']
        else:
            symbol = '.input'
        return Pod(partial(self._conv_2d, **kwargs), symbol, kwargs['name'])
    def _conv_2d(self, name, input, kernel, out_chs, w_init='xavier', w_param=None,
                 b_init=None, b_param=None, w_reg='l2', b_reg='l2', stride=(1, 1), padding='same'):
        padding = padding.upper()
        in_chs = int(input.get_shape()[-1])
        in_out_chs = [in_chs, out_chs]
        w = self._createVar(name+'_w', kernel + in_out_chs, w_init, w_param, w_reg)
        if b_init:
            b = self._createVar(name+'_b', [in_out_chs[-1]], b_init, b_param, b_reg)
            return tf.nn.bias_add(tf.nn.conv2d(input, w, [1, stride[0], stride[1], 1], padding), b, name=name)
        else:
            return tf.nn.conv2d(input, w, [1, stride[0], stride[1], 1], padding, name=name)

    # ------------------------------------ Activation ------------------------------------ #

    def sigmoid(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._sigmoid, **kwargs), symbol, kwargs['name'])
    def _sigmoid(self, name, input):
        return tf.nn.sigmoid(input, name)

    def tanh(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._tanh, **kwargs), symbol, kwargs['name'])
    def _tanh(self, name, input):
        return tf.nn.tanh(input, name)

    def softmax(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._tanh, **kwargs), symbol, kwargs['name'])
    def _softmax(self, name, input):
        return tf.nn.softmax(input, name)

    def relu(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._relu, **kwargs), symbol, kwargs['name'])
    def _relu(self, name, input):
        return tf.nn.relu(input, name)

    def relu_leaky(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._relu_leaky, **kwargs), symbol, kwargs['name'])
    def _relu_leaky(self, name, input):
        return tf.nn.leaky_relu(input, name)

    # ------------------------------------ Distributing ------------------------------------ #

    def dropout(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._dropout, **kwargs), symbol, kwargs['name'])
    def _dropout(self, name, input, p_drop):
        return tf.identity(tf.nn.dropout(input, 1-p_drop), name=name)

    def batch_norm(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._batch_norm, **kwargs), symbol, kwargs['name'])
    def _batch_norm(self, name, input, is_train, beta=False, gamma=False):
        return tf.layers.batch_normalization(input, training=is_train, center=beta, scale=gamma, name=name)

    def embedding(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._embedding, **kwargs), symbol, kwargs['name'])
    def _embedding(self, name, input, vocabulary, vec_dims, w_init='xavier', w_param=None):
        embd_vec = self._createVar(name+'_vec', [vocabulary, vec_dims], w_init, w_param)
        return tf.nn.embedding_lookup(embd_vec, input, name=name)

    # ------------------------------------ Pooling ------------------------------------ #

    def max_pool_2d(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._max_pool_2d, **kwargs), symbol, kwargs['name'])
    def _max_pool_2d(self, name, input, kernel=(2, 2), stride=(2, 2), padding='same', if_global=False):
        padding = padding.upper()
        if if_global:
            in_shape = input.get_shape()
            kernel = (int(in_shape[-3], int(in_shape[-2])))
        return tf.nn.max_pool(input,
                              [1, kernel[0], kernel[1], 1],
                              [1, stride[0], stride[1], 1],
                              padding, name=name)

    def avg_pool_2d(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._avg_pool_2d, **kwargs), symbol, kwargs['name'])
    def _avg_pool_2d(self, name, input, kernel=(2, 2), stride=(2, 2), padding='same', if_global=False):
        padding = padding.upper()
        if if_global:
            in_shape = input.get_shape()
            kernel = (int(in_shape[-3]), int(in_shape[-2]))
        return tf.nn.avg_pool(input,
                              [1, kernel[0], kernel[1], 1],
                              [1, stride[0], stride[1], 1],
                              padding, name=name)

    # ------------------------------------ Reshape ------------------------------------ #

    def reshape(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._reshape, **kwargs), symbol, kwargs['name'])
    def _reshape(self, name, input, shape):
        return tf.reshape(input, shape, name)

    def flat(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._flat, **kwargs), symbol, kwargs['name'])
    def _flat(self, name, input):
        return tf.layers.flatten(input, name=name)

    def slice(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._slice, **kwargs), symbol, kwargs['name'])
    def _slice(self, name, input, indices):
        for d in range(len(indices)):
            output = input[indices[d][0]:indices[d][1]]
        return tf.identity(output, name)

    def pad(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._pad, **kwargs), symbol, kwargs['name'])
    def _pad(self, name, input, margin, fill_in=0):
        return tf.pad(input, margin, constant_values=fill_in, name=name)

    # -------------------------------------- Arithmetic -------------------------------------- #

    def clip(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._clip, **kwargs), symbol, kwargs['name'])
    def _clip(self, name, input, min_max_vals):
        return tf.clip_by_value(input, min_max_vals[0], min_max_vals[1], name)

    def dense(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._dense, **kwargs), symbol, kwargs['name'])
    def _dense(self, name, input, out_chs, w_init='xavier', w_param=None,
               b_init='zero', b_param=None, w_reg='l2', b_reg='l2'):
        in_chs = int(input.get_shape()[-1])
        in_out_chs = [in_chs, out_chs]
        w = self._createVar(name + '_w', in_out_chs, w_init, w_param, w_reg)
        if b_init:
            b = self._createVar(name + '_b', [in_out_chs[-1]], b_init, b_param, b_reg)
            return tf.nn.bias_add(tf.matmul(input, w), b, name=name)
        else:
            return tf.matmul(input, w, name=name)

    def argmax(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._argmax, **kwargs), symbol, kwargs['name'])
    def _argmax(self, name, input, axis):
        return tf.argmax(input, axis, name=name)

    # ------------------------------------ Image Manipulation ------------------------------------ #

    def resize(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._resize, **kwargs), symbol, kwargs['name'])
    def _resize(self, name, input, size, method='bilinear'):
        if method == 'bilinear':
            return tf.image.resize_bilinear(input, size, name=name)
        elif method == 'bicubic':
            return tf.image.resize_bicubic(input, size, name=name)
        elif method == 'crop':
            return tf.image.resize_image_with_crop_or_pad(input, size, name=name)
        else:
            raise KeyError('%s is not a legal resize method.' % method)


    # ------------------------------------ Redefine or Rename ------------------------------------ #

    def duplicate(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._duplicate, **kwargs), symbol, kwargs['name'])
    def _duplicate(self, name, input):
        return tf.identity(input, name)

    def convert(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._convert, **kwargs), symbol, kwargs['name'])
    def _convert(self, name, input, dtype, trainable=False):
        '''
        convert data type or convert list/numpy array to tensor
        :param name:
        :param input: input tensor / list / numpy array
        :param dtype:
        :param trainable: if tensor is trainable
        :return: tensor
        '''
        if isinstance(input, (tf.Tensor, tf.SparseTensor, tf.Variable)):
            return tf.cast(input, tf.as_dtype(dtype), name=name)
        else:
            return tf.Variable(input, trainable=trainable, name=name)

    # ------------------------------------ Loss ------------------------------------ #

    def weight_decay(self, **kwargs):
        if 'penalty' in kwargs.keys():
            message = [kwargs['penalty']]
        else:
            message = []
        return Pod(partial(self._weight_decay, **kwargs), '.penalty', kwargs['name'], message)
    def _weight_decay(self, name, penalty, decay_scope=None):
        if decay_scope is None:
            return tf.multiply(tf.add_n(tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)),
                               penalty, name=name)
        else:
            return tf.multiply(tf.add_n(tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES, scope=decay_scope)),
                               penalty, name=name)

    def sigm_xentropy(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._sigm_xentropy, **kwargs), symbol, kwargs['name'], [kwargs['label']])
    def _sigm_xentropy(self, name, input, label):
        labels = tf.cast(label, tf.float32)
        return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=label, logits=input, name=name))

    def sftm_xentropy(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._sftm_xentropy, **kwargs), symbol, kwargs['name'], [kwargs['label']])
    def _sftm_xentropy(self, name, input, label, is_one_hot):
        if is_one_hot:
            labels = tf.cast(label, tf.float32)
            return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=input, name=name))
        else:
            return tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
                                        labels=label, logits= input, name=name))

    def mse(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._mse, **kwargs), symbol, kwargs['name'], [kwargs['label']])
    def _mse(self, name, input, label):
        return tf.reduce_mean(tf.squared_difference(input, label), name=name)

    def mae(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._mae, **kwargs), symbol, kwargs['name'], [kwargs['label']])
    def _mae(self, name, input, label):
        return tf.reduce_mean(tf.abs(input-label), name=name)

    # ------------------------------------ Optimizer ------------------------------------ #

    def _lrStrategy(self, mile_meter, lr, lr_decay, miles, param):
        if lr_decay == 'exp':
            return tf.train.exponential_decay(lr, mile_meter, miles, param, staircase=False)
        elif lr_decay == 'exp_stair':
            return tf.train.exponential_decay(lr, mile_meter, miles, param, staircase=True)
        elif lr_decay == 'poly':
            return tf.train.polynomial_decay(lr, mile_meter, miles, power=param, cycle=False)
        elif lr_decay == 'poly_cycle':
            return tf.train.polynomial_decay(lr, mile_meter, miles, power=param, cycle=True)
        elif lr_decay == 'stair':
            return tf.train.piecewise_constant(mile_meter, [i*param for i in range(1, len(lr))], lr)
        else:
            raise KeyError('%s decay is not supported or defined.' % lr_decay)

    def _computeGrad(self, optz, cost, update_scope, ignore_name, grad_limit):
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            if update_scope is None:
                tr_var = tf.trainable_variables()
            else:
                tr_var = tf.trainable_variables(scope=update_scope)
            if not ignore_name is None:
                update_var = []
                for tv in tr_var:
                    flag_ignore = False
                    for ig in ignore_name:
                        if ig in tv.op.name:
                            flag_ignore = True
                            break
                    if not flag_ignore:
                        update_var.append(tv)
            else:
                update_var = tr_var
            grad_var_pairs = optz.compute_gradients(cost, var_list=update_var)

            if grad_limit is None:
                return grad_var_pairs
            else:
                return [(tf.clip_by_value(grad, -grad_limit, grad_limit), var) for grad, var in grad_var_pairs]

    def momentum(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._momentum, **kwargs), symbol, kwargs['name'])
    def _momentum(self, name, input, mile_meter, lr, mmnt=0.9, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None):
        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt': mmnt, 'update_scope': update_scope, 'ignore_name': ignore_name,
                      'lr_decay': lr_decay, 'lr_miles': lr_miles, 'decay_param': decay_param, 'grad_limit': grad_limit})
        if isinstance(lr_decay, str):
            lr = self._lrStrategy(mile_meter, lr, lr_decay, lr_miles, decay_param)
        optz = tf.train.MomentumOptimizer(lr, mmnt)
        grad = self._computeGrad(optz, input, update_scope, ignore_name, grad_limit)
        train_op = optz.apply_gradients(grad, mile_meter, name=name)
        return train_op

    def nesterov(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._nesterov, **kwargs), symbol, kwargs['name'])
    def _nesterov(self, name, input, mile_meter, lr, mmnt=0.9, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None):
        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt': mmnt, 'update_scope': update_scope, 'ignore_name': ignore_name,
                      'lr_decay': lr_decay, 'lr_miles': lr_miles, 'decay_param': decay_param, 'grad_limit': grad_limit})
        if isinstance(lr_decay, str):
            lr = self._lrStrategy(mile_meter, lr, lr_decay, lr_miles, decay_param)
        optz = tf.train.MomentumOptimizer(lr, mmnt, use_nesterov=True)
        grad = self._computeGrad(optz, input, update_scope, ignore_name, grad_limit)
        train_op = optz.apply_gradients(grad, mile_meter, name=name)
        return train_op

    def adam(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._adam, **kwargs), symbol, kwargs['name'])
    def _adam(self, name, input, mile_meter, lr, mmnt1=0.9, mmnt2=0.999, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None):
        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt1': mmnt1, 'mmnt2': mmnt2, 'update_scope': update_scope,
                      'ignore_name': ignore_name, 'lr_decay': lr_decay, 'lr_miles': lr_miles,
                      'decay_param': decay_param, 'grad_limit': grad_limit})
        if isinstance(lr_decay, str):
            lr = self._lrStrategy(mile_meter, lr, lr_decay, lr_miles, decay_param)
        optz = tf.train.AdamOptimizer(lr, beta1=mmnt1, beta2=mmnt2)
        grad = self._computeGrad(optz, input, update_scope, ignore_name, grad_limit)
        train_op = optz.apply_gradients(grad, mile_meter, name=name)
        return train_op

    # ------------------------------------ Metric ------------------------------------ #

    def accuracy_cls(self, **kwargs):
        symbol = kwargs.get('input', '.input')
        return Pod(partial(self._accuracy_cls, **kwargs), symbol, kwargs['name'], [kwargs['label']])
    def _accuracy_cls(self, name, input, label, multi_class, is_one_hot=False):
        if multi_class:
            assert not is_one_hot
            pred = tf.cast(tf.round(input), label.dtype)
            correct = tf.reduce_all(tf.equal(pred, label), axis=-1)
            return tf.reduce_mean(tf.cast(correct, tf.float32), name=name)
        else:
            if is_one_hot:
                label = tf.argmax(label, axis=-1)
            pred = tf.argmax(input, axis=-1)
            correct = tf.equal(pred, label)
            return tf.reduce_mean(tf.cast(correct, tf.float32), name=name)