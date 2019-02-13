from __future__ import absolute_import
import tensorflow as tf
from aether.libraries.contrib.nn.learning import TensorFlowArchitecture, TensorflowMlpModel
import math, random, time


import logging
logger = logging.getLogger(__name__)


from six.moves import range

# A great guide to the modules, motivations, and evolution of Inception.
# https://towardsdatascience.com/a-simple-guide-to-the-versions-of-the-inception-network-7fc52b863202

class InceptionBuilder(object):

    @staticmethod
    def _conv_bn(x, filters, num_row, num_col, is_train, padding='same', strides=(1, 1)):
        x = tf.layers.conv2d(x, filters, (num_row, num_col), strides=strides, activation=tf.nn.relu, padding=padding)
        x = tf.layers.batch_normalization(x, training=is_train)
        return x

    # These 1x1 convolutions are used to reduce the feature dimension (from 192 features to 32, here), before the
    # expensive computation of convolutions (3x3, 5x5, etc..). These base on the success of embeddings, where even
    # low dimensional information contains a lot of information about the original high dimensional space.
    @staticmethod
    def _InceptionResNetModuleA(x, is_train, factor32=1):
        branch_0 = InceptionBuilder._conv_bn(x, 32*factor32, 1, 1, is_train)

        branch_1 = InceptionBuilder._conv_bn(x, 32*factor32, 1, 1, is_train)
        branch_1 = InceptionBuilder._conv_bn(branch_1, 32*factor32, 3, 1, is_train)
        branch_1 = InceptionBuilder._conv_bn(branch_1, 32*factor32, 1, 3, is_train)

        branch_2 = InceptionBuilder._conv_bn(x, 32*factor32, 1, 1, is_train)
        branch_2 = InceptionBuilder._conv_bn(branch_2, 32*factor32, 3, 1, is_train)
        branch_2 = InceptionBuilder._conv_bn(branch_2, 32*factor32, 1, 3, is_train)
        branch_2 = InceptionBuilder._conv_bn(branch_2, 32*factor32, 3, 1, is_train)
        branch_2 = InceptionBuilder._conv_bn(branch_2, 32*factor32, 1, 3, is_train)
        branches = [branch_0, branch_1, branch_2]

        filter_branch = tf.concat(branches, axis=3)
        filter_branch = InceptionBuilder._conv_bn(filter_branch, 32*8*factor32, 1, 1, is_train)

        block = tf.concat([x, filter_branch], axis=3)
        return block

    @staticmethod
    def _InceptionResNetModuleSmallA(x, is_train, factor32=1):
        branch_0 = InceptionBuilder._conv_bn(x, 32*factor32, 1, 1, is_train)

        branch_1 = InceptionBuilder._conv_bn(x, 32*factor32, 1, 1, is_train)
        branch_1 = InceptionBuilder._conv_bn(branch_1, 32*factor32, 3, 1, is_train)
        branch_1 = InceptionBuilder._conv_bn(branch_1, 32*factor32, 1, 3, is_train)

        branches = [branch_0, branch_1]

        filter_branch = tf.concat(branches, axis=3)
        filter_branch = InceptionBuilder._conv_bn(filter_branch, 32*2*factor32, 1, 1, is_train)

        block = tf.concat([x, filter_branch], axis=3)
        return block

    @staticmethod
    def _InceptionResNetModuleB(x, is_train, factor32=4):
        branch_0 = InceptionBuilder._conv_bn(x, 32*factor32, 1, 1, is_train)

        branch_1 = InceptionBuilder._conv_bn(x, 32*factor32, 1, 1, is_train)
        branch_1 = InceptionBuilder._conv_bn(branch_1, 32*factor32, 7, 1, is_train)
        branch_1 = InceptionBuilder._conv_bn(branch_1, 32*factor32, 1, 7, is_train)

        branches = [branch_0, branch_1]

        filter_branch = tf.concat(branches, axis=3)
        filter_branch = InceptionBuilder._conv_bn(filter_branch, 32*7*factor32, 1, 1, is_train)

        block = tf.concat([x, filter_branch], axis=3)
        return block

    @staticmethod
    def _InceptionStemModule(inputs, is_train):
        a = InceptionBuilder._conv_bn(inputs, 32, 3, 3, is_train, strides=(2, 2), padding='same')
        b = InceptionBuilder._conv_bn(a, 32, 3, 3, is_train, padding='same')
        b = InceptionBuilder._conv_bn(b, 64, 3, 3, is_train)
        c = tf.layers.max_pooling2d(b, (3, 3), strides=(2, 2), padding='same')

        c = InceptionBuilder._conv_bn(c, 80, 1, 1, is_train, padding='same')
        c = InceptionBuilder._conv_bn(c, 192, 3, 3, is_train, padding='same')
        d = tf.layers.max_pooling2d(c, (3, 3), strides=(2, 2), padding='same')
        return d, [a, b, c, d]

    # @staticmethod
    # def _InceptionInverseStemModule(layers_merged, is_train):
    #     x = tf.concat([layers_merged[0], layers_merged[1]], axis=3)
    #     x = InceptionBuilder._conv_bn(x, 32, 3, 3, is_train, padding='same')
    #     # conv2d_transpose XYZ
    #     # x = layers.UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='nearest')(x)
    #     x = tf.image.resize_nearest_neighbor(x, (2*tf.shape(x)[1],2*tf.shape(x)[2]))
    #     x = tf.concat([layers_merged[2], x], axis=3)
    #     x = InceptionBuilder._conv_bn(x, 32, 3, 3, is_train, padding='same')
    #     x = InceptionBuilder._conv_bn(x, 64, 3, 3, is_train)
    #     # x = layers.UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='nearest')(x)
    #     x = tf.image.resize_nearest_neighbor(x, (2*tf.shape(x)[1],2*tf.shape(x)[2]))
    #     x = tf.concat([layers_merged[3], x], axis=3)
    #     x = InceptionBuilder._conv_bn(x, 80, 1, 1, is_train, padding='same')
    #     x = InceptionBuilder._conv_bn(x, 192, 3, 3, is_train, padding='same')
    #     # x = layers.UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='nearest')(x)
    #     x = tf.image.resize_nearest_neighbor(x, (2*tf.shape(x)[1],2*tf.shape(x)[2]))
    #     x = InceptionBuilder._conv_bn(x, 64, 3, 3, is_train)
    #     return x

    @staticmethod
    def _InceptionConnectedModule(x, n_classes, is_train, n_hidden=None, keep_prob=None, scale128=4):
        if n_hidden is None:
            n_hidden = []

        # Classification block
        x = tf.reduce_mean(x, axis=(1,2))
        if keep_prob is not None and keep_prob != 1.0:
            x = tf.layers.dropout(x, rate=1.0-keep_prob, training=is_train)

        # Adds extra layers before classification
        for hidden in n_hidden:
            x = tf.layers.dense(inputs=x, units=hidden, activation=tf.nn.relu)

        x = tf.layers.dense(inputs=x, units=n_classes, activation=tf.nn.sigmoid)
        return x

    # @staticmethod
    # def _InceptionFullyConnectedModule(x, n_classes, keep_prob=None, name=None):
    #     # Classification block
    #     if keep_prob is not None and keep_prob != 1.0:
    #         x = layers.Dropout(rate=1.0 - keep_prob)(x)
    #     name = "predictions" if name is None else name
    #     # x = InceptionBuilder._conv_bn(x, 256, 1, 1, padding='same')
    #     x = layers.Dense(n_classes, activation='softmax', name=name)(x)
    #     return x


