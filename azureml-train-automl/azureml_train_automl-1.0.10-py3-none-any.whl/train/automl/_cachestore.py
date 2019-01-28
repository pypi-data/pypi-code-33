# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for automl cache store."""
import logging
import os
import sys  # noqa F401 # dynamically evaluated to get caller
import tempfile
import uuid
import copy

from abc import ABC, abstractmethod

from azureml import _async
from azureml._vendor.azure_storage.file import FileService, models, ContentSettings
from azureml.telemetry.activity import log_activity
from automl.client.core.common.pickler import DefaultPickler

# default task timeout
DEFAULT_TASK_TIMEOUT_SECONDS = 900


class _CacheStore(ABC):
    """ABC for cache store."""

    def __init__(self, path=None, max_retries=3, module_logger=logging.getLogger()):
        """
        Cache store constructor.

        :param path: path of the store
        :param max_retries: max retries to get/put from/to store
        :param module_logger: logger
        """
        self.path = path
        self.cache_items = dict()
        self.max_retries = max_retries
        self.module_logger = module_logger

    @abstractmethod
    def load(self):
        """Load - abstract method."""
        pass

    @abstractmethod
    def unload(self):
        """Unload - abstract method."""
        pass

    def add(self, keys, values):
        """Add to store.

        :param keys: store key
        :param values: store value
        """
        for k, v in zip(keys, values):
            self.cache_items[k] = v

    def add_or_get(self, key, value):
        """
        Add or get from store.

        :param key: store key
        :param value: store value
        :return: value
        """
        val = self.cache_items.get(key, None)
        if val is not None:
            return val

        self.add([key], [value])
        return value

    def get(self, keys, default=None):
        """
        Get value from store.

        :param default: default value
        :param keys: store keys
        :return: values
        """
        vals = dict()
        for k in keys:
            vals[k] = self.cache_items.get(k, default)

        return vals

    def set(self, key, value):
        """
        Set value to store.

        :param key: store key
        :param value: store value
        """
        self.add([key], [value])

    def remove(self, key):
        """
        Remove from store.

        :param key: store key
        """
        obj = self.cache_items.pop(key)
        del obj

    def remove_all(self):
        """Remove all entry from store."""
        for k, v in self.cache_items.items():
            del v

        self.cache_items.clear()

    def __iter__(self):
        """
        Store iterator.

        :return: cache items
        """
        return iter(self.cache_items.items())

    @staticmethod
    def _function_with_retry(fn, max_retries, logger, *args, **kwargs):
        """
        Call function with retry capability.

        :param fn: function to be executed
        :param max_retries: number of retries
        :param logger: logger
        :param args: args
        :param kwargs: kwargs
        :return: Exception if failure, otherwise returns value from function call
        """
        retry_count = 0
        ex = None
        while retry_count < max_retries:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.warning("Execution failed {}".format(e))
                ex = e
            finally:
                retry_count += 1

        raise ex


class _MemoryCacheStore(_CacheStore):
    """MemoryCacheStore - stores value in memory."""

    def __init__(self, path=None):
        """Constructor."""
        super(_MemoryCacheStore, self).__init__(path=path)

    def __getstate__(self):
        return {'module_logger': None,
                'path': self.path,
                'cache_items': self.cache_items,
                'max_retries': self.max_retries}

    def __setstate__(self, state):
        self.module_logger = logging.getLogger()
        self.path = state['path']
        self.cache_items = state['cache_items']
        self.max_retries = state['max_retries']

    def load(self):
        """Load from memory - NoOp."""
        pass

    def add(self, keys, values):
        """
        adds to store by creating a deep copy
        :param keys: store key
        :param values: store value
        """
        for k, v in zip(keys, values):
            self.cache_items[k] = copy.deepcopy(v)

    def unload(self):
        """Unload from memory."""
        self.cache_items.clear()


