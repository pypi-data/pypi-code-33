"""
Base Tatau's model

"""
from abc import abstractmethod, ABC
from collections import Iterable
from logging import getLogger

from tatau.nn.class_loader import load_class
from .progress import TrainProgress

logger = getLogger(__name__)


class Model(ABC):
    """
    Base Model Class

    """
    #: Path to the weights summarizer class :py:class:`tatau.nn.tatau.summarizer.Summarizer`
    weights_summarizer_class = 'tatau.nn.tatau.summarizer.Summarizer'

    #: Path to weights serializer class :py:class:`tatau.nn.tatau.serializer.WeightsSerializer`
    weights_serializer_class = 'tatau.nn.tatau.serializer.WeightsSerializer'

    transform_train = None
    transform_eval = None
    transform_target = None

    def __init__(self):
        self._model = None
        self._optimizer = None

    @property
    def optimizer(self):
        """
        Gets model optimizer.

        :return: instance optimizer
        """
        return self._optimizer

    @optimizer.setter
    def optimizer(self, value):
        self._optimizer = value

    @classmethod
    def load_model(cls, path: str):
        """
        Construct model from asset.

        :param path: path to model file
        :return: model instance
        :rtype: Model
        """
        model = None

        # try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('model', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, 'Model'):
            raise RuntimeError('Module {} has no model declaration'.format(path))

        if not issubclass(module.Model, Model):
            raise RuntimeError('Model must be inherited from Tatau Model')

        model = module.Model()
        # except Exception as e:
        #     logger.exception(e)

        return model

    @property
    def native_model(self):
        if not self._model:
            self._model = self.native_model_factory()
        return self._model

    @classmethod
    def native_model_factory(cls):
        """
        Native Model Factory.

        :return: instance native model
        """
        raise NotImplementedError()

    @abstractmethod
    def get_weights(self):
        """
        Get model weights.

        :return: weights
        :rtype: list(numpy.array)
        """
        pass

    @abstractmethod
    def set_weights(self, weights: list):
        """
        Set model weights.

        :param weights: weights
        :return:
        """
        pass

    @abstractmethod
    def get_data_loader(self, chunk_dirs: Iterable, batch_size, transform, target_transform, **kwargs):
        """
        This method should return generator of train data.
        For Keras will be used for fit_generator function.
        For PyTorch should return instance of DataLoader.

        :param chunk_dirs: list of paths to chunk dirs
        :param batch_size: batch size
        :param transform: transformations
        :param target_transform: transformations for target
        :return:
        """
        pass

    @abstractmethod
    def train(self, chunk_dirs: Iterable, batch_size: int, current_iteration: int,
              nb_epochs: int, train_progress: TrainProgress)-> list:
        """
        Train model.
        Before the start of the training, the part of the dataset allocated for the worker by means of chunks will be
        saved to disk. The array of paths to the chunk will be passed through the chunks_dir parameter.

        :param train_progress: Task Progress Callback
        :param batch_size: batch size
        :param chunk_dirs: list of paths to chunk dirs
        :param current_iteration: iteration on whole train process
        :param nb_epochs: number of epochs in current iteration
        :param train_progress: instance of TrainProgress for reporting progress
        :return: loss history list((loss, acc))
        """
        pass

    @abstractmethod
    def eval(self, chunk_dirs: Iterable, batch_size: int):
        """
        Evaluate  model

        :param chunk_dirs: list of paths to chunk dirs
        :param batch_size: batch size
        :return: tuple(loss, acc)
        """
        pass

    @classmethod
    def get_weights_serializer(cls):
        """
        Construct and return an instance of serializer class, which will be used for save and load model weights.

        :return: instance of Serializer class
        """
        return load_class(cls.weights_serializer_class)()

    @classmethod
    def get_weights_summarizer(cls):
        """
        Construct and return an instance of summarizer class,
        which will be used for summarize model weights from different workers.

        :return: instance of summarizer
        """
        return load_class(cls.weights_summarizer_class)()

    def load_weights(self, path: str):
        """
        Load and set weights to model.

        :param path: path to weights file
        """
        self.set_weights(weights=self.get_weights_serializer().load(path=path))

    def save_weights(self, path: str):
        """
        Save model weights.

        :param path: target path to weights file
        """
        self.get_weights_serializer().save(weights=self.get_weights(), path=path)
