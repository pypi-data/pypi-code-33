# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os

from azureml._async import WorkerPool
from azureml._history.utils.constants import (OUTPUTS_DIR, LOGS_DIR, DRIVER_LOG_NAME,
                                              AZUREML_LOGS, AZUREML_LOG_FILE_NAME)
from azureml._history.utils.context_managers import (LoggedExitStack, RedirectUserOutputStreams, UploadLogsCM,
                                                     TrackFolders, CatchValidExits, SendRunKillSignal)

EXECUTION_ENV_FRAMEWORK = "AZUREML_FRAMEWORK"
EXECUTION_ENV_COMMUNICATOR = "AZUREML_COMMUNICATOR"
PY_SPARK_FRAMEWORK = "PySpark"
TARGET_TYPE_BATCH_AI = "batchai"

# This logger is actually for logs happening in this file
module_logger = logging.getLogger(__name__)

AZUREML_LOG_DIR = os.environ.get("AZUREML_LOGDIRECTORY_PATH", AZUREML_LOGS)
USER_LOG_PATH = os.path.join(AZUREML_LOG_DIR, DRIVER_LOG_NAME)


def get_history_context(callback, args, module_logger, track_folders=None, deny_list=None, **kwargs):
    return get_history_context_manager(track_folders=track_folders, deny_list=deny_list, **kwargs)


def get_history_context_manager(track_folders=None, deny_list=None, skip_track_logs_dir=False, **kwargs):
    # Configure logging for azureml namespace - debug logs+
    aml_logger = logging.getLogger('azureml')
    aml_logger.debug("Called azureml._history.utils.context_managers.get_history_context")

    # load the msrest logger to log requests and responses
    msrest_logger = logging.getLogger("msrest")

    aml_loggers = [aml_logger, msrest_logger]

    # Log inputs to simplify debugging remote runs
    inputs = ("Inputs:: kwargs: {kwargs}, "
              "track_folders: {track_folders}, "
              "deny_list: {deny_list}, "
              "skip_track_logs_dir: {skip_track_logs_dir}").format(kwargs=kwargs,
                                                                   track_folders=track_folders,
                                                                   deny_list=deny_list,
                                                                   skip_track_logs_dir=skip_track_logs_dir)
    aml_logger.debug(inputs)

    # Configure loggers to: log to known file, format logs, log at specified level
    # Send it to our log folder
    azureml_log_file_path = os.path.join(AZUREML_LOG_DIR, AZUREML_LOG_FILE_NAME)

    file_handler = logging.FileHandler(azureml_log_file_path)
    file_handler.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
    file_handler.setFormatter(formatter)

    # Also move this to RunConfig resolver
    LOG_LEVEL = int(os.environ.get("AZUREML_LOG_LEVEL", logging.DEBUG))

    for logger in aml_loggers:
        logger.setLevel(LOG_LEVEL)

        # This is not a great thing, but both revo and jupyter appear to add
        # root streamhandlers, causing too much information to be sent to the
        # user
        logger.propagate = 0

        logger.addHandler(file_handler)
    # Done configuring loggers

    track_folders = track_folders if track_folders is not None else []
    deny_list = deny_list if deny_list is not None else []

    os.environ["AZUREML_OUTPUT_DIRECTORY"] = OUTPUTS_DIR
    if not os.path.exists(OUTPUTS_DIR):
        os.mkdir(OUTPUTS_DIR)

    context_managers = []

    # Load run and related context managers
    py_wd_cm = get_py_wd()

    worker_pool = WorkerPool(_ident="HistoryTrackingWorkerPool", _parent_logger=aml_logger)

    # Enters the worker pool so that it's the last flushed element
    context_managers.append(worker_pool)
    # Catch sys.exit(0) - like signals from examples such as TF to avoid failing the run
    context_managers.append(CatchValidExits(_parent_logger=aml_logger))

    # Send the "about to be killed" signal so Runs can clean up quickly
    send_kill_signal = bool(os.environ.get("AZUREML_RUN_KILL_SIGNAL", "True"))
    kill_signal_timeout = float(os.environ.get("AZUREML_RUN_KILL_SIGNAL_TIMEOUT_SEC", "300"))
    context_managers.append(SendRunKillSignal(send_kill_signal, kill_signal_timeout))

    # Important! decompose here so we don't construct a run object
    from azureml.core.run import Run
    run = Run.get_context(_worker_pool=worker_pool, allow_offline=False)
    run_context_manager = run._context_manager

    # Send heartbeats if enabled
    if run_context_manager.heartbeat_enabled:
        context_managers.append(run_context_manager.heartbeat_context_manager)

    # TODO uncomment after fixed spark bug
    # from azureml._history.utils.daemon import ResourceMonitor
    # context_managers.append(ResourceMonitor("ResourceMonitor", aml_logger))

    target_type = os.environ.get("AZUREML_TARGET_TYPE")
    create_driver_log = target_type is None or target_type.lower() != TARGET_TYPE_BATCH_AI

    # Upload well-known log files ()
    context_managers.append(UploadLogsCM(aml_logger, run, DRIVER_LOG_NAME if create_driver_log else None,
                                         USER_LOG_PATH, azureml_log_file_path))
    # Upload the ./outputs folder and any extras we need
    context_managers.append(TrackFolders(py_wd_cm, run, track_folders + [OUTPUTS_DIR], deny_list + [USER_LOG_PATH]))
    # Inject the user's output streams for stream processing (log redirection, metric scraping)
    if create_driver_log:
        context_managers.append(RedirectUserOutputStreams(aml_logger, USER_LOG_PATH))

    if not skip_track_logs_dir:
        # Tail the logs folder to the cloud
        context_managers.append(run_context_manager.get_content_uploader(LOGS_DIR))

    # python working directory context manager is added last to ensure the
    # working directory before and after the user code is the same for all
    # the subsequent context managers
    return LoggedExitStack(aml_logger, context_managers + [py_wd_cm])


class PythonWorkingDirectory(object):
    _python_working_directory = None

    @classmethod
    def get(cls):
        logger = module_logger.getChild(cls.__name__)
        if cls._python_working_directory is None:
            fs_list = []
            from azureml._history.utils.filesystem import PythonFS
            py_fs = PythonFS('pyfs', logger)
            fs_list.append(py_fs)
            target_type = str(os.environ.get("AZUREML_TARGET_TYPE")).lower()
            logger.debug("Execution target type: {0}".format(target_type))
            try:
                from pyspark import SparkContext
                logger.debug("PySpark found in environment.")

                if SparkContext._active_spark_context is not None:
                    logger.debug("Adding SparkDFS")
                    from azureml._history.utils.filesystem import SparkDFS
                    spark_dfs = SparkDFS("spark_dfs", logger)
                    fs_list.append(spark_dfs)
                    logger.debug("Added SparkDFS")

                else:
                    if target_type == PY_SPARK_FRAMEWORK:
                        logger.warning("No active spark context with target type {}".format(target_type))

            except ImportError as import_error:
                logger.debug("Failed to import pyspark with error: {}".format(import_error))

            from azureml._history.utils.context_managers import WorkingDirectoryCM
            cls._python_working_directory = WorkingDirectoryCM(logger, fs_list)

        return cls._python_working_directory


def get_py_wd():
    return PythonWorkingDirectory.get()
