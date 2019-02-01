from warnings import warn
import distributed.joblib
from ftk.factor_types import ComputeJobType
from ftk.exception import (ComputeException,
                           JobTypeNotSupportedException,
                           DataFrameProcessingException)
from ftk.verify import Messages
from .compute_base import (ComputeStrategyMixin, ComputeBase)
from .scheduler import Scheduler


class DaskDistributedCompute(ComputeBase):
    """
    Provides capabilities to execute compute jobs on distributed compute backends.
    This compute requires a scheduler of type :class:`~ftk.compute.scheduler.Scheduler`
    for job scheduling. 
    This scheduler is applicable to scenarios where you bring/manage your own dask cluster.
    The scheduler leverages `Distributed <https://distributed.readthedocs.io>`_ . 
     
    :param scheduler: The scheduler that will be used to execute the jobs.         
    :type scheduler: :class:`~ftk.compute.scheduler.Scheduler`
    :param execution_mode_async:
        Mode of execution. If several jobs are expected to be queued
        concurrently, use execution_mode_async. For obtaining results
        in a synchronous fashion, set this flag to false.
    :type execution_mode_async: boolean

    """
    def __init__(self, scheduler=None, execution_mode_async=True):
        super().__init__()

        # The default scheduler for distributed compute is based
        # off of the Dask distributed's LocalCluster. This
        # abstracts worker processes by spinning local Python sub-processes.
        if scheduler is None:
            self.scheduler = Scheduler(async=execution_mode_async)
        else:
            self.scheduler = scheduler

    # pylint: disable=no-member
    @ComputeBase.jobs.setter
    def jobs(self, val):
        self._jobs = val

    @ComputeBase.job_results.setter
    def job_results(self, val):
        if self._job_results is None:
            self._job_results = list()
        self._job_results.append(val)

    @ComputeBase.summary.setter
    def summary(self, val):
        if self._summary is None:
            self._summary = list()
        self._summary.append(val)

    @ComputeBase.errors.setter
    def errors(self, val):
        if self._errors is None:
            self._errors = list()
        self._errors.append(val)    

    @ComputeBase.scheduler.setter
    def scheduler(self, val):
        """
        A scheduler is required for this backend since we run it
        on the current node itself with plain joblib APIs.
        """
        if not isinstance(val, Scheduler):
            raise ComputeException(Messages.SCHEDULER_INVALID)
        self._scheduler = val

    def state(self):
        """
        Check state of the compute backend. For this compute backend
        there is nothing to validate. No-op by returning true.
        """
        return True    

    def execute_job(self, func, data, data_map_func, job_type, *args, **kwargs):
        """
        Execute a job using Azure Batch AI compute backend.
        
        :param func:
            Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data:
            Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type func: Callable.
        :param args:
            List of arguments to be passed to the func.
        :type args: list.
        :param kwargs:
            Keyword arguments to be passed to the func.
        :type args: dict.

        :returns: self.
        :rtype: object.

        :raises TypeError: If callable func and data_map_func are not passed.
        :raises JobTypeNotSupportedException: If job type is not supported.
        """
        # Validate params
        if not callable(func):
            raise TypeError(Messages.PARAM_MUST_BE_CALLABLE.format('func'))

        if data_map_func is not None and not callable(data_map_func):
            raise TypeError(Messages.PARAM_MUST_BE_CALLABLE.format('data_map_func'))
        
        if job_type is None or not isinstance(job_type, ComputeJobType):
            raise JobTypeNotSupportedException(str(job_type))
        
        # Execute different job types.
        if job_type is ComputeJobType.Fit:
            return self.__process_train_job(func, data, data_map_func, *args, **kwargs)
        if job_type is ComputeJobType.CVSearch:
            return self.__process_cvsearch_job(func, data, data_map_func, **kwargs)
        else:
            raise JobTypeNotSupportedException(Messages.JOB_TYPE_NOT_SUPPORTED.format(str(job_type)))
    
    def execute_task_job(self, func, job_type, tasks, *func_args, **func_kwargs):        
        raise ComputeException(Messages.EXECUTE_TASK_JOB_NOT_SUPPORTED)

    def __process_train_job(self, func, data, data_map_func, *args, **kwargs):
        """
        Function that executes job of type - ComputeJobType.Fit.

        :param func:
            Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data:
            Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type func: Callable.
        :param args:
            List of arguments to be passed to the func.
        :type args: list.
        :param kwargs:
            Keyword arguments to be passed to the func.
        :type args: dict.

        :returns: self.
        :rtype: object.

        :raises ComputeException: If inputs are invalid.
        """        
        if not self.state() is True:
            raise ComputeException(Messages.COMPUTE_ERROR_STATE_INVALID)

        if func is None:
            raise ComputeException(Messages.FUNC_PARAM_NOT_SPECIFIED)

        if data is None:
            raise ComputeException(Messages.DATA_PARAM_NOT_SPECIFIED)

        if data_map_func is None:
            raise ComputeException(Messages.MAPPER_FUNC_PARAM_NOT_SPECIFIED)

        try:
            # The schedule_job method returns a tuple - <valid job futures, errors>
            # Simply pass along the errors and eval only the valid futures.
            self.jobs, __schedule_errors = self.scheduler.schedule_job(func, data, *args, **kwargs)
            if __schedule_errors is not None:
                self.errors = __schedule_errors

            # If running jobs exist, then call eval_jobs method.
            # It returns a tuple - <results, errors>.
            # Append errors and save results.
            if self.jobs is not None:
                results, __eval_errors = self.scheduler.eval_jobs(self.jobs)
                if __eval_errors is not None:
                    self.errors = __eval_errors
                if results is not None:
                    self.job_results = results
            else:
                warn('No DaskDistributedCompute jobs were submitted. '
                     + 'Inspect errors to ensure that no errors were encountered.')
        except Exception as exc:
            self.errors = exc
        return self

    def __process_cvsearch_job(self, func, data, data_map_func, **kwargs):
        """
        Function that executes job of type - ComputeJobType.CVSearch.

        :param func: Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data: Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type func: Callable.
        :param args: List of arguments to be passed to the func.
        :type args: list.
        :param kwargs: Keyword arguments to be passed to the func.
        :type args: dict.

        :returns: self.
        :rtype: object.

        :raises ComputeException: If inputs are invalid.
        """
        if not self.state() is True:
            raise ComputeException(Messages.COMPUTE_ERROR_STATE_INVALID)

        if func is None:
            raise ComputeException(Messages.FUNC_PARAM_NOT_SPECIFIED)

        if data is None:
            raise ComputeException(Messages.DATA_PARAM_NOT_SPECIFIED)

        try:
            # The schedule_job method returns a tuple - <valid job futures, errors>
            # Simply pass along the errors and eval only the valid futures.
            self.job_results, __job_errors = self.scheduler.schedule_job_with_scatter(
                                                     func,                            
                                                     data,
                                                     data_map_func,
                                                     **kwargs)
            if __job_errors is not None:
                self.errors = __job_errors            
        except Exception as exc:
            self.errors = exc
        return self