class TensorFlowCnnArchitecture(TensorFlowArchitecture):

    def build(self, image_size, n_classes, size="small", keep_prob=1.0, scale=2):

        inputs = tf.placeholder(tf.float32, [None, image_size[0], image_size[1], image_size[2]])
        labels = tf.placeholder(tf.float32, [None, n_classes])
        is_training = tf.placeholder(tf.bool)

        with tf.variable_scope("FeatureTrunk", reuse=tf.AUTO_REUSE):
            x, _ = InceptionBuilder._InceptionStemModule(inputs, is_training)

            x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale)
            x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale)
            # x = tf.layers.max_pooling2d(x, (3, 3), strides=(2, 2), padding='same')

            # if size in ["small", "medium", "large"]:
            x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*2)
            x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*2)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*2)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*2)
            # x = tf.layers.max_pooling2d(x, (3, 3), strides=(2, 2), padding='same')

            # if size in ["medium", "large"]:
            x = InceptionBuilder._InceptionResNetModuleSmallA(x, is_training, factor32=scale*4)
            x = InceptionBuilder._InceptionResNetModuleSmallA(x, is_training, factor32=scale*4)
            # x = InceptionBuilder._InceptionResNetModuleSmallA(x, is_training, factor32=scale*4)
            # x = InceptionBuilder._InceptionResNetModuleSmallA(x, is_training, factor32=scale*4)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*4)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*4)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*4)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*4)
            # x = tf.layers.max_pooling2d(x, (3, 3), strides=(2, 2), padding='same')

            # if size in ["large"]:
            # x = InceptionBuilder._InceptionResNetModuleSmallA(x, is_training, factor32=scale*8)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*8)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*8)
            # x = InceptionBuilder._InceptionResNetModuleA(x, is_training, factor32=scale*8)
            # x = tf.layers.max_pooling2d(x, (3, 3), strides=(2, 2), padding='same')

        logits = InceptionBuilder._InceptionConnectedModule(x, n_classes, is_training, keep_prob=keep_prob)

        probabilities = tf.nn.softmax(logits)
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=logits, labels=labels))
        train_step = tf.train.AdamOptimizer().minimize(loss)

        # Add our TensorBoard summaries
        tf.summary.scalar('loss', loss)

        label_ids = tf.cast(tf.argmax(labels, 1), tf.int32)
        for k in [1, 2, 3, 5, 10]:
            if k >= n_classes:
                continue
            top_n = tf.reduce_mean(tf.cast(tf.nn.in_top_k(predictions=logits, targets=label_ids, k=k), tf.int32))
            tf.summary.scalar('top_{}_acc'.format(k), top_n)

        summaries = tf.summary.merge_all()

        self._operators = dict(
            inputs=inputs,
            labels=labels,
            is_training=is_training,
            loss=loss,
            train_step=train_step,
            probabilities=probabilities,
            summaries=summaries,
        )

        return self
