# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._history.utils.context_managers import LoggedExitStack, TrackFolders, CatchValidExits
from azureml._async.daemon import Daemon
from azureml._history.utils.context_managers import ContentUploader
from azureml._restclient.constants import RUN_ORIGIN
from azureml._logging import ChainedIdentity

from azureml.history._tracking import get_py_wd

import logging
import os
import errno

module_logger = logging.getLogger(__name__)


class BaseRunContext(ChainedIdentity):
    def __init__(self, run, **kwargs):
        super(BaseRunContext, self).__init__(**kwargs)
        self.run = run

    def __enter__(self):
        return self


class RunStatusContext(BaseRunContext):
    def __exit__(self, exit_type, value, traceback):
        if value is not None:
            self.run.fail()
        else:
            self.run.complete()


class RunHeartBeatContext(BaseRunContext):
    DEFAULT_INTERVAL_SEC = 30

    def __init__(self, run, interval_sec=DEFAULT_INTERVAL_SEC, **kwargs):
        super(RunHeartBeatContext, self).__init__(run, **kwargs)
        buffered_interval_sec = RunHeartBeatContext.buffered_interval(interval_sec)
        self._daemon = Daemon(work_func=run._heartbeat,
                              interval_sec=buffered_interval_sec,
                              _ident="RunHeartBeat",
                              _parent_logger=self._logger)

    @classmethod
    def buffered_interval(cls, interval_sec):
        return 4 * interval_sec / 5

    def __enter__(self):
        self._logger.debug("Started HeartBeat daemon")
        self._daemon.start()
        return self

    def __exit__(self, exit_type, value, traceback):
        self._logger.debug("Stopped HeartBeat daemon")
        self._daemon.stop()


class RunContextManager(BaseRunContext):
    def __init__(self, run, outputs=None, logs=None, heartbeat_enabled=True, **kwargs):
        super(RunContextManager, self).__init__(run, **kwargs)
        catch_valid_exits = CatchValidExits(_parent_logger=self._logger)
        self._status_context_manager = RunStatusContext(run, _parent_logger=self._logger)
        # Create the outputs directory if it does not exist
        if outputs is not None:
            try:
                os.makedirs(outputs)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
        py_wd = get_py_wd()
        outputs = [outputs] if outputs is not None else []

        # blacklist is empty
        self._output_file_context_manager = TrackFolders(py_wd, run, outputs, [])

        context_managers = [run._client.metrics,
                            catch_valid_exits,
                            self._status_context_manager,
                            self._output_file_context_manager]

        self.heartbeat_enabled = heartbeat_enabled
        if self.heartbeat_enabled:
            self._heartbeat_context_manager = RunHeartBeatContext(run, _parent_logger=self._logger)
            context_managers.append(self._heartbeat_context_manager)

        if logs is not None:
            self._logger.debug("Valid logs dir, setting up content loader")
            context_managers.append(self.get_content_uploader(logs))

        # python workingdirectory is last to preserve the original working directory
        self.context_manager = LoggedExitStack(self._logger, context_managers + [py_wd])

    def __enter__(self):
        self._logger.debug("Entered {}".format(self.__class__.__name__))
        return self.context_manager.__enter__()

    def __exit__(self, exit_type, value, traceback):
        self._logger.debug("Exited {}".format(self.__class__.__name__))
        return self.context_manager.__exit__(exit_type, value, traceback)

    @property
    def status_context_manager(self):
        return self._status_context_manager

    @property
    def output_file_context_manager(self):
        return self._output_file_context_manager

    @property
    def heartbeat_context_manager(self):
        return self._heartbeat_context_manager

    def get_content_uploader(self, logs_dir, **kwargs):
        return ContentUploader(RUN_ORIGIN,
                               self.run._data_container_id,
                               self.run._client.artifacts,
                               logspath=logs_dir, **kwargs)
