import os
import shutil
import tensorflow as tf
import numpy as np
import math
import datetime
import multiprocessing as mp
from ..utils import lazy_property, SpawningCache
from ..dataset import MemoryXYIter


class Tensorboardable:
    def __init__(self):
        self.placeholders = SpawningCache()
        self.summarys = SpawningCache()

    @property
    def path_tb(self):
        return 'log/%s_%s' % (self.__class__.__name__, datetime.datetime.now())

    @lazy_property
    def summary_writer(self):
        return tf.summary.FileWriter(self.path_tb, graph=tf.get_default_graph())

    def write(self, summ_value, i):
        """
        Write summary value to SummaryWriter
        :param summ_value:
        :param i:
        :return:
        """
        self.summary_writer.add_summary(summ_value, i)

    def writes(self, summ_value_list, i):
        """
        Write multiple summary values to SummaryWriter
        :param summ_value_list:
        :param i:
        :return:
        """
        for summ_value in summ_value_list:
            self.write(summ_value, i)

    def write_scalar(self, sess, name, value, i):
        ph = self.placeholders.get(
            key=name,
            spawner=lambda: tf.placeholder(tf.float32, [], name)
        )
        summ = self.summarys.get(
            key=name,
            spawner=lambda: tf.summary.scalar(name, ph)
        )
        summ_value = sess.run(summ, feed_dict={ph: value})
        self.write(summ_value, i)

    def write_scalars(self, sess, d, i):
        for name, value in d.items():
            self.write_scalar(sess, name, value, i)

    """
    def register_gvs(self, name, grads_and_vars):
        self.archive.summary(name, lambda: tf.summary.merge(
                [tf.summary.histogram('%s-grad' % v.name, g) for g, v in grads_and_vars if g is not None] +
                [tf.summary.histogram('%s' % v.name, v) for g, v in grads_and_vars]
            ))

    def get_gv(self, name):
        attribute_summ = '_cache_summ_gv_' + name
        return getattr(self, attribute_summ)

    """


class MPWrapper:
    def __init__(self, processes=None):
        self.processes = processes
        self.pool = mp.Pool(processes)

    def __enter__(self):
        self.pool.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.__exit__(exc_type, exc_val, exc_tb)

    def get(self, batch_iterator):
        return MPIterator(batch_iterator, self.pool)


class MPIterator:
    def __init__(self, batch_iterator, pool):
        self.batch_iterator = batch_iterator
        self.pool = pool

    def __len__(self):
        return self.batch_iterator.__len__()

    def __iter__(self):
        return self.pool.imap(self.batch_iterator.fetch_data, self.batch_iterator.index_iterator)