class _AzureFileCacheStore(_CacheStore):
    """Cache store based on azure file system."""

    def __init__(self, path,
                 account_name=None,
                 account_key=None,
                 pickler=None,
                 task_timeout=DEFAULT_TASK_TIMEOUT_SECONDS,
                 module_logger=logging.getLogger(__name__),
                 temp_location=None
                 ):
        """
        Cache based on azure file system.

        :param path: path of the store
        :param account_name: account name
        :param account_key: account key
        :param pickler: pickler, default is cPickler
        :param task_timeout: task timeout
        :param module_logger: logger
        """
        super(_AzureFileCacheStore, self).__init__()

        if pickler is None:
            pickler = DefaultPickler()

        self.task_timeout = task_timeout
        self.pickler = pickler
        self.account_name = account_name
        self.account_key = account_key
        self.cache_items = dict()
        self._num_workers = os.cpu_count()
        self.module_logger = module_logger
        self.temp_location = _create_temp_dir(temp_location)
        self.activity_prefix = "_AzureFileCacheStore"
        self.file_service = FileService(account_name=account_name,
                                        account_key=account_key)
        self.path = path.lower().replace('_', '-')
        self.file_service.create_share(self.path)

    def __getstate__(self):
        return {'task_timeout': self.task_timeout,
                'pickler': self.pickler,
                'account_name': self.account_name,
                'account_key': self.account_key,
                'cache_items': self.cache_items,
                'num_workers': self._num_workers,
                'module_logger': None,
                'temp_location': self.temp_location,
                'activity_prefix': self.activity_prefix,
                'file_service': self.file_service,
                'path': self.path,
                'max_retries': self.max_retries}

    def __setstate__(self, state):
        self.file_service = state['file_service']
        self.path = state['path']
        self.pickler = state['pickler']
        self.account_name = state['account_name']
        self.account_key = state['account_key']
        self.cache_items = state['cache_items']
        self._num_workers = state['num_workers']
        self.module_logger = logging.getLogger()
        self.temp_location = _create_temp_dir()
        self.activity_prefix = state['activity_prefix']
        self.task_timeout = state['task_timeout']
        self.max_retries = state['max_retries']

    def add(self, keys, values):
        """Add to azure file store.

        :param keys: keys
        :param values: values
        """
        worker_pool = _async.WorkerPool(max_workers=self._num_workers)
        tasks = []
        with _log_activity(logger=self.module_logger):
            with _async.TaskQueue(worker_pool=worker_pool, _ident=__name__,
                                  flush_timeout_seconds=self.task_timeout,
                                  _parent_logger=self.module_logger) as tq:
                for k, v in zip(keys, values):
                    tasks.append(tq.add(self._function_with_retry,
                                        self._upload,
                                        self.max_retries,
                                        self.module_logger,
                                        k,
                                        v))

            map(lambda task: task.wait(), tasks)
            worker_pool.shutdown()

    def add_or_get(self, key, value):
        """
        Add or gets from azure file store.

        :param key:
        :param value:
        :return: unpickled value
        """
        val = self.cache_items.get(key, None)
        if val is None:
            self.add([key], [value])
            return {key: value}

        return self.get([key], None)

    def get(self, keys, default=None):
        """
        Get from azure file store & unpickles.

        :param default: default value
        :param keys: store key
        :return: unpickled object
        """
        worker_pool = _async.WorkerPool(max_workers=self._num_workers)
        tasks = []
        with _log_activity(logger=self.module_logger):
            with _async.TaskQueue(worker_pool=worker_pool, _ident=__name__,
                                  flush_timeout_seconds=self.task_timeout,
                                  _parent_logger=self.module_logger) as tq:
                for key in keys:
                    tasks.append(tq.add(self._function_with_retry,
                                        self._download_file,
                                        self.max_retries,
                                        self.module_logger,
                                        key))

            results = map(lambda task: task.wait(), tasks)
            worker_pool.shutdown()
            ret = dict()
            pickle_exception = None
            for result in results:
                try:
                    for key, val in result.items():
                        obj = default
                        if val is not None:
                            try:
                                obj = self.pickler.load(val)
                                self.cache_items[key] = key
                            finally:
                                self._try_remove_temp_file(path=val)
                        ret[key] = obj
                except Exception as e:
                    self.module_logger.warning("Pickle error {}".format(e))
                    pickle_exception = e

            if pickle_exception is not None:
                raise CacheException("Cache failure {}".format(pickle_exception))

        return ret

    def set(self, key, value):
        """
        Set values to store.

        :param key: key
        :param value: value
        """
        self.add(key, value)

    def remove(self, key):
        """
        Remove from store.

        :param key: store key
        """
        with _log_activity(logger=self.module_logger):
            self._remove(self.path, [key])

    def remove_all(self):
        """Remove all the file from cache."""
        with _log_activity(logger=self.module_logger):
            self._remove(self.path, self.cache_items.keys())

    def load(self):
        """Load from azure file store."""
        worker_pool = _async.WorkerPool(max_workers=self._num_workers)
        tasks = []
        with _log_activity(logger=self.module_logger):
            with _async.TaskQueue(worker_pool=worker_pool, _ident=__name__,
                                  flush_timeout_seconds=self.task_timeout,
                                  _parent_logger=self.module_logger) as tq:
                tasks.append(tq.add(self._function_with_retry,
                                    self._get_azure_file_lists,
                                    self.max_retries,
                                    self.module_logger,
                                    self.path))

            map(lambda task: task.wait(), tasks)
            worker_pool.shutdown()

    def unload(self):
        """Unload the cache."""
        try:
            self.file_service.delete_share(share_name=self.path)
        except Exception as e:
            self.module_logger.warning("Failed to delete share {}, {}".format(self.path, e))

        self.cache_items.clear()
        _try_remove_dir(self.temp_location)

    def _remove(self, path, files):
        worker_pool = _async.WorkerPool(max_workers=self._num_workers)
        tasks = []

        with _async.TaskQueue(worker_pool=worker_pool, _ident=__name__,
                              flush_timeout_seconds=self.task_timeout,
                              _parent_logger=self.module_logger) as tq:
            for file in files:
                tasks.append(tq.add(self._function_with_retry,
                                    self._remove_from_azrue_file_store,
                                    self.max_retries,
                                    self.module_logger,
                                    path,
                                    file))

        map(lambda task: task.wait(), tasks)
        worker_pool.shutdown()

    def _remove_from_azrue_file_store(self, path, key):
        self.file_service.delete_file(path, directory_name=None, file_name=key)
        self.cache_items.pop(key)

    def _get_azure_file_lists(self, path):
        """
        Get list of files available from azure file store. similar to dir.

        :param path: path
        """
        for dir_or_file in self.file_service.list_directories_and_files(share_name=path):
            if isinstance(dir_or_file, models.File):
                self.cache_items[dir_or_file.name] = dir_or_file.name

    def _download_file(self, file):
        """
        Download from azure file store.

        :param file:
        """
        temp_path = os.path.join(self.temp_location, file)
        try:
            self.file_service.get_file_to_path(share_name=self.path,
                                               directory_name=None,
                                               file_name=file,
                                               file_path=temp_path)
            self.cache_items[file] = temp_path
        except Exception:
            # get_file_to_path created temp file if file doesnt exists
            self._try_remove_temp_file(temp_path)
            raise

        return {file: temp_path}

    def _upload(self, file, obj):
        temp_path = os.path.join(self.temp_location, file)
        try:
            self.pickler.dump(obj, temp_path)
            self.file_service.create_file_from_path(share_name=self.path,
                                                    file_name=file,
                                                    directory_name=None,
                                                    content_settings=ContentSettings('application/x-binary'),
                                                    local_file_path=temp_path)
            self.cache_items[file] = file
        finally:
            self._try_remove_temp_file(temp_path)

    def _try_remove_temp_file(self, path):
        try:
            os.remove(path)
        except OSError as e:
            self.module_logger.warning("failed to remove temp file {}".format(e))

    def __del__(self):
        _try_remove_dir(self.temp_location)


class _FileCacheStore(_CacheStore):
    """FileCacheStore - cache store based on file system."""

    def __init__(self, path=None, pickler=None,
                 task_timeout=DEFAULT_TASK_TIMEOUT_SECONDS,
                 module_logger=None):
        """
        File based cache store - constructor.

        :param path: store path
        :param pickler: pickler, defaults to cPickler
        :param task_timeout: task timeout
        :param module_logger:
        """
        super(_FileCacheStore, self).__init__()

        if pickler is None:
            pickler = DefaultPickler()

        self.task_timeout = task_timeout
        self.pickler = pickler
        self.module_logger = module_logger
        self._num_workers = os.cpu_count()
        self.path = path
        if not path:
            self.path = _create_temp_dir()

    def __getstate__(self):
        return {'pickler': self.pickler,
                'task_timeout': self.task_timeout,
                'module_logger': None,
                'num_workers': self._num_workers,
                'path': self.path,
                'cache_items': self.cache_items,
                'max_retries': self.max_retries}

    def __setstate__(self, state):
        self.pickler = state['pickler']
        self.module_logger = logging.getLogger()
        self._num_workers = state['num_workers']
        self.path = state['path']
        self.cache_items = state['cache_items']
        self.max_retries = state['max_retries']
        self.task_timeout = state['task_timeout']

    def log_debug_messages(self, message):
        """
        Log a message in the logfile.

        :param message: message to be logged
        """
        if self.module_logger:
            self.module_logger.info(message)

    def add(self, keys, values):
        """
        Pickles the object and adds to cache.

        :param keys: store keys
        :param values: store values
        """
        with _log_activity(logger=self.module_logger):
            for k, v in zip(keys, values):
                self.log_debug_messages("Uploading key: " + k)
                self._upload(k, v)

    def add_or_get(self, key, value):
        """
        Add or gets from the store.

        :param key: store key
        :param value: store value
        :return: UnPickled object
        """
        val = self.cache_items.get(key, None)
        if val is not None:
            return self.get([key])

        self.add([key], [value])
        return value

    def get(self, keys, default=None):
        """
        Get unpickled object from store.

        :param keys: store keys
        :param default: returns default value if not present
        :return: unpickled objects
        """
        res = dict()

        with _log_activity(logger=self.module_logger):
            for key in keys:
                path = self.cache_items.get(key, None)
                obj = default
                self.log_debug_messages("Getting data for key: " + key)
                if path is not None:
                    obj = self.pickler.load(path)
                res[key] = obj

        return res

    def set(self, key, value):
        """
        Set to store.

        :param key: store key
        :param value: store value
        """
        self.add([key], [value])

    def remove(self, key):
        """
        Remove from store.

        :param key: store key
        """
        with _log_activity(logger=self.module_logger):
            try:
                self.log_debug_messages("Deleting data for key: " + key)
                self.cache_items.pop(key)
                self._delete_file(key)
            except Exception as e:
                self.module_logger.warning("remove from store failed {}".format(e))

    def remove_all(self):
        """Remove all the cache from store."""
        length = self.cache_items.__len__()

        worker_pool = _async.WorkerPool(max_workers=self._num_workers)
        tasks = []
        with _log_activity(logger=self.module_logger):
            with _async.TaskQueue(worker_pool=worker_pool,
                                  flush_timeout_seconds=self.task_timeout,
                                  _ident=__name__,
                                  _parent_logger=self.module_logger) as tq:
                while length > 0:
                    length -= 1
                    k, v = self.cache_items.popitem()
                    tasks.append(tq.add(self._delete_file, k))

            map(lambda task: task.wait(), tasks)
            worker_pool.shutdown()

    def load(self):
        """Load from store."""
        self.log_debug_messages("Loading from file cache")
        with _log_activity(logger=self.module_logger):
            for f in os.listdir(self.path):
                if self.pickler.is_meta_file(f):
                    path = os.path.join(self.path, f)
                    val = self.pickler.get_name_without_extn(path)
                    key = self.pickler.get_name_without_extn(f)
                    self.cache_items[key] = val

    def unload(self):
        """Unload from store."""
        # load to make sure all the meta files are loaded
        self.load()

        self.log_debug_messages("UnLoading from file cache")
        self.remove_all()
        _try_remove_dir(self.path)

    def _upload(self, key, obj):
        try:
            path = os.path.join(self.path, key)
            self.pickler.dump(obj, path=path)
            self.cache_items[key] = path
            self.log_debug_messages("Uploaded key: " + key)
        except Exception as e:
            self.module_logger.error("Uploading {} failed with {}".format(key, e))
            raise

    def _delete_file(self, k):
        try:
            path = os.path.join(self.path, k)
            chunk_files = self.pickler.get_pickle_files(path)
            for chunk_file in chunk_files:
                os.remove(chunk_file)
        except Exception as e:
            self.module_logger.warning("remove from store failed {}".format(e))


def _create_temp_dir(temp_location=None):
    """
    Create temp dir.

    :return: temp location
    """
    try:
        return tempfile.mkdtemp(dir=temp_location)
    except OSError as e:
        raise CacheException("Failed to create temp folder {}. You can disable the "
                             "cache if space is concern. Setting to disable cache enable_cache=False".format(e))


def _try_remove_dir(path):
    """
    Remove directory.

    :param path: path to be removed
    """
    try:
        os.rmdir(path)
    except OSError:
        return False

    return True


def _log_activity(logger, custom_dimensions=None):
    """
    Log activity collects the execution latency.

    :param logger: logger
    :param custom_dimensions: custom telemetry dimensions
    :return: log activity
    """
    get_frame_expr = 'sys._getframe({}).f_code.co_name'
    caller = eval(get_frame_expr.format(2))
    telemetry_values = dict()
    telemetry_values['caller'] = caller

    if custom_dimensions is not None:
        telemetry_values.update(custom_dimensions)

    return log_activity(logger=logger, activity_name=caller, custom_dimensions=telemetry_values)


class CacheException(Exception):
    """Cache exceptions."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(CacheException, self).__init__(*args, **kwargs)
