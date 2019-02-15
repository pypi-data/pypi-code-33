# -*- coding: utf-8 -*-
"""
定义模型优化器
"""
import tensorflow as tf


class Optimizer(object):

    def __init__(self):
        self._lr = 0.01
        self._train_op = None
        self._global_step = tf.Variable(0, name='global_step', trainable=False)

    def __call__(self, *args, **kwargs):
        return self.optimizer_gradients(hp=kwargs["hp"], loss=kwargs["loss"])

    def _learning_rate_decay(self, init_lr, warmup_steps=4000.):
        """

        :param init_lr:
        :param warmup_steps:
        :return:
        """
        # noinspection PyTypeChecker
        step = tf.cast(self._global_step + 1, dtype=tf.float32)
        return init_lr * warmup_steps ** 0.5 * tf.minimum(step * warmup_steps ** -1.5, step ** -0.5)

    def optimizer_gradients(self, hp, loss):
        """  梯度优化器

        :param hp: 参数类
        :param loss: 损失函数
        :return:
        """
        self._lr = self._learning_rate_decay(hp.lr)
        tf.summary.scalar('train/lr', self._lr)
        optimizer = tf.train.AdamOptimizer(learning_rate=self._lr)
        # gradient clipping
        gvs = optimizer.compute_gradients(loss)
        clipped = []
        for grad, var in gvs:
            grad = tf.clip_by_norm(grad, 5.)
            clipped.append((grad, var))
        self._train_op = optimizer.apply_gradients(clipped, global_step=self._global_step)
        return self._train_op, self._global_step

    @property
    def lr(self):
        return self._lr