class Experiment(Tensorboardable):
    def train_epoch_g_mp(self, sess, batch_gen, i_epoch,
                         train_op, loss_op, accuracy, x_ph, y_ph, is_training_ph, lr_ph, lr=1e-3,
                         steps=None):

        with MPWrapper() as wrapper:
            batch_gen = wrapper.get(batch_gen)
            return self.train_epoch_g(sess, batch_gen, i_epoch, train_op, loss_op, accuracy,
                                      x_ph, y_ph, is_training_ph, lr_ph, lr, steps)

    def train_epoch_g(self, sess, batch_gen, i_epoch,
                      train_op, loss_op, accuracy, x_ph, y_ph, is_training_ph, lr_ph, lr=1e-3,
                      steps=None):
        losses = list()
        accs = list()
        batch_nums = list()
        loss, acc = 0, 0

        if steps is None:
            output_generator = enumerate(batch_gen)
        else:
            output_generator = zip(range(steps), batch_gen)

        for i_batch, (x_batch, y_batch) in output_generator:
            _, loss, acc = sess.run([train_op, loss_op, accuracy],
                                    feed_dict={x_ph: x_batch,
                                               y_ph: y_batch,
                                               is_training_ph: 1,
                                               lr_ph: lr})
            losses.append(np.mean(loss))
            accs.append(acc)
            batch_nums.append(len(y_batch))

            loss = np.average(losses, weights=batch_nums)
            acc = np.average(accs, weights=batch_nums)
            print('\rEpoch #%03d Batch #%03d/%d, Loss: %.4f, Acc: %.3f' %
                  (i_epoch, i_batch + 1, len(batch_gen), loss, acc), end='')
        else:
            print()
        return loss, acc

    def evaluate_g(self, sess, batch_gen,
                   loss_op, accuracy, x_ph, y_ph, is_training_ph, steps=None):
        losses = list()
        accs = list()
        batch_nums = list()

        if steps is None:
            output_generator = enumerate(batch_gen)
        else:
            output_generator = zip(range(steps), batch_gen)

        for i_batch, (x_batch, y_batch) in output_generator:
            loss, acc = sess.run([loss_op, accuracy],
                                 feed_dict={x_ph: x_batch,
                                            y_ph: y_batch,
                                            is_training_ph: 0})
            losses.append(np.mean(loss))
            accs.append(acc)
            batch_nums.append(len(y_batch))

            loss = np.average(losses, weights=batch_nums)
            acc = np.average(accs, weights=batch_nums)
            print('\rEvaluating Batch #%03d/%d, Loss: %.4f, Acc: %.3f' %
                  (i_batch + 1, len(batch_gen), loss, acc), end='')

        loss = np.average(losses, weights=batch_nums)
        acc = np.average(accs, weights=batch_nums)
        print('\rTest Loss: %.4f, Acc: %.3f' % (loss, acc))
        return loss, acc

    def train_epoch(self, sess, X, Y, i_epoch, batch_size,
                    train_op, loss_op, accuracy, x_ph, y_ph, is_training_ph, lr_ph, lr=1e-3):
        batch_gen = MemoryXYIter(X, Y, batch_size)
        return self.train_epoch_g(sess, batch_gen, i_epoch,
                                  train_op, loss_op, accuracy, x_ph, y_ph, is_training_ph, lr_ph, lr)

    def evaluate(self, sess, X, Y, batch_size,
                 loss_op, accuracy, x_ph, y_ph, is_training_ph):
        batch_gen = MemoryXYIter(X, Y, batch_size)
        return self.evaluate_g(sess, batch_gen, loss_op, accuracy, x_ph, y_ph, is_training_ph)

    def feedforward(self, sess, outputs, feed_dict_l, feed_dict, batch_size, total_size):
        """

        :param tf.Session sess:
        :param outputs: output to calculate
        :param feed_dict_l:
        :param feed_dict:
        :param batch_size:
        :param total_size:
        :return:
        """
        num_batch = int(math.ceil(total_size / batch_size))

        for i_batch in range(num_batch):
            feed_dict_batch = {}

    @staticmethod
    def accuracy(labels, predictions):
        correct = tf.cast(tf.equal(
            tf.cast(tf.argmax(predictions, axis=1), tf.int32),
            tf.cast(tf.argmax(labels, axis=1), tf.int32)
        ), tf.float32)
        return tf.reduce_mean(correct)

    @property
    def sess_config(self):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        return config

    @property
    def path_results(self):
        return './results/%s/' % self.__class__.__name__

    def clear_results(self):
        os.makedirs(self.path_results, exist_ok=True)
        shutil.rmtree(self.path_results)
        os.makedirs(self.path_results, exist_ok=True)

    @staticmethod
    def minimize_clipped(optimizer, loss, var_list=None, norm=5.):
        gradients, variables = zip(*optimizer.compute_gradients(loss, var_list=var_list))
        gradients, _ = tf.clip_by_global_norm(gradients, norm)
        grads_and_vars = list(zip(gradients, variables))
        return optimizer.apply_gradients(grads_and_vars)


class ClassificationExperiment(Experiment):
    def main_train(self):
        pass