TensorFlowArchitecture.register(TensorFlowCnnArchitecture)



#
# class TensorFlowCnnSiameseArchitecture(object):
#
#     @staticmethod
#     def create_root(input):
#         layer1 = InceptionBuilder._InceptionResNetModuleA(input, factor32=1)
#
#         layer2 = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(layer1)
#         layer2 = InceptionBuilder._InceptionResNetModuleA(layer2, factor32=1)
#         layer2 = InceptionBuilder._InceptionResNetModuleA(layer2, factor32=1)
#
#         layer3 = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(layer2)
#         layer3 = InceptionBuilder._InceptionResNetModuleA(layer3, factor32=2)
#         layer3 = InceptionBuilder._InceptionResNetModuleSmallA(layer3, factor32=2)
#
#         layer4 = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(layer3)
#         layer4 = InceptionBuilder._InceptionResNetModuleSmallA(layer4, factor32=2)
#         layer4 = InceptionBuilder._InceptionResNetModuleSmallA(layer4, factor32=4)
#
#         features = layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same')(layer4)
#
#         return features, [layer4, layer3, layer2, layer1]
#
#     @staticmethod
#     def _create_deconvolution_root(layers_merged):
#         layer5 = InceptionBuilder._InceptionResNetModuleSmallA(layers_merged[0], factor32=2)
#         layer5 = layers.UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='nearest')(layer5)
#
#         layer6 = layers.concatenate([layer5, layers_merged[1]], axis=-1)
#         layer6 = InceptionBuilder._InceptionResNetModuleSmallA(layer6, factor32=6)
#         layer6 = InceptionBuilder._InceptionResNetModuleSmallA(layer6, factor32=2)
#         # layer6 = InceptionBuilder._InceptionResNetModuleA(layer6, factor32=2)
#         layer6 = layers.UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='nearest')(layer6)
#
#         layer7 = layers.concatenate([layer6, layers_merged[2]], axis=-1)
#         layer7 = InceptionBuilder._InceptionResNetModuleSmallA(layer7, factor32=3)
#         layer7 = InceptionBuilder._InceptionResNetModuleA(layer7, factor32=2)
#         # layer7 = InceptionBuilder._InceptionResNetModuleB(layer7, factor32=2)
#         layer7 = layers.UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='nearest')(layer7)
#
#         layer8 = layers.concatenate([layer7, layers_merged[3]], axis=-1)
#         layer8 = InceptionBuilder._InceptionResNetModuleA(layer8, factor32=2)
#         layer8 = InceptionBuilder._InceptionResNetModuleA(layer8, factor32=1)
#         # layer8 = InceptionBuilder._InceptionResNetModuleA(layer8, factor32=1)
#         layer8 = layers.UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='nearest')(layer8)
#
#         layer9 = layers.concatenate([layer8, layers_merged[4]], axis=-1)
#         layer9 = InceptionBuilder._InceptionResNetModuleA(layer9, factor32=1)
#
#         return layer9
#
#     @staticmethod
#     def create_model(image_size, n_bands, n_classes=None, keep_prob=0.8,
#                      n_regression=None, n_segmentation=None):
#         input_shape = [image_size[0], image_size[1], n_bands]
#
#         # When we reuse the same layer instance multiple times, the weights of the layer
#         # are also being reused. It is *the same* layer).
#         generic_input = layers.Input(input_shape)
#         features, [layer4, layer3, layer2, layer1] = InceptionONERASiamese.create_root(generic_input)
#
#         features_model = Model(generic_input, [features, layer4, layer3, layer2, layer1])
#         features, layer4, layer3, layer2, layer1 = None, None, None, None, None
#
#         inputs_A = layers.Input(input_shape)
#         inputs_B = layers.Input(input_shape)
#
#         encoded_a = features_model(inputs_A)
#         encoded_b = features_model(inputs_B)
#
#         layers_merged = [layers.concatenate([encoded_a[e_i], encoded_b[e_i]], axis=-1) for e_i in range(len(encoded_a))]
#         features_model, encoded_a, encoded_b = None, None, None
#
#         features_merged = layers_merged[0]
#
#         classifier_name = "classifier_model"
#         regression_name = "regression_model"
#         segmentation_name = "segmentation_model"
#
#         loss_functions = []
#         metric_functions = []
#         models = []
#
#         if n_classes is not None:
#             outputs = InceptionBuilder._InceptionConnectedModule(features_merged, n_classes, keep_prob=keep_prob, name=classifier_name)
#             model_classifier = Model([inputs_A, inputs_B], outputs, name=classifier_name)
#             loss_functions.append("categorical_crossentropy")
#             metric_functions.append(["accuracy"])
#             models.append(model_classifier)
#
#         if n_regression is not None:
#             outputs = InceptionBuilder._InceptionConnectedModule(features_merged, n_regression, keep_prob=keep_prob, name=regression_name)
#             model_regression = Model([inputs_A, inputs_B], outputs, name=regression_name)
#             loss_functions.append("mean_squared_error")
#             metric_functions.append(["accuracy", "mean_absolute_error"])
#             models.append(model_regression)
#
#         if n_segmentation is not None:
#             outputs = InceptionONERASiamese._create_deconvolution_root(layers_merged)
#             outputs = InceptionBuilder._InceptionFullyConnectedModule(outputs, n_segmentation, keep_prob=keep_prob, name=segmentation_name)
#             model_segmentation = Model([inputs_A, inputs_B], outputs, name=segmentation_name)
#             loss_functions.append("categorical_crossentropy")
#             metric_functions.append(["accuracy"])
#             models.append(model_segmentation)
#
#         return models, loss_functions, metric_functions
#
#     @staticmethod
#     def compile(models, loss_functions, metric_functions):
#         for i in range(len(models)):
#             models[i].compile(optimizer='rmsprop',
#                               loss=loss_functions[i],
#                               metrics=metric_functions[i])
#         return models
