#
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
#

import grakn
import numpy as np
import tensorflow as tf
import tensorflow.contrib.layers as layers
from tensorflow.python import debug as tf_debug

import kglib.kgcn.preprocess.persistence as persistence
import kglib.kgcn.models.embedding as base
import kglib.kgcn.models.tmp.manager as manager
import kglib.kgcn.neighbourhood.data.sampling.ordered as ordered
import kglib.kgcn.neighbourhood.data.sampling.sampler as samp
import kgcn.neighbourhood.schema.strategy as schema_strat

flags = tf.app.flags
FLAGS = flags.FLAGS

# flags.DEFINE_float('learning_rate', 0.01, 'Learning rate')
# flags.DEFINE_integer('classes_length', 2, 'Number of classes')
# flags.DEFINE_integer('features_length', 9 + 20 + 128, 'Number of features after encoding')
# flags.DEFINE_integer('starting_concepts_features_length', 20 + 128,
#                      'Number of features after encoding for the nodes of interest, which excludes the features for '
#                      'role_type and role_direction')
# flags.DEFINE_integer('aggregated_length', 20, 'Length of aggregated representation of neighbours, a hidden dimension')
# flags.DEFINE_integer('output_length', 32, 'Length of the output of "combine" operation, taking place at each depth, '
#                                           'and the final length of the embeddings')
#
# flags.DEFINE_integer('max_training_steps', 100, 'Max number of gradient steps to take during gradient descent')
# flags.DEFINE_string('log_dir', './out', 'directory to use to store data from training')

NO_DATA_TYPE = ''  # TODO Pass this to traversal/executor


def main():
    # entity_query = "match $x isa person, has name 'Sundar Pichai'; get;"
    entity_query = "match $x isa company, has name 'Google'; get;"
    uri = "localhost:48555"
    keyspace = "test_schema"
    client = grakn.Grakn(uri=uri)
    session = client.session(keyspace=keyspace)
    tx = session.transaction(grakn.TxType.WRITE)

    neighbour_sample_sizes = (4, 3)

    sampling_method = ordered.ordered_sample

    samplers = []
    for sample_size in neighbour_sample_sizes:
        samplers.append(samp.Sampler(sample_size, sampling_method, limit=sample_size * 2))

    # Strategies
    role_schema_strategy = schema_strat.SchemaRoleTraversalStrategy(include_implicit=False, include_metatypes=False)
    thing_schema_strategy = schema_strat.SchemaThingTraversalStrategy(include_implicit=False, include_metatypes=False)

    traversal_strategies = {'role': role_schema_strategy,
                            'thing': thing_schema_strategy}

    concepts = [concept.get('x') for concept in list(tx.query(entity_query))]

    kgcn = KGCN(session, traversal_strategies, samplers)

    kgcn.train(session, concepts, np.array([[1, 0]], dtype=np.float32))
    kgcn.predict(session, concepts)


class KGCN:

    def __init__(self, storage_path=None):
        """
        A full Knowledge Graph Convolutional Network, running with TensorFlow and Grakn
        :param schema_tx:
        :return:
        """
        ################################################################################################################
        # Raw Array Building
        ################################################################################################################


        ################################################################################################################
        # Learner
        ################################################################################################################

        # Create a session for running Ops on the Graph.
        self._sess = tf.Session()
        self._graph = tf.get_default_graph()
        if FLAGS.debug:
            self._sess = tf_debug.LocalCLIDebugWrapperSession(self._sess)

        features_lengths = [FLAGS.features_length] * len(self._neighbour_sample_sizes)
        features_lengths[-1] = FLAGS.starting_concepts_features_length
        print(features_lengths)

        # optimizer = tf.train.AdagradOptimizer(learning_rate=FLAGS.learning_rate)
        # optimizer = tf.train.AdamOptimizer(learning_rate=FLAGS.learning_rate)
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=FLAGS.learning_rate)
        learner = base.SupervisedKGCNClassifier(FLAGS.classes_length, features_lengths,
                                                FLAGS.aggregated_length,
                                                FLAGS.output_length, self._neighbour_sample_sizes, optimizer,
                                                sigmoid_loss=False,
                                                regularisation_weight=0.0, classification_dropout_keep_prob=0.7,
                                                classification_activation=lambda x: x,
                                                # classification_activation=tf.nn.tanh,
                                                # Moves to nn.math.tanh in r1.12
                                                # classification_activation=tf.nn.sigmoid,
                                                # classification_activation=tf.nn.softsign,
                                                classification_regularizer=layers.l2_regularizer(scale=0.1),
                                                classification_kernel_initializer=
                                                     tf.contrib.layers.xavier_initializer())

        self._learning_manager = manager.LearningManager(learner, FLAGS.max_training_steps, FLAGS.log_dir, self._dataset_initializer)
        self._learning_manager(self._sess, encoded_arrays, labels)  # Build the graph

        ################################################################################################################
        # Calls to the Learning manager
        ################################################################################################################
        self._storage_path = storage_path
        self._mode_params = {
            tf.estimator.ModeKeys.TRAIN: KGCN.ModeParams(self._learning_manager.train, 'train.p'),
            tf.estimator.ModeKeys.EVAL: KGCN.ModeParams(self._learning_manager.evaluate, 'eval.p'),
            tf.estimator.ModeKeys.PREDICT: KGCN.ModeParams(self._learning_manager.predict, 'predict.p'),
        }

    class ModeParams:
        def __init__(self, func, file_suffix):
            self.func = func
            self.file_suffix = file_suffix

    def _pack_feed_dict(self, feed_dict):
        print('Packing...')
        feed_dict_placeholder_names_as_keys = {}

        for placeholder, value in feed_dict.items():
            print('    ' + placeholder.name)
            feed_dict_placeholder_names_as_keys[placeholder.name] = value

        return feed_dict_placeholder_names_as_keys

    def _unpack_feed_dict(self, packed_feed_dict):

        print('Unpacking...')
        unpacked_feed_dict = {}
        for placeholder_name, value in packed_feed_dict.items():
            print('    ' + placeholder_name)
            unpacked_feed_dict[self._graph.get_tensor_by_name(placeholder_name)] = value

        return unpacked_feed_dict

    def get_feed_dict(self, mode, session=None, concepts=None, labels=None, load=False, save=True):

        file_path = self._storage_path + self._mode_params[mode].file_suffix

        if load:
            feed_dict = self._unpack_feed_dict(persistence.load_variable(file_path))
        else:
            feed_dict = self._build_feed_dict(session, concepts, labels=labels)

            if save:
                if self._storage_path is None:
                    raise ValueError('Cannot save data without a path to save to')

                persistence.save_variable(self._pack_feed_dict(feed_dict), file_path)

                # self._savers[mode] = tf.tra§in.Saver(feed_dict)
                # saver = tf.train.Saver(feed_dict)
                # saver.save(self._sess, file_path)
                # self._savers[mode].save(self._sess, file_path)

        return feed_dict

    def model_fn(self, mode, session=None, concepts=None, labels=None, load=False, save=True):

        feed_dict = self.get_feed_dict(mode, session, concepts, labels=labels, load=load, save=save)
        self._mode_params[mode].func(self._sess, feed_dict)

    def train(self, session, concepts, labels):
        self.model_fn(tf.estimator.ModeKeys.TRAIN, session, concepts, labels, save=True)

    def evaluate(self, session, concepts, labels):
        self.model_fn(tf.estimator.ModeKeys.EVAL, session, concepts, labels, save=True)

    def predict(self, session, concepts):
        self.model_fn(tf.estimator.ModeKeys.PREDICT, session, concepts)

    def train_from_file(self):
        self.model_fn(tf.estimator.ModeKeys.TRAIN, load=True)

    def evaluate_from_file(self):
        self.model_fn(tf.estimator.ModeKeys.EVAL, load=True)

    def predict_from_file(self):
        self.model_fn(tf.estimator.ModeKeys.PREDICT, load=True)


if __name__ == "__main__":
    main()
