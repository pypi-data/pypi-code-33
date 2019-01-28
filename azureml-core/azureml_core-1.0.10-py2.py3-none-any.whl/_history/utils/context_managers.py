# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from __future__ import print_function
from azureml._history.utils.log_scope import LogScope

import six
import logging
import os
import sys
import traceback
from azureml._run_impl.file_watcher import FileWatcher
from azureml._logging import ChainedIdentity

if six.PY2:
    from contextlib2 import ExitStack
else:
    from contextlib import ExitStack


class OutputCollector(object):
    def __init__(self, stream, processor):
        self._inner = stream
        self.processor = processor

    def write(self, buf):
        self.processor(buf)
        self._inner.write(buf)

    def __getattr__(self, name):
        return getattr(self._inner, name)


class LoggedExitStack(object):
    def __init__(self, logger, context_managers=None):
        self._logger = logger
        self._exit_stack = ExitStack()

        # TODO make this cleaner, types would be nice
        context_managers = context_managers if context_managers is not None else []

        self.context_managers = (context_managers if isinstance(context_managers, list)
                                 else [context_managers])

    def __enter__(self):
        self._exit_stack.__enter__()
        for context_manager in self.context_managers:
            self._exit_stack.enter_context(LogScope(self._logger,
                                                    context_manager.__class__.__name__))
            self._exit_stack.enter_context(context_manager)
        return self

    def __exit__(self, *args):
        return self._exit_stack.__exit__(*args)


class WorkingDirectoryCM(object):
    def __init__(self, logger, fs_list):
        ids = [fs.ident() for fs in fs_list]
        if len(ids) != len(set(ids)):
            raise Exception("Fs ids are not unique: {}".format(ids))

        self.logger = logger.getChild("workingdir")
        self.fs_list = fs_list
        self.prev_paths = {fs.ident(): None for fs in fs_list}
        self.logger.debug("Pinning working directory for filesystems: {0}".format(list(self.prev_paths.keys())))

    def __enter__(self):
        self.logger.debug("[START]")
        for fs in self.fs_list:
            path = fs.get_abs_working_dir()
            self.logger.debug("Calling {}".format(fs.ident()))
            self.logger.debug("Storing working dir for {0} as {1}".format(fs.ident(), path))
            self.prev_paths[fs.ident()] = path
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for fs in self.fs_list:
            self.logger.debug("Calling {}".format(fs.ident()))
            path = fs.get_abs_working_dir()
            old_path = self.prev_paths[fs.ident()]
            if path != old_path:
                self.logger.debug("{} has path {}".format(fs.ident(), path))
            self.logger.debug("Reverting working dir from {0} to {1}".format(path, old_path))
            fs.set_working_dir(old_path)
        self.logger.debug("[STOP]")
        return False

    def track(self, run_tracker, track_folders, blacklist):
        self.logger.debug("Uploading tracked directories: {0}, excluding {1}".format(track_folders, blacklist))
        for fs in self.fs_list:
            self.logger.debug("Calling track for {}".format(fs.ident()))
            fs.track(run_tracker, track_folders, blacklist)
        return True


class RedirectUserOutputStreams(object):
    def __init__(self, logger, user_log_path):
        self.user_log_path = user_log_path
        self.logger = logger

    def __enter__(self):
        self.logger.debug("Redirecting user output to {0}".format(self.user_log_path))
        self.user_log_fp = open(self.user_log_path, "wt")
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = OutputCollector(sys.stdout, self.user_log_fp.write)
        sys.stderr = OutputCollector(sys.stderr, self.user_log_fp.write)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_val:
                # The default traceback.print_exc() expects a file-like object which
                # OutputCollector is not. Instead manually print the exception details
                # to the wrapped sys.stderr by using an intermediate string.
                # trace = traceback.format_tb(exc_tb)
                trace = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
                print(trace, file=sys.stderr)
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

            self.user_log_fp.close()
            self.logger.debug("User scope execution complete.")


class TrackFolders(object):
    def __init__(self, py_wd, run_tracker, trackfolders, blacklist):
        self.py_wd = py_wd
        self.run_tracker = run_tracker
        self.trackfolders = trackfolders
        self.blacklist = blacklist

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.py_wd.track(self.run_tracker, self.trackfolders, self.blacklist)


class SendRunKillSignal(object):
    def __init__(self, send_kill_signal=True, kill_signal_timeout=40):
        self._send_signal = send_kill_signal
        self._kill_timeout = kill_signal_timeout

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._send_signal:
            # Saddest thing in the world - cyclic dependency
            from azureml._run_impl.run_base import _RunBase
            _RunBase._kill(timeout=self._kill_timeout)


class UploadLogsCM(object):
    def __init__(self, logger, run_tracker, driver_log_name, user_log_path, azureml_log_file_path):
        self.azureml_log_file_path = azureml_log_file_path
        self.user_log_path = user_log_path
        self.driver_log_name = driver_log_name
        self.run_tracker = run_tracker
        self.logger = logger

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Uploading driver log")
        if self.driver_log_name is not None:
            self.run_tracker.upload_file(self.driver_log_name, self.user_log_path)
        self._upload_azureml_log()

    def _upload_azureml_log(self):
        has_azureml_log_file = os.path.exists(self.azureml_log_file_path)
        self.logger.debug("has_azureml_log_file is {}".format(has_azureml_log_file))
        if has_azureml_log_file:
            self.logger.debug("azureml.log path is {}".format(self.azureml_log_file_path))
            self.run_tracker.upload_file(self.azureml_log_file_path,
                                         self.azureml_log_file_path)


class ContentUploader(object):
    def __init__(self, origin, container, artifacts_client, logspath, parallelism=None):
        self.origin = origin
        self.container = container
        self.artifacts_client = artifacts_client
        self.logspath = logspath
        self.threads = []
        self.logger = logging.getLogger(__name__)
        self.parallelism = parallelism

    def __enter__(self):
        # create a thread to watch files
        self.logger.debug("starting file watcher")
        self.file_watcher = FileWatcher(self.logspath,
                                        self.origin,
                                        self.container,
                                        self.artifacts_client,
                                        self.logger,
                                        parallelism=self.parallelism)
        self.file_watcher.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("exiting ContentUploader, waiting for file_watcher to finish upload...")
        self.file_watcher.finish()
        self.file_watcher.join()
        self.logger.debug("file watcher exited")


class CatchValidExits(ChainedIdentity):
    def __enter__(self):
        self._logger.debug("Entered {}".format(self.__class__.__name__))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == SystemExit:
            return exc_val.code is None or exc_val.code == 0
