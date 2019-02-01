import sys
import importlib
import traceback
import multiprocessing
import concurrent.futures
from abc import abstractmethod
from concurrent.futures import (as_completed, 
                                ALL_COMPLETED, 
                                TimeoutError, 
                                CancelledError, 
                                wait)
import distributed.joblib
from dask.distributed import Client, LocalCluster
from dask import compute, delayed
from distributed import Worker
from joblib import Parallel, parallel_backend
from pickle import PicklingError
from tornado import gen
from ftk.exception import SchedulerException

class Scheduler:
    """
    Class that abstracts a scheduler. The scheduler will be used
    by compute backends such as "AzureBatchAICompute". This class will 
    contain a default implementation that is based off of 
    `Dask <https://distributed.readthedocs.io>`_.
    
    Additional design info: The dask scheduler has 3 actors - client, scheduler and worker.    
    The default scheduler implementation is based off distributed::LocalCluster.
    The LocalCluster uses the local machine as a compute resource and schedules dask jobs
    on worker processes.

    :param async:
        Flag to let know if the jobs submitted using this scheduler object
        will need asynchronous (non-blocking) jobs.
    :type async: boolean
    :param worker_count:
        Number of workers to create. Default is the number of cpus
        on the compute resource.
    :type worker_count: int

    """

    _job_scheduler = None
    _cluster = None  
    _async = True
    _is_initialized = False    
    _is_localcluster = False
    _requires_reinit = False    

    def __init__(self, async=True, worker_count=multiprocessing.cpu_count()):
        self._async = async
        # # Requires distributed 1.21.5 or greater. Otherwise runs into 
        # https://github.com/dask/distributed/issues/1879 on Windows envs.        
        self._cluster = LocalCluster(n_workers=worker_count, silence_logs=False)
        self._job_scheduler = Client(self._cluster, asynchronous=self._async)
        self._is_initialized = True
        self._is_localcluster = True
    
    @abstractmethod
    def __init_scheduler(self):
        """
        Initialize the scheduler. Classes that inherit from this class must override 
        this method and provide a valid init routine for cluster setup.
        This class implements default `distributed.LocalCluster`. 
        """
        if (self._job_scheduler and 
            self._is_localcluster and 
            (self._requires_reinit or not self._is_initialized)):
            self._job_scheduler.restart()

    @abstractmethod
    def __tear_down_scheduler(self):
        """
        Tear down the Client object that allows for
        scheduling jobs. 
        """
        if self._job_scheduler and self._is_localcluster:
            self._job_scheduler.close()
            self._requires_reinit = True        
    
    @abstractmethod    
    def schedule_job(self, func, data, *args, **func_params):
        """
        .. _distributed.Client.submit: http://dask.pydata.org/en/latest/futures.html#distributed.Client.submit

        Schedule job on a LocalCluster with a `distributed.Client.submit`_ call.
        The `*args` and `**kwargs` are passed to the func along with the 
        data.

        :param func:
            function that will be called to process a single task
            of any given type
        :type func: callable
        :param data:
            array-like, shape = [n_samples] or [n_samples, n_output], optional
            Target relative to X for classification or regression; None for
            unsupervised learning.
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param groups:
            array-like, with shape (n_samples,), optional
            Group labels for the samples used while splitting the dataset into
            train/test set.
        :type groups: array
        :param func_params: Parameters passed to the `func` method
        :type func_params: dict

        :returns: A tuple of <jobs, errors>.
        :rtype: tuple.
        
        """
        errors = list()
        _futures = list()
        try:
            # Init the client (introduce a flag to keep client)
            self.__init_scheduler()
             
            # Do work
            if self._is_localcluster and self._job_scheduler is not None:

                ## Option 1 
                #values = [delayed(func)(lvl, series_frame, *args, **kwargs) for (lvl, series_frame) in data]
                #results = compute(*values, get=self._job_scheduler.get)
                ##

                ## Option 2
                #self._job_scheduler.scatter(data)

                # Potentially use map on the groupedby data..
                #return self._job_scheduler.map(func, data_futures, pure=False)

                # Submit is a non-blocking call and returns immediately.                
                dask_params = {'pure': False}                
                kwargs = {**dask_params, **func_params}

                for (lvl, series_frame) in data:
                    try:
                        future = self._job_scheduler.submit(func, lvl, series_frame, *args, **kwargs)                        
                        if future.exception() is not None:
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            traceback.print_exc(limit=10, file=sys.stdout)
                            errors.append(future.exception())
                        else:
                            _futures.append(future)
                    except PicklingError as pkl_err:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exc(limit=10, file=sys.stdout)                        
                        errors.append(pkl_err)
                    except TypeError as typ_err:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exc(limit=10, file=sys.stdout)
                        errors.append(typ_err)
        except Exception as exc:
            self._requires_reinit = True
            return errors.append(exc)
        else:
            # Tear down client
            self.__tear_down_scheduler()
        return _futures or None, errors or None

    @abstractmethod    
    def schedule_job_with_scatter(self, func, data, data_map_func, **func_params):
        """
        Schedule job using data scatter pattern. In this case, the data is 
        split across all workers and computations proceed on those workers
        for whatever data they hold. A good use case for this would be CVSearch 
        workloads where the "fit" can avoid pushing data with every task (each combination
        in the grid space).
        
        :param func:
            function that will be called to process a single task
            of any given type
        :type func: callable
        :param data:
            array-like, shape = [n_samples] or [n_samples, n_output], optional
            Target relative to X for classification or regression; None for
            unsupervised learning.
        :type data: :class:`~ftk.time_series_data_frame.TimeSeriesDataFrame`
        :param groups: array-like, with shape (n_samples,), optional
        Group labels for the samples used while splitting the dataset into
        train/test set.
        :type groups: array
        :param func_params: Parameters passed to the `func` method
        :type func_params: dict        

        :returns: A tuple of <job results, errors>.
        :rtype: tuple.

        """
        errors = list()
        results = None
        try:
            # Init the client (introduce a flag to keep client)
            self.__init_scheduler()
            
            # Fetch scheduler ip and port. 
            # Required for initializing joblib backend
            scheduler_info = self._cluster.scheduler_address
            scheduler_ip = scheduler_info[scheduler_info.rfind('/') + 1: scheduler_info.rfind(':')]
            scheduler_port = scheduler_info[scheduler_info.rfind(':') + 1: len(scheduler_info)]

            # Do work
            if self._is_localcluster and self._job_scheduler is not None:
                
                # 1. Cannot pass data scatter param to parallel_backend: scatter = [data]
                # Results in serialization issues due to TSDF.                
                with parallel_backend('dask.distributed', 
                        scheduler_host="{}:{}".format(str(scheduler_ip), str(scheduler_port))):
                    results = ((func)(data, parameters, train, test, **func_params)
                                for parameters, (train, test) in data_map_func(data, **func_params))
                    
        except PicklingError as pkl_err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exc(limit=10, file=sys.stdout)                        
            errors.append(pkl_err)
        except TypeError as typ_err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exc(limit=10, file=sys.stdout)
            errors.append(typ_err)
        except Exception as exc:
            self._requires_reinit = True
            return errors.append(exc)

        else:
            # Tear down client
            self.__tear_down_scheduler()
        return results or None, errors or None

    @abstractmethod    
    def schedule_application_job(self, script_path, data, *args, **kwargs):
        """
        Execute an application job using a script.
        
        """
        raise NotImplementedError

    @abstractmethod
    @gen.coroutine
    def eval_jobs(self, futures):
        """
        Evaluate the result of the jobs. 
        Design info: In general, it is not recommended to communicate or fetch
        the result back, and that any "data" be left back on the workers for
        further processing. Light-weight results such as status of a function
        execution be brough back with no side-effects.

        :param futures: A list of futures to be evaluated
        :type futures: :class:`concurrent.futures`

        """
        results = list()
        errors = list()
        try:
            # Not a good idea except may be when running tests.
            if not self._async:
                concurrent.futures.wait(futures, timeout=None, return_when=ALL_COMPLETED)
            else:
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
            #results = self._job_scheduler.gather(futures, asynchronous = False)        
            #results = self._job_scheduler.gather(futures, asynchronous = False)
            #results = yield self._job_scheduler.gather(futures, asynchronous = self._async)
            #results = IOLoop.current().run_sync(lambda: self.__eval_job_result(futures))            
        except Exception as exc:
            errors.append(SchedulerException('%r generated an exception' % (exc)))
        else:
            return results or None, errors or None


