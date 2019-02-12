#!/usr/bin/env python
'''
time_machine_tf
Created by Seria at 04/02/2019 4:35 PM
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
from tensorflow.python.framework import graph_util
import os
import json
from ..toolkit import parseConfig, recordConfig

class TimeMachineTF(object):
    def __init__(self, param):
        '''
        Time Machine saves current states or restores saved states
        '''
        self.param = param
        self.restorer = None
        self.saver = None
        if not self.param['ckpt_path'] is None:
            if self.param['ckpt_scope'] is None:
                to_be_restored = tf.global_variables()
            else:
                to_be_restored = tf.global_variables(scope=self.param['ckpt_scope'])
            self.restorer = tf.train.Saver(to_be_restored)
        if not self.param['save_path'] is None:
            if self.param['save_scope'] is None:
                to_be_saved = tf.global_variables()
            else:
                to_be_saved = tf.global_variables(scope=self.param['save_scope'])
            self.saver = tf.train.Saver(to_be_saved, max_to_keep=1)
        if not self.param['thawed_path'] is None:
            self.time_point = tf.GraphDef()
            with open(self.param['thawed_path'], 'rb') as thawing:
                self.time_point.ParseFromString(thawing.read())

    def _setParams(self, sess, mile, scope, config):
        self.config = config
        self.sess = sess
        self.mile = mile
        if scope:
            self.scope = scope[:-1]
        else:
            self.scope = 'ckpt'
        self.sess.run(tf.global_variables_initializer())

    def backTo(self):
        if self.restorer is None:
            return
        else:
            if os.path.isfile(self.param['ckpt_path']):
                ckpt = self.param['ckpt_path']
            else:
                ckpt = tf.train.latest_checkpoint(self.param['ckpt_path'])
            self.restorer.restore(self.sess, ckpt)
            print('+' + ((10 + len(self.param['ckpt_path'])) * '-') + '+')
            print('| Back to \033[1;34m%s\033[0m |' % self.param['ckpt_path'])
            print('+' + ((10 + len(self.param['ckpt_path'])) * '-') + '+')

    def digWormHole(self):
        if self.saver is None:
            return
        else:
            if not os.path.exists(self.param['save_path']):
                os.mkdir(self.param['save_path'])
            self.saver.save(self.sess, os.path.join(self.param['save_path'], self.scope),
                            global_step=self.mile, write_meta_graph=True)
            print('| Worm Hole is located at \033[1;34m%s\033[0m |' % self.param['save_path'])

            temp_config = os.path.join(os.getcwd(), 'temp_config.json')
            if os.path.exists(temp_config):
                hyper_param = parseConfig(temp_config)
                self.config['SC'] = hyper_param
                recordConfig(os.path.join(self.param['save_path'], 'config.json'), self.config)
                os.remove(os.path.join(os.getcwd(), 'temp_config.json'))

    def thawTheMoment(self, fuel_line, moments):
        moments = [m.name for m in moments]
        return tf.import_graph_def(self.time_point, fuel_line, return_elements=moments)

    def freezeTheMoment(self, moments):
        if self.param['frozen_path'] is None:
            return
        else:
            moments = [m.op.name for m in moments]
            out_graph_def = graph_util.convert_variables_to_constants(self.sess, self.sess.graph_def, moments)
            tf.train.write_graph(out_graph_def, os.path.dirname(self.param['frozen_path']),
                                 os.path.basename(self.param['frozen_path']), as_text=False)
            print('+' + ((23 + len(self.param['frozen_path'])) * '-') + '+')
            print('| Moment is frozen in \033[1;34m%s\033[0m |' % self.param['frozen_path'])
            print('+' + ((23 + len(self.param['frozen_path'])) * '-') + '+')