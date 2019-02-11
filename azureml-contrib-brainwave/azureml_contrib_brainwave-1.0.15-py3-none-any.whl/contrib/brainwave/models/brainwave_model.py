# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module with the baseclass of brainwave models and the renset-50 model."""
import os
import tempfile
import zipfile
from abc import abstractproperty

try:
    from abc import ABCMeta

    ABC = ABCMeta('ABC', (), {})
except ImportError:
    from abc import ABC

import requests
import tensorflow as tf
from azureml.contrib.brainwave.external.tensorflow.graph_util_impl import convert_variables_to_constants


class BrainwaveModel(ABC):
    """Abstract base class for Brainwave models.

    Brainwave models are specific neural networks that can be
    accelerated  on dedicated hardware.
    """

    _prefix = ""

    def __init__(self, model_base_path, model_folder_name, version, check_point_uri, save_name,
                 is_frozen=False, weight_path=None):
        """Abstract base class for a brainwave model.

        To add a new model, implement a subclass - model folder_name, version, checkpoint_uri and save_name
        should all be given by the user. Weight path and is frozen should be exposed at least for quantized versions.
        :param model_base_path: The base path to store all models in. Generally given by the user.
        :param model_folder_name: The path on disk to store all versions of this model.
        :param version: The version of this model.
        :param check_point_uri: The URI where the model is downloaded from if they don't have it on disk.
        :param save_name: The name the checkpoint is saved under, used to load metagraph.
        :param is_frozen: If the model should be frozen when it is loaded.
        :param weight_path: A custom path to load weights from, instead of the default path on disk. Used in retraining
        scenarios.
        """
        self._model_folder_name = model_folder_name
        self.version = version
        self.__check_point_uri = check_point_uri
        self._save_name = save_name
        self.__model_dir = os.path.join(model_base_path, self._model_folder_name, self.version)
        self.__metagraph_location = os.path.join(self.__model_dir, '{0}_bw.meta'.format(self._save_name))
        self.__download_if_not_present()
        if weight_path is None:
            self.__checkpoint_directory = self.__model_dir
        else:
            self.__checkpoint_directory = weight_path
        self.is_frozen = is_frozen
        self.__saver = None

    def __download_if_not_present(self):
        if not os.path.exists(self.__metagraph_location):
            if not os.path.exists(self.__model_dir):
                os.makedirs(self.__model_dir)
            r = requests.get(self.__check_point_uri)
            model_zip_path = os.path.join(self.__model_dir, 'model.zip')
            with open(model_zip_path, 'wb') as output:
                output.write(r.content)
            zip_ref = zipfile.ZipFile(model_zip_path, 'r')
            zip_ref.extractall(self.__model_dir)
            zip_ref.close()
            os.remove(model_zip_path)

    def __import_frozen_graph_def(self, input_map=None):
        frozen_graph_def_location = os.path.join(self.__checkpoint_directory,
                                                 self.model_ref + "." + self.model_version + ".frozen.pb")
        if not os.path.exists(frozen_graph_def_location):
            with tf.Session(graph=tf.Graph()) as sess:
                # The graph we import here will have no input_tensor, so the saved graphdef will still have
                # the original input names/values (ie, on disk is_training will be false).
                self.__saver = tf.train.import_meta_graph(self.__metagraph_location)
                self.restore_weights(sess)
                frozen_graph_def = convert_variables_to_constants(sess, sess.graph.as_graph_def(),
                                                                  [self._input_op_name()],
                                                                  [self._output_op_name()])
                with tf.gfile.GFile(frozen_graph_def_location, "wb") as f:
                    f.write(frozen_graph_def.SerializeToString())
        with tf.gfile.GFile(frozen_graph_def_location, "rb") as f:
            input_graph_def = tf.GraphDef()
            input_graph_def.ParseFromString(f.read())
            return tf.import_graph_def(input_graph_def, name='', input_map=input_map,
                                       return_elements=[self.output_tensor_name])

    def import_graph_def(self, input_tensor=None, is_training=True):
        """Import the graph definition corresponding to this model.

        Imports into the currently active graph.

        :param input_tensor: Input tensor for the model.
        :type input_tensor: tf.Tensor
        :param is_training: If the graph is training.
        :type is_training: bool
        :return: Output tensor of the graph definition.
        """
        input_map = {"is_training": tf.placeholder_with_default(is_training, (), "is_training")}
        if input_tensor is not None:
            input_map[self._input_op_name()] = input_tensor
        if self.is_frozen:
            return self.__import_frozen_graph_def(input_map)[0]
        else:
            if input_tensor is not None:
                self._input_op = input_tensor.name[:-2]  # store the input tensor's name for extracting the graph.
            self.__saver = tf.train.import_meta_graph(self.__metagraph_location, input_map=input_map)
            return tf.get_default_graph().get_tensor_by_name(self.output_tensor_name)

    def restore_weights(self, session):
        """Restore the weights of the model into the specific session.

        :param session: The session to load the weights into.
        :type session: tf.Session
        """
        self.__saver.restore(session, tf.train.latest_checkpoint(self.__checkpoint_directory))

    def save_weights(self, path, session=None):
        """Save the weights of the model from a specific session into a specific path.

        :param path: Path of the checkpoint to save the weights into.
        :param session: Session to save weights from.
        :type session: tf.Session
        """
        if session is None:
            session = tf.get_default_session()
        self.__saver.save(session, path, write_meta_graph=False)

    # Apparently compiler needs a checkpoint with only this part.
    def _write_only_this_checkpoint(self, path, session):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.save_weights(tmpdir, session)
            with tf.Session(graph=tf.Graph()) as sess:
                self.import_graph_def(is_training=False)
                self.restore_weights(sess)
                saver = tf.train.Saver()
                saver.save(sess, path)

    @property
    def model_ref(self):
        """
        Name that refers to the model - used for writing the model_def.

        :return:
        """
        return self._save_name

    @property
    def model_version(self):
        """Model Version.

        :return:
        """
        return self.version

    @abstractproperty
    def output_dims(self):
        """Output dimensions of the model."""
        raise NotImplementedError("Base class doesn't implement this")

    @abstractproperty
    def input_dims(self):
        """Input dimensions of the model."""
        raise NotImplementedError("Base class doesn't implement this")

    @property
    def input_tensor_name(self):
        """Name of the input tensor of this model.

        :return:
        """
        return self._input_op_name() + ":0"

    @property
    def output_tensor_name(self):
        """Name of the output tensor of this model.

        :return:
        """
        return self._output_op_name() + ":0"

    def _input_op_name(self):
        return self._input_op

    def _output_op_name(self):
        return self._output_op

    def _write_to_tempdir(self, sess, path):
        model_path = path + "/{0}".format(self._save_name)
        if self.is_frozen:
            tf.train.latest_checkpoint(self.__checkpoint_directory)
            with tf.Session(graph=tf.Graph()) as sess:
                sav = tf.train.import_meta_graph(self.__metagraph_location)
                sav.restore(sess, tf.train.latest_checkpoint(self.__checkpoint_directory))
                sav.save(sess, model_path)
        else:
            self._write_only_this_checkpoint(model_path, sess)

    @classmethod
    def _download_classifier(cls, model_dir):
        rndir = os.path.join(model_dir, cls._modelname, cls._modelver)
        _classifier_location = os.path.join(rndir, "{}_classifier.pb".format(cls._save_name))
        if not os.path.exists(_classifier_location):
            if not os.path.exists(rndir):
                os.makedirs(rndir)
            r = requests.get(cls.classifier_uri)
            with open(_classifier_location, 'wb') as output:
                output.write(r.content)
        return _classifier_location

    def get_default_classifier(self, input_tensor):
        """Import a frozen, default Imagenet classifier for the model into the current graph.

        :param input_tensor: The input feature tensor for the classifier. Expected to be [?, 2048]
        :param model_dir: The directory to download the classifier into. Used as a cache locally.
        :return:
        """
        _classifier_location = self._download_classifier(self.__model_dir)

        input_map = {self.classifier_input: input_tensor}
        input_graph_def = tf.GraphDef()
        with tf.gfile.Open(_classifier_location, "rb") as f:
            data = f.read()

            input_graph_def.ParseFromString(data)

        tensors = tf.import_graph_def(input_graph_def, name='', input_map=input_map,
                                      return_elements=[self.classifier_output])
        return tensors[0]