class DistributedScheduler(Scheduler):
    """

    Class that abstracts a scheduler. The scheduler will be used 
    by compute backends such as "AzureBatchAICompute". This class will 
    contain a default implementation that is based off of 
    `Dask <https://distributed.readthedocs.io>`_.
    
    Additional design info: The dask scheduler has 3 actors - client, scheduler and worker.    
    The default scheduler implementation is based off distributed::LocalCluster.
    The LocalCluster uses the local machine as a compute resource and schedules dask jobs
    on worker processes.

    :param async: Flag to let know if the jobs submitted using this scheduler object
    will need asynchronous (non-blocking) jobs.
    :type async: boolean
    :param worker_count: Number of workers to create. Default is the number of cpus 
    on the compute resource.
    :type worker_count: int

    """

    _job_scheduler = None
    _cluster = None  
    _async = True
    _is_initialized = False
    _requires_reinit = False    

    def __init__(self, run_config, prepare_cluster=True, async=True):
        self._async = async
        self._is_initialized = True
        self._is_localcluster = True
    
    @abstractmethod
    def __init_scheduler(self):
        """
        Initialize the scheduler. Classes that inherit from this class must override 
        this method and provide a valid init routine for cluster setup.
        This class implements default `distributed.LocalCluster`. 
        """
        if (self._job_scheduler and             
            (self._requires_reinit or not self._is_initialized)):
            self._job_scheduler.restart()

    @abstractmethod
    def __tear_down_scheduler(self):
        """
        Tear down the Client object that allows for
        scheduling jobs. 
        """
        if self._job_scheduler is not None:
            self._job_scheduler.close()
            self._requires_reinit = True        
    
    @abstractmethod    
    def schedule_job(self, func, data, *args, **func_params):
        """
        Schedule job on a LocalCluster with a :func:`distributed.Client.submit` call. 
        The `*args` and `**kwargs` are passed to the func along with the 
        data.

        :param func: function that will be called to process a single task 
        of any given type
        :type func: callable
        :param data: array-like, shape = [n_samples] or [n_samples, n_output], optional
        Target relative to X for classification or regression; None for unsupervised learning.
        :type data: :class:`ftk.dataframe_ts.TimeSeriesDataFrame`
        :param groups: array-like, with shape (n_samples,), optional
        Group labels for the samples used while splitting the dataset into
        train/test set.
        :type groups: array
        :param func_params: Parameters passed to the `func` method
        :type func_params: dict

        :returns: A tuple of <jobs, errors>.
        :rtype: tuple.
        
        """
        errors = list()
        _futures = list()
        try:
            # Init the client (introduce a flag to keep client)
            self.__init_scheduler()
             
            # Do work
            if self._is_localcluster and self._job_scheduler is not None:

                ## Option 1 
                #values = [delayed(func)(lvl, series_frame, *args, **kwargs) for (lvl, series_frame) in data]
                #results = compute(*values, get=self._job_scheduler.get)
                ##

                ## Option 2
                #self._job_scheduler.scatter(data)

                # Potentially use map on the groupedby data..
                #return self._job_scheduler.map(func, data_futures, pure=False)

                # Submit is a non-blocking call and returns immediately.                
                dask_params = {'pure': False}                
                kwargs = {**dask_params, **func_params}

                for (lvl, series_frame) in data:
                    try:
                        future = self._job_scheduler.submit(func, lvl, series_frame, *args, **kwargs)                        
                        if future.exception() is not None:
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            traceback.print_exc(limit=10, file=sys.stdout)
                            errors.append(future.exception())
                        else:
                            _futures.append(future)
                    except PicklingError as pkl_err:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exc(limit=10, file=sys.stdout)                        
                        errors.append(pkl_err)
                    except TypeError as typ_err:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exc(limit=10, file=sys.stdout)
                        errors.append(typ_err)
        except Exception as exc:
            self._requires_reinit = True
            return errors.append(exc)
        else:
            # Tear down client
            self.__tear_down_scheduler()
        return _futures or None, errors or None

    @abstractmethod    
    def schedule_job_with_scatter(self, func, data, data_map_func, **func_params):
        """
        Schedule job using data scatter pattern. In this case, the data is 
        split across all workers and computations proceed on those workers
        for whatever data they hold. A good use case for this would be CVSearch 
        workloads where the "fit" can avoid pushing data with every task (each combination
        in the grid space).
        
        :param func: function that will be called to process a single task 
        of any given type
        :type func: callable
        :param data: array-like, shape = [n_samples] or [n_samples, n_output], optional
        Target relative to X for classification or regression; None for unsupervised learning.
        :type data: :class:`ftk.dataframe_ts.TimeSeriesDataFrame`
        :param groups: array-like, with shape (n_samples,), optional
        Group labels for the samples used while splitting the dataset into
        train/test set.
        :type groups: array
        :param func_params: Parameters passed to the `func` method
        :type func_params: dict        

        :returns: A tuple of <job results, errors>.
        :rtype: tuple.

        """
        errors = list()
        results = None
        try:
            # Init the client (introduce a flag to keep client)
            self.__init_scheduler()
            
            # Fetch scheduler ip and port. 
            # Required for initializing joblib backend
            scheduler_info = self._cluster.scheduler_address
            scheduler_ip = scheduler_info[scheduler_info.rfind('/') + 1: scheduler_info.rfind(':')]
            scheduler_port = scheduler_info[scheduler_info.rfind(':') + 1: len(scheduler_info)]

            # Do work
            if self._is_localcluster and self._job_scheduler is not None:
                
                # 1. Cannot pass data scatter param to parallel_backend: scatter = [data]
                # Results in serialization issues due to TSDF.                
                with parallel_backend('dask.distributed', 
                        scheduler_host="{}:{}".format(str(scheduler_ip), str(scheduler_port))):
                    results = ((func)(data, parameters, train, test, **func_params)
                                for parameters, (train, test) in data_map_func(data, **func_params))
                    
        except PicklingError as pkl_err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exc(limit=10, file=sys.stdout)                        
            errors.append(pkl_err)
        except TypeError as typ_err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exc(limit=10, file=sys.stdout)
            errors.append(typ_err)
        except Exception as exc:
            self._requires_reinit = True
            return errors.append(exc)

        else:
            # Tear down client
            self.__tear_down_scheduler()
        return results or None, errors or None

    @abstractmethod    
    def schedule_application_job(self, script_path, data, *args, **kwargs):
        """
        Execute an application job using a script.
        
        """
        raise NotImplementedError

    @abstractmethod
    @gen.coroutine
    def eval_jobs(self, futures):
        """
        Evaluate the result of the jobs. 
        Design info: In general, it is not recommended to communicate or fetch the result back,
        and that any "data" be left back on the workers for further processing. Light-weight results
        such as status of a function execution be brough back with no side-effects.

        :param futures: A list of futures to be evaluated
        :type futures: :class:`concurrent.futures`

        """
        results = list()
        errors = list()
        try:
            # Not a good idea except may be when running tests.
            if not self._async:
                concurrent.futures.wait(futures, timeout=None, return_when=ALL_COMPLETED)
            else:
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
            #results = self._job_scheduler.gather(futures, asynchronous = False)        
            #results = self._job_scheduler.gather(futures, asynchronous = False)
            #results = yield self._job_scheduler.gather(futures, asynchronous = self._async)
            #results = IOLoop.current().run_sync(lambda: self.__eval_job_result(futures))            
        except Exception as exc:
            errors.append(SchedulerException('%r generated an exception' % (exc)))
        else:
            return results or None, errors or None