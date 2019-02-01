import sys
import warnings
import traceback
import multiprocessing
import concurrent.futures
from collections import Iterable
from itertools import repeat
from joblib import Parallel, delayed

from ftk.exception import (ComputeException,
                           JobTypeNotSupportedException,
                           DataFrameProcessingException)
from ftk.factor_types import ComputeJobType
from ftk.verify import Messages
from .compute_base import (ComputeStrategyMixin, ComputeBase)


class JoblibParallelCompute(ComputeBase):
    """
    A compute strategy that utilizes "joblib" to parallelize compute requests. 
    This strategy class can be used when the tasks are expected to run within 
    a single compute resource - such as a VM or a physical machine.

    :param job_count: Number of parallel jobs to create for a backend. Defaults to 
        available number of CPUs :func:`multiprocessing.cpu_count`
    :type job_count: int
    :param backend: Type of backend to use. 
    :type backend: string 

    """
    def __init__(self, job_count=multiprocessing.cpu_count(), backend="threading"):
        self._job_count = job_count
        self._backend = backend
        super().__init__()

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
        No scheduler is required for this backend since we run it
        on the current node itself with plain joblib APIs.
        """
        self._scheduler = None

    def state(self):
        """
        Nothing to validate for concurrent jobs backend.
        Simply return true.
        """
        return True

    def execute_experiment(self, job_type, **kwargs):       
        raise NotImplementedError

    def execute_job(self, func, data, data_map_func, job_type, *args, **kwargs):
        """
        Execute a job using Joblib. 
        
        :param func:
            Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data: Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type data_map_func: Callable.
        :param job_type:
            Type of job passed by the caller so that the compute backends
            appropriately handle it.
        :type job_type: :class:`~ftk.factortypes.ComputeJobType`
        :param args: List of arguments to be passed to the func.
        :type args: list.
        :param kwargs: Keyword arguments to be passed to the func.
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
        
        # Process different jobs based on type.
        if job_type is ComputeJobType.Fit:
            return self.__process_train_job(func, data, data_map_func, *args, **kwargs)
        elif job_type is ComputeJobType.CVSearch:
            return self.__process_cvsearch_job(func, data, data_map_func, **kwargs)                               
        else:
            raise JobTypeNotSupportedException(Messages.JOB_TYPE_NOT_SUPPORTED.format(str(job_type)))
    
    def execute_task_job(self, func, job_type, tasks, *func_args, **func_kwargs):
        raise ComputeException(Messages.EXECUTE_TASK_JOB_NOT_SUPPORTED)

    def __process_train_job(self, func, data, data_map_func, *args, **kwargs):
        """
        Execute model train jobs using joblib. This is essentially a 
        "blocking" API and no futures are created/returned. 

       :param func: Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data: Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type data_map_func: Callable.
        :param args: List of arguments to be passed to the func.
        :type args: list.
        :param kwargs: Keyword arguments to be passed to the func.
        :type args: dict.

        :returns: self.
        :rtype: object.

        :raises ComputeException: Raised if input parameters are invalid.
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
            self._job_results = \
                Parallel(self._job_count, backend=self._backend)(
                    delayed(func)(lvl, series_frame, *args, **kwargs)
                    for lvl, series_frame in data)
        except Exception as exc:
            self.errors = exc
        return self

    def __process_cvsearch_job(self, func, data, data_map_func, **kwargs):
        """
        Execute cross-validation search jobs using joblib. This is essentially a 
        "blocking" API and no futures are created/returned. 

       :param func: Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data: Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func: Function that takes in the data and splits it into 
        chunks appropriately for processing. 
        :type data_map_func: Callable.
        :param args: List of arguments to be passed to the func.
        :type args: list.
        :param kwargs: Keyword arguments to be passed to the func.
        :type args: dict.
        :returns: self.
        :rtype: object.

        :raises ComputeException: Raised if input parameters are invalid.
        """
        if not self.state() is True:
            raise ComputeException(Messages.COMPUTE_ERROR_STATE_INVALID)

        if func is None:
            raise ComputeException(Messages.FUNC_PARAM_NOT_SPECIFIED)

        if data is None:
            raise ComputeException(Messages.DATA_PARAM_NOT_SPECIFIED)

        try:
            self.job_results = Parallel(n_jobs=1, 
                                        backend=self._backend, 
                                        verbose=10)(delayed(func)
                    (data, parameters, train, test, **kwargs)
                    for parameters, (train, test) in data_map_func(data, **kwargs))

        except TypeError as typ_err:
            self.errors = typ_err
        except Exception as exc:
            self.errors = exc
        return self


class ConcurrentFuturesCompute(ComputeBase):
    """
    A compute strategy that utilizes ::class:`concurrent.futures` to parallelize
    compute request. The concurrent.futures library allows thread based and process based
    execution options for work partitioning. 
    
    :param threads:
        Number of threads to use for processing. Defaults to
        available number of CPUs :func:`multiprocessing.cpu_count`
    :type threads: int    
    
    """
    def __init__(self, threads=multiprocessing.cpu_count()):        
        self._threads = threads        
        super().__init__()

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
        No scheduler is required for this backend since we run it
        on the current node itself with plain joblib APIs.
        """
        self._scheduler = None

    def state(self):
        """        
        Check state of the compute backend. For this compute backend
        there is nothing to validate. No-op by returning true.        
        """
        return True

    def execute_experiment(self, job_type, **kwargs):        
        raise NotImplementedError

    def execute_job(self, func, data, data_map_func, job_type, *args, **kwargs):
        """
        Execute a job using :class:`concurrent.futures`. Only supports job of type
        ComputeJobType.Fit
        
        :param func: Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data: Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type data_map_func: Callable.
        :param job_type:
            Type of job passed by the caller so that the compute backends
            appropriately handle it.
        :type job_type: :class:`~ftk.factor_types.ComputeJobType`
        :param args: List of arguments to be passed to the func.
        :type args: list.
        :param kwargs: Keyword arguments to be passed to the func.
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
        
        # Process different jobs based on job type
        if job_type is ComputeJobType.Fit:
            return self.__process_train_job(func, data, data_map_func, *args, **kwargs)
        else:
            raise JobTypeNotSupportedException(Messages.JOB_TYPE_NOT_SUPPORTED.format(str(job_type)))
    
    def execute_task_job(self, func, job_type, tasks, *func_args, **func_kwargs):
        """
        Executes a set of tasks using :class:`concurrent.futures.ProcessPoolExecutor`. 
        To schedule tasks provide a callback function that will be called with each item in the
        iterable provided along with any keyword argument that you may pass to the callable.
        Supports job of type :const:`~ftk.factor_types.ComputeJobType.ForecasterUnion`
        
        :param func: Function to processes a single task. Passed by the caller.
        :type func: callable.
        :type job_type: Job type.
        :param job_type: :class:`~ftk.factor_types.ComputeJobType`
        :param tasks: Iterable of tasks.
        :type tasks: list.        
        :param func_kwargs: Keyword arguments to be passed to the func.
        :type func_kwargs: dict.
        :param func_kwargs: Keyword arguments to be passed to the func.
        :type func_kwargs: dict.
        :returns: self.
        :rtype: :class:`~ftk.compute.scale_up_compute.ConcurrentFuturesCompute`

        :raises TypeError: If ```func``` is not a callable.
        :raises JobTypeNotSupportedException: If job type is not supported.
        """
        # Validate params
        if not self.state() is True:
            raise ComputeException(Messages.COMPUTE_ERROR_STATE_INVALID)

        if not callable(func):
            raise TypeError(Messages.PARAM_MUST_BE_CALLABLE.format('func'))        
        
        # Only supports ForecasterUnion. Enable other types as needed.
        if job_type is None or job_type is not ComputeJobType.ForecasterUnion:            
            raise JobTypeNotSupportedException(Messages.JOB_TYPE_NOT_SUPPORTED.format(str(job_type)))        
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._threads) as executor:

            # In this case, the iterable is the first parameter to the function and you have other positional or keyword
            # args in addition (such as the one in ForecasterUnion).
            if tasks is not None and isinstance(tasks, Iterable):
                if (func_args is not None and len(func_args) != 0) and (func_kwargs is not None and len(func_kwargs) != 0):
                    self.jobs = [executor.submit(func, (task, *func_args), **func_kwargs) for task in tasks]
                elif (func_args is not None and len(func_args) != 0) and (func_kwargs is None or len(func_kwargs) == 0):
                    self.jobs = [executor.submit(func, (task, *func_args)) for task in tasks]
                elif (func_args is None or len(func_args) == 0) and (func_kwargs is not None and len(func_kwargs) != 0):
                    self.jobs = [executor.submit(func, task, **func_kwargs) for task in tasks]
                else:
                    self.jobs = [executor.submit(func, task) for task in tasks]
            
            
            # We assume range-repeated function calls (where range is len(tasks)) that sprays 
            # *args and **kwargs.
            elif tasks is not None and isinstance(tasks, int):                
                if func_args is not None and func_kwargs is not None:
                    self.jobs = [executor.map(func, repeat(*func_args), repeat(**func_kwargs)) for _ in range(tasks)]
                elif func_args is not None and func_kwargs is None:
                    self.jobs = [executor.map(func, repeat(**func_kwargs)) for _ in range(tasks)]
                elif func_args is None and func_kwargs is not None:
                    self.jobs = [executor.map(func, repeat(*func_args)) for _ in range(tasks)]
                else:
                    self.jobs = [executor.map(func) for _ in range(tasks)]

            # Check we do have jobs
            if self.jobs is None or len(self.jobs) == 0:
                warnings.warn('No jobs were found.')

            # Process jobs
            else:
                # Wait until all jobs complete (no timeout)
                completed_futures, incomplete_futures = concurrent.futures.wait(self.jobs)
            
                # There should be no incomplete futures. We'll just throw a warning for now.
                if incomplete_futures is not None and len(incomplete_futures) > 0:
                    warnings.warn('ConcurrentFuturesCompute: Some tasks were not complete')

                # Unwrap each future and assign error if any or the result.
                for future in completed_futures:
                    if future._exception is not None:
                        self.errors = future._exception
                    else:
                        self.job_results = future.result()            
        return self

    def __process_train_job(self, func, data, data_map_func, *args, **kwargs):
        """
        Execute model training job with :class:`concurrent.futures.ThreadPoolExecutor`
        
        :param func: Function to processes a single item. passed by the caller.
        :type func: Callable.
        :param data: Dataframe to be processed
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param data_map_func:
            Function that takes in the data and splits it into
            chunks appropriately for processing.
        :type data_map_func: Callable.
        :param args: List of arguments to be passed to the func.
        :type args: list.
        :param kwargs: Keyword arguments to be passed to the func.
        :type args: dict.

        :returns: self.
        :rtype: object.

        :raises ComputeException: Raised if input parameters are invalid.
        """
        if not self.state() is True:
            raise ComputeException(Messages.COMPUTE_ERROR_STATE_INVALID)

        if func is None:
            raise ComputeException(Messages.FUNC_PARAM_NOT_SPECIFIED)

        if data is None:
            raise ComputeException(Messages.DATA_PARAM_NOT_SPECIFIED)

        if data_map_func is None:
            raise ComputeException(Messages.MAPPER_FUNC_PARAM_NOT_SPECIFIED)
    
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._threads) as executor:            
            jobs_future_list = {executor.submit(func, lvl, series_frame, *args, **kwargs)
                                for (lvl, series_frame) in data}
            self.jobs = jobs_future_list
            for future in concurrent.futures.as_completed(jobs_future_list):
                try:
                    result = future.result()
                    if result is not None:
                        self.job_results = result
                except concurrent.futures.CancelledError as canceled:
                    self.errors = DataFrameProcessingException('concurrent.futures.CancelledError: %s' % (canceled))
                except concurrent.futures.TimeoutError as timeout:
                    self.errors = DataFrameProcessingException('concurrent.futures.TimeoutError: %s' % (timeout))
                except Exception as exc:
                    self.errors = DataFrameProcessingException('Exception: %s' % (exc))                    
        return self