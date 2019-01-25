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

import tensorflow as tf

import kglib.kgcn.encoder.encode as encode
import kglib.kgcn.models.downstream as ds
import kglib.kgcn.models.embedding as learners
import kglib.kgcn.models.tmp.manager as manager
import kglib.kgcn.neighbourhood.data.sampling.ordered as ordered
import kglib.kgcn.neighbourhood.data.sampling.sampler as samp
import kglib.kgcn.preprocess.preprocess
import kglib.kgcn.preprocess.preprocess as preprocess


neighbour_sample_sizes = (3, 4)
sampling_method = ordered.ordered_sample
num_samples = 30
batch_size = 30

################################################################################################################
# Features
################################################################################################################

# Make a dictionary to show which of the default keys should be ignored and pass it on to various objects
features_to_exclude = ['neighbour_value_date']
features_to_exclude = {key: None for key in features_to_exclude}

################################################################################################################
# Preprocessing
################################################################################################################

traversal_samplers = []
for sample_size in neighbour_sample_sizes:
    traversal_samplers.append(samp.Sampler(sample_size, sampling_method, limit=sample_size * 2))

formatters = {'neighbour_value_date': preprocess.datetime_to_unixtime}

traverser = kglib.kgcn.preprocess.preprocess.Traverser(traversal_samplers)


def input_fn(session, concepts):
    raw_array_depths = traverser(session, concepts)
    raw_array_depths = preprocess.apply_operations(raw_array_depths, formatters)
    return raw_array_depths


# Computation graph feeding
dataset_builder = preprocess.DatasetBuilder(neighbour_sample_sizes, features_to_exclude)
arrays_dataset = dataset_builder()

# if labels is not None:
# Build the placeholder for the labels
num_classes = 3
labels_placeholder = manager.build_labels_placeholder(None, num_classes, name='labels_input')
tf.summary.histogram('labels_input', labels_placeholder)


def _run(mode):

    output_tensors = self._output_tensors[mode]

    feed_dict = preprocess.build_feed_dict(dataset_builder.raw_array_placeholders, raw_array_depths,
                                           labels_placeholder=labels_placeholder, labels=labels)
    _ = sess.run(dataset_initializer, feed_dict=feed_dict)
    for step in range(self._max_training_steps):
        output_values = sess.run(*output_tensors)

################################################################################################################
# Combined Dataset
################################################################################################################

labels_dataset = tf.data.Dataset.from_tensor_slices(labels_placeholder)

dataset = tf.data.Dataset.zip((arrays_dataset, labels_dataset))

buffer_size = batch_size = tf.cast(batch_size, tf.int64)
dataset = dataset.shuffle(buffer_size=buffer_size, seed=5, reshuffle_each_iteration=True)
dataset = dataset.batch(batch_size=batch_size).repeat()

dataset_iterator = dataset.make_initializable_iterator()
dataset_initializer = dataset_iterator.initializer

shuffled_batch_arrays, labels = dataset_iterator.get_next()

print('shuffled_batch_arrays.shape')
print(shuffled_batch_arrays[0]['neighbour_type'].shape)
print('labels.shape')
print(labels.shape)

encoder = encode.Encoder(schema_tx)
encoded_arrays = encoder(shuffled_batch_arrays)

embedding = learners.Embedder(feature_lengths, aggregated_length, output_length, neighbour_sample_sizes,
                              normalisation=tf.nn.l2_normalize)


################################################################################################################
# Downstream learning
################################################################################################################

classifier = ds.SupervisedKGCNClassifier(kgcn, num_classes, optimizer,
                                         sigmoid_loss=True,
                                         regularisation_weight=0.0,
                                         classification_dropout_keep_prob=0.7,
                                         classification_activation=tf.nn.tanh,
                                         classification_regularizer=layers.l2_regularizer(scale=0.1),
                                         classification_kernel_initializer=tf.contrib.layers.xavier_initializer())

confusion_matrix, class_predictions, class_scores = classifier.train(session, concepts, labels)
confusion_matrix, class_predictions, class_scores = classifier.eval(session, concepts, labels)
class_predictions, class_scores = classifier.predict(session, concepts)
