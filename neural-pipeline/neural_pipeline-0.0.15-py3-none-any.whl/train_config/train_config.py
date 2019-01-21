from abc import ABCMeta, abstractmethod

from torch import Tensor
from torch.optim import Optimizer
from torch.nn import Module
import numpy as np

try:
    from IPython import get_ipython

    ip = get_ipython()
    if ip is not None:
        from tqdm import tqdm_notebook as tqdm
    else:
        from tqdm import tqdm
except ImportError:
    from tqdm import tqdm

from neural_pipeline.data_producer.data_producer import DataProducer
from neural_pipeline.data_processor.data_processor import TrainDataProcessor

__all__ = ['AbstractMetric', 'MetricsGroup', 'MetricsProcessor', 'AbstractStage', 'TrainStage', 'ValidationStage', 'TrainConfig']


class AbstractMetric(metaclass=ABCMeta):
    """
    Abstract class for metrics. When it works in neural_pipeline, it store metric value for every call of :meth:`calc`

    :param name: name of metric. Name wil be used in monitors, so be careful in use unsupported characters
    """

    def __init__(self, name: str):
        self._name = name
        self._values = np.array([])

    @abstractmethod
    def calc(self, output: Tensor, target: Tensor) -> np.ndarray or float:
        """
        Calculate metric by output from model and target

        :param output: output from model
        :param target: ground truth
        """

    def _calc(self, output: Tensor, target: Tensor):
        """
        Calculate metric by output from model and target. Method for internal use

        :param output: output from model
        :param target: ground truth
        """
        self._values = np.append(self._values, self.calc(output, target))

    def name(self) -> str:
        """
        Get name of metric

        :return: metric name
        """
        return self._name

    def get_values(self) -> np.ndarray:
        """
        Get array of metric values

        :return: array of values
        """
        return self._values

    def reset(self) -> None:
        """
        Reset array of metric values
        """
        self._values = np.array([])

    @staticmethod
    def min_val() -> float:
        """
        Get minimum value of metric. This used for correct histogram visualisation in some monitors
        :return: minimum value
        """
        return 0

    @staticmethod
    def max_val() -> float:
        """
        Get maximum value of metric. This used for correct histogram visualisation in some monitors
        :return: maximum value
        """
        return 1


class MetricsGroup:
    """
    Class for unite metrics or another :class:`MetricsGroup`'s in one namespace.
    Note: MetricsGroup may contain only 2 level of :class:`MetricsGroup`'s. So ``MetricsGroup().add(MetricsGroup().add(MetricsGroup()))``
    will raises :class:`MGException`

    :param name: group name. Name wil be used in monitors, so be careful in use unsupported characters
    """

    class MGException(Exception):
        """
        Exception for MetricsGroup
        """

        def __init__(self, msg: str):
            self.__msg = msg

        def __str__(self):
            return self.__msg

    def __init__(self, name: str):
        self.__name = name
        self.__metrics = []
        self.__metrics_groups = []
        self.__lvl = 1

    def add(self, item: AbstractMetric or 'MetricsGroup') -> 'MetricsGroup':
        """
        Add :class:`AbstractMetric` or :class:`MetricsGroup`

        :param item: object to add
        :return: self object
        :rtype: :class:`MetricsGroup`
        """
        if isinstance(item, type(self)):
            item._set_level(self.__lvl + 1)
            self.__metrics_groups.append(item)
        else:
            self.__metrics.append(item)
        return self

    def metrics(self) -> [AbstractMetric]:
        """
        Get list of metrics

        :return: list of metrics
        """
        return self.__metrics

    def groups(self) -> ['MetricsGroup']:
        """
        Get list of metrics groups

        :return: list of metrics groups
        """
        return self.__metrics_groups

    def name(self) -> str:
        """
        Get group name

        :return: name
        """
        return self.__name

    def have_groups(self) -> bool:
        """
        Is this group contains another metrics groups

        :return: True if contains, otherwise - False
        """
        return len(self.__metrics_groups) > 0

    def _set_level(self, level: int) -> None:
        """
        Internal method for set metrics group level
        TODO: if metrics group contains in two groups with different levels - this is undefined case

        :param level: parent group level
        """
        if level > 2:
            raise self.MGException("The metric group {} have {} level. There must be no more than 2 levels".format(self.__name, self.__lvl))
        self.__lvl = level
        for group in self.__metrics_groups:
            group._set_level(self.__lvl + 1)

    def calc(self, output: Tensor, target: Tensor) -> None:
        """
        Recursive calculate all metrics in this group and all nested group

        :param output: predict value
        :param target: target value
        """
        for metric in self.__metrics:
            metric._calc(output, target)
        for group in self.__metrics_groups:
            group.calc(output, target)

    def reset(self) -> None:
        """
        Recursive reset all metrics in this group and all nested group
        """
        for metric in self.__metrics:
            metric.reset()
        for group in self.__metrics_groups:
            group.reset()


