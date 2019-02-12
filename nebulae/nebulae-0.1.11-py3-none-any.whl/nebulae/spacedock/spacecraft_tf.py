#!/usr/bin/env python
'''
space_craft_tf
Created by Seria at 03/02/2019 11:25 AM
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
import tensorflow as tf
import numpy as np
from .component import Pod


class SpaceCraftTF(object):
    def __init__(self, engine, blueprint, scope=''):
        assert '/' not in scope
        if scope:
            self.scope = scope + '/'
        else:
            self.scope = scope
        self.mile = tf.Variable(0, trainable=False)
        self.valid_dtypes = ['uint8', 'uint16', 'uint32', 'int8', 'int16', 'int32', 'int64',
                             'float16', 'float32', 'float64', 'str', 'bool']
        self.operands = {'+': tf.add, '-': tf.subtract, '*': tf.multiply, '@': tf.matmul, '&': tf.concat}
        self.operands_counter = {'+': 0, '-': 0, '*': 0, '@': 0, '&': 0}
        self.layout = {}
        self.engine = engine
        self.blueprint = blueprint

    def fuelLine(self, name, shape, dtype, default=None):
        if dtype not in self.valid_dtypes:
            raise Exception('%s is not a valid data type.' % dtype)
        if not default is None:
            self.layout[name] = tf.placeholder_with_default(tf.constant(default, dtype=dtype),
                                                            shape, 'FL/DEFAULT_' + name)
        else:
            self.layout[name] = tf.placeholder(tf.as_dtype(dtype), shape, 'FL/' + name)

    def _getHull(self, component):
        if isinstance(component, (tf.Tensor, tf.SparseTensor, tf.Variable)):
            tshape = component.get_shape()
            if tshape.dims is None or tshape.ndims == 0:
                return ' 1    '
            shape = tshape[1:].as_list()
        elif isinstance(component, np.ndarray):
            shape = list(component.shape)
        else:
            shape = [1]
        len_wo_bs = len(shape) - 1
        hull = ' '
        for dim in range(len_wo_bs):
            hull += '%-4d x ' % shape[dim]
        hull += '%-5d' % shape[-1]
        return hull

    def _assemble(self, left_comp, len_prefix, assemblage=None, sub_scope=''):
        left_symbol = left_comp.symbol
        left_msg = left_comp.message
        if sub_scope:
            sub_prefix = sub_scope + '/'
        else:
            sub_prefix = sub_scope
        # this is an atomic component
        if left_symbol == '>':
            for comp in left_comp.component:
                assemblage = self.assemble(comp, assemblage=assemblage,
                                           sub_scope=sub_scope, is_external=False)
            return assemblage
        elif left_symbol in ['+', '-', '*', '@', '&']:
            operator = None
            self.operands_counter[left_symbol] += 1
            # TODO: if a pod is extended to more than two comps, assemblage_name needs modification
            assemblage_name = left_comp.name + '_' + str(self.operands_counter[left_symbol])
            assemblage_list = []
            hull_list = []
            init_assemblage = assemblage
            for comp in left_comp.component:
                assemblage = self.assemble(comp, assemblage=init_assemblage,
                                           sub_scope=sub_scope, is_external=False)
                assemblage_list.append(assemblage)
                hull = self._getHull(self.layout[assemblage])
                hull_list.append(hull)
                if operator is None:
                    operator = self.layout[assemblage]
                else:
                    if left_symbol == '&':
                        operator = self.operands[left_symbol]([operator, self.layout[assemblage]],
                                                              axis=-1, name=assemblage_name)
                    else:
                        operator = self.operands[left_symbol](operator,
                                                              self.layout[assemblage],
                                                              name=assemblage_name)
            self.layout[sub_prefix + assemblage_name] = operator
            self.blueprint._combineNodes(assemblage_list, hull_list,
                                            sub_prefix + assemblage_name, left_symbol)
            return sub_prefix + assemblage_name
        else:
            node_name = sub_prefix + left_comp.name
            if node_name in self.layout.keys():  # Reuse or Redefine an existent node
                assert len(left_msg) == 1  # the only way to reuse is invoking DUPLICATE with single input
                hull = self._getHull(left_msg[0])
                self.blueprint._drawNode(left_msg[0].op.name[len_prefix:], node_name, hull)
                return sub_prefix + left_comp.name
            if assemblage is None:
                self.layout[node_name] = left_comp.component(name=left_comp.name)
            else:
                if left_symbol == 'penalty':
                    self.layout[node_name] = left_comp.component(name=left_comp.name)
                else:  # message is .input
                    self.layout[node_name] = left_comp.component(name=left_comp.name,
                                                                 input=self.layout[assemblage])
                    # draw layout sheet
                    hull = self._getHull(self.layout[assemblage])
                    self.blueprint._drawNode(assemblage, node_name, hull)
            for msg in left_msg:
                # draw layout sheet
                if isinstance(msg, (tf.Tensor, tf.SparseTensor, tf.Variable)):
                    hull = self._getHull(msg)
                    if msg.name.startswith('FL/'):  # if the input is a fuel line
                        self.blueprint._drawNode(msg.op.name[3:], node_name, hull, init=True)
                    else:
                        self.blueprint._drawNode(msg.op.name[len_prefix:], node_name, hull)
            return sub_prefix + left_comp.name

    def assemble(self, left_comp, assemblage=None, sub_scope='', is_external=True,
                 reuse=None):
        if not isinstance(left_comp, Pod):
            raise TypeError('Only the members from Component can be assembled.')
        if self.scope[:3] == 'FL/':
            raise ValueError('FL is the reserved words for fuel lines in spacecraft. '
                             + 'Please change your global scope name.')
        len_prefix = len(self.scope)
        if not is_external:
            return self._assemble(left_comp, len_prefix, assemblage=assemblage, sub_scope=sub_scope)
        else:
            # append sub scope
            if sub_scope:
                scope = self.scope + sub_scope + '/'
            else:
                scope = self.scope
            # whether to reuse variable name
            if reuse is None:
                reuse = tf.AUTO_REUSE
            with tf.variable_scope(scope, reuse=reuse):
                return self._assemble(left_comp, len_prefix, assemblage=assemblage, sub_scope=sub_scope)