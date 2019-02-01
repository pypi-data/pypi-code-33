from abc import ABC, abstractmethod
from ftk.verify import Messages
from ftk.exception import (ComputeTypeException,
                           ComputeException,
                           DataFrameProcessingException)
from ftk.factor_types import ComputeJobType


class ComputeStrategyMixin(object):
    """
    Mixin that adds a compute strategy capability to the inheriting class.
    The classes that will inherit this mixin are the ones that need any sort of large scale processing
    capability. 
     
    :param compute_strategy:
        An object that will be used to execute jobs. Expected to be concrete instance
        of type :class:`ftk.compute.compute_base.ComputeBase`
    :type compute_strategy: :class:`ComputeBase`    

    """    
    _compute_strategy = None        

    def __init__(self, compute_strategy=None):
        self._compute_strategy = compute_strategy        

    @property
    def compute_strategy(self):
        return self._compute_strategy

    @compute_strategy.setter
    def compute_strategy(self, val):
        if not isinstance(val, ComputeBase):
            raise ComputeTypeException(Messages.COMPUTE_STRATEGY_MUST_INHERIT_BASE)
        else:
            self._compute_strategy = val

    def execute_job(self, func, data, data_map_func, job_type, *args, **kwargs):
        """
        A generic function to execute a compute job that will used by inheritors
        of this mixin class.

        :param func: Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data: Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type data_map_func: Callable.
        :param job_type: Type of job passed by the caller so that the compute backends 
        appropriately handle it.
        :type job_type: :class:`~ftk.factortypes.ComputeJobType`
        :param args: List of arguments to be passed to the func.
        :type args: list.
        :param kwargs: Keyword arguments to be passed to the func.
        :type args: dict.
        :returns: self.
        :rtype: object.
        """
        if not callable(func):
            raise TypeError("First input to map must be a callable function")

        if job_type is None or not isinstance(job_type, ComputeJobType):
            raise Exception("A valid job type must be specified")

        if self._compute_strategy is None:
            raise ComputeTypeException(Messages.COMPUTE_STRATEGY_INVALID)       
        
        return self._compute_strategy.execute_job(func, data, data_map_func, job_type, *args, **kwargs)

    def execute_task_job(self, func, job_type, tasks, *func_args, **func_kwargs):
        """
        A generic function to execute a compute job that will used by inheritors
        of this mixin class.

        :param func: Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param job_type: Type of job passed by the caller so that the compute backends 
                        appropriately handle it.
        :type job_type: :class:`~ftk.factortypes.ComputeJobType`
        :param tasks: Iterable of tasks to execute.
        :type tasks: list.
        :param func_args: Name arguments to pass to ```func```.
        :type func_args: list
        :param func_kwargs: Keyword arguments to be passed to the func.
        :type func_kwargs: dict.
        :returns: self.
        :rtype: object.
        """
        if not callable(func):
            raise TypeError("First input to map must be a callable function")

        if job_type is None or not isinstance(job_type, ComputeJobType):
            raise Exception("A valid job type must be specified")

        if self._compute_strategy is None:
            raise ComputeTypeException(Messages.COMPUTE_STRATEGY_INVALID)       
        
        return self._compute_strategy.execute_task_job(func, job_type, tasks, *func_args, **func_kwargs)

class ComputeBase(ABC):
    """
    Abstract Base Class for all compute backends supported by Forecasting Toolkit.
    
    :ivar scheduler:
        A scheduler to execute a "job". The concrete compute backends
        may or may not support a scheduler.
    :ivar summary:
        The summary of an execution. It is expected the concrete compute classes
        clear the summary before each job is executed.
    :ivar jobs:
        An object that represents a set of executing jobs. It is generally
        recommended that concrete implementors set this to be a list of
        futures that can be queried for completion and other statistics.
    :ivar job_results: An object that represents the result from the jobs. 
    :ivar errors: A list of errors that are reported by a compute backend during execution.

    """ 
    _scheduler = None
    _summary = None
    _jobs = None
    _job_results = None
    _errors = list()

    def __init__(self):        
        super().__init__()        

    @property    
    def scheduler(self):
        return self._scheduler

    @scheduler.setter
    @abstractmethod
    def scheduler(self, val):
        pass

    @property    
    def summary(self):
        return self._summary

    @summary.setter
    @abstractmethod
    def summary(self, val):
        pass

    @property    
    def jobs(self):
        return self._jobs

    @jobs.setter
    @abstractmethod
    def jobs(self, val):
        pass

    @property    
    def job_results(self):
        return self._job_results

    @job_results.setter
    @abstractmethod
    def job_results(self, val):
        pass

    @property    
    def errors(self):
        return self._errors

    @errors.setter
    @abstractmethod
    def errors(self, val):
        pass

    @abstractmethod
    def execute_job(self, func, data, data_map_func, job_type, *args, **kwargs):
        """
        Execute a job using the scheduler specified. All concrete compute backends
        must implement this method.
        """
        raise ComputeException(Messages.COMPUTE_MUST_IMPLEMENT_EXECUTE_JOB)

    @abstractmethod
    def execute_task_job(self, func, job_type, tasks, *func_args, **func_kwargs):
        """
        Execute a set of task bound jobs. All compute backends must implement this.
        """
        pass
    
    @abstractmethod
    def state(self):
        """
        Implement this method to indicate the state/status of the 
        concrete backend. Processing will be gated on this field.
        Default is False so a valid implementation must be provided 
        by derived classes.
        """
        return False