class MetricsProcessor:
    """
    Collection for all :class:`AbstractMetric`'s and :class:`MetricsGroup`'s
    """

    def __init__(self):
        self._metrics = []
        self._metrics_groups = []

    def add_metric(self, metric: AbstractMetric) -> AbstractMetric:
        """
        Add :class:`AbstractMetric` object

        :param metric: metric to add
        :return: metric object
        :rtype: :class:`AbstractMetric`
        """
        self._metrics.append(metric)
        return metric

    def add_metrics_group(self, group: MetricsGroup) -> MetricsGroup:
        """
        Add :class:`MetricsGroup` object

        :param group: metrics group to add
        :return: metrics group object
        :rtype: :class:`MetricsGroup`
        """
        self._metrics_groups.append(group)
        return group

    def calc_metrics(self, output, target) -> None:
        """
        Recursive calculate all metrics

        :param output: predict value
        :param target: target value
        """
        for metric in self._metrics:
            metric.calc(output, target)
        for group in self._metrics_groups:
            group.calc(output, target)

    def reset_metrics(self) -> None:
        """
        Recursive reset all metrics values
        """
        for metric in self._metrics:
            metric.reset()
        for group in self._metrics_groups:
            group.reset()

    def get_metrics(self) -> {}:
        """
        Get metrics and groups as dict

        :return: dict of metrics and groups with keys [metrics, groups]
        """
        return {'metrics': self._metrics, 'groups': self._metrics_groups}


class AbstractStage(metaclass=ABCMeta):
    """
    Stage of training process. For example there may be 2 stages: train and validation.
    Every epochs in train loop is iteration by stages.

    :param name: name of stage
    """

    def __init__(self, name: str):
        self._name = name

    def name(self) -> str:
        """
        Get name of stage

        :return: name
        """
        return self._name

    def metrics_processor(self) -> MetricsProcessor or None:
        """
        Get metrics processor

        :return: :class:'MetricsProcessor` object or None
        """
        return None

    @abstractmethod
    def run(self, data_processor: TrainDataProcessor) -> None:
        """
        Run stage
        """

    def get_losses(self) -> np.ndarray or None:
        """
        Get losses from this stage

        :return: array of losses or None if this stage doesn't need losses
        """
        return None

    def on_epoch_end(self) -> None:
        """
        Callback for train epoch end
        """
        pass


class StandardStage(AbstractStage):
    """
    Standard stage for train process.

    When call :meth:`run` it's iterate :meth:`process_batch` of data processor by data loader

    After stop iteration ValidationStage accumulate losses from :class:`DataProcessor`.

    :param data_producer: :class:`DataProducer` object
    :param metrics_processor: :class:`MetricsProcessor`
    """

    def __init__(self, stage_name: str, is_train: bool, data_producer: DataProducer, metrics_processor: MetricsProcessor = None):
        super().__init__(name=stage_name)
        self.data_loader = data_producer.get_loader()
        self._metrics_processor = metrics_processor
        self._losses = None
        self._is_train = is_train

    def run(self, data_processor: TrainDataProcessor) -> None:
        """
        Run stage. This iterate by DataProducer and show progress in stdout

        :param data_processor: :class:`DataProcessor` object
        """
        with tqdm(self.data_loader, desc=self.name(), leave=False) as t:
            self._losses = None
            for batch in t:
                cur_loss = data_processor.process_batch(batch, metrics_processor=self.metrics_processor(), is_train=self._is_train)
                if self._losses is None:
                    self._losses = cur_loss
                else:
                    self._losses = np.append(self._losses, cur_loss)
                t.set_postfix({'loss': '[{:4f}]'.format(np.mean(self._losses))})

    def metrics_processor(self) -> MetricsProcessor or None:
        return self._metrics_processor

    def get_losses(self) -> np.ndarray:
        """
        Get losses from this stage

        :return: array of losses
        """
        return self._losses

    def on_epoch_end(self) -> None:
        self._losses = None
        self.metrics_processor().reset_metrics()


class TrainStage(StandardStage):
    """
    Standard training stage

    When call :meth:`run` it's iterate :meth:`process_batch` of data processor by data loader with ``is_tran=True`` flag.

    After stop iteration ValidationStage accumulate losses from :class:`DataProcessor`.

    :param data_producer: :class:`DataProducer` object
    :param metrics_processor: :class:`MetricsProcessor`
    """

    def __init__(self, data_producer: DataProducer, metrics_processor: MetricsProcessor = None):
        super().__init__('train', True, data_producer, metrics_processor)


class ValidationStage(StandardStage):
    """
    Standard validation stage.

    When call :meth:`run` it's iterate :meth:`process_batch` of data processor by data loader with ``is_tran=False`` flag.

    After stop iteration ValidationStage accumulate losses from :class:`DataProcessor`.

    :param data_producer: :class:`DataProducer` object
    :param metrics_processor: :class:`MetricsProcessor`
    """

    def __init__(self, data_producer: DataProducer, metrics_processor: MetricsProcessor = None):
        super().__init__('validation', False, data_producer, metrics_processor)


class TrainConfig:
    """
    Train process setting storage

    :param train_stages: list of stages for train loop
    :param loss: loss criterion
    :param optimizer: optimizer object
    :param experiment_name: name of experiment for difference from another experiments (e.g. visualisation)
    """

    def __init__(self, train_stages: [], loss: Module, optimizer: Optimizer, experiment_name: str):
        self._train_stages = train_stages
        self.__loss = loss
        self.__experiment_name = experiment_name
        self.__optimizer = optimizer

    def loss(self) -> Module:
        """
        Get loss object

        :return: loss object
        """
        return self.__loss

    def optimizer(self) -> Optimizer:
        """
        Get optimizer object

        :return: optimizer object
        """
        return self.__optimizer

    def experiment_name(self) -> str:
        """
        Get experiment name

        :return: experiment name
        """
        return self.__experiment_name

    def stages(self) -> [AbstractStage]:
        """
        Get list of stages

        :return: list of stages
        """
        return self._train_stages
