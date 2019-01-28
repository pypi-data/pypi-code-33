# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating ensembles from previous Automated Machine Learning iterations."""

import os
from sklearn.base import BaseEstimator

from azureml import _async
from azureml.core import Experiment, Workspace, Run
from azureml.core.compute import ComputeTarget

from . import _automl_settings
from . import constants
from . import _logging
from ._vendor.automl.client.core.common import logging_utilities as log_utils
from ._vendor.automl.client.core.common import ensemble_base


class Ensemble(BaseEstimator, ensemble_base.EnsembleBase):
    """
    Class for ensembling previous AutoML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    """

    DEFAULT_DOWNLOAD_MODELS_TIMEOUT_IN_SEC = 5 * 60  # 5 minutes

    def __init__(self,
                 automl_settings,
                 ensemble_run_id: str,
                 experiment_name: str,
                 workspace_name: str,
                 subscription_id: str,
                 resource_group_name: str):
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        Arguments:
            automl_settings -- The settings for this current experiment
            ensemble_run_id -- The id of the current ensembling run
            experiment_name -- The name of the current Azure ML experiment
            workspace_name --  The name of the current Azure ML workspace where the experiment is run
            subscription_id --  The id of the current Azure ML subscription where the experiment is run
            resource_group_name --  The name of the current Azure resource group
        """
        # input validation
        if automl_settings is None:
            raise ValueError("automl_settings parameter should not be None")

        if ensemble_run_id is None:
            raise ValueError("ensemble_run_id parameter should not be None")

        if experiment_name is None:
            raise ValueError("experiment_name parameter should not be None")

        if subscription_id is None:
            raise ValueError("subscription_id parameter should not be None")

        if resource_group_name is None:
            raise ValueError("resource_group_name parameter should not be None")

        if workspace_name is None:
            raise ValueError("workspace_name parameter should not be None")

        super().__init__(automl_settings)
        self._ensemble_run_id = ensemble_run_id
        self._experiment_name = experiment_name
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name

        self.estimator = None

        # for potentially large models, we should allow users to override this timeout
        if hasattr(self._automl_settings, "ensemble_download_models_timeout_sec"):
            self._download_models_timeout_sec = self._automl_settings.ensemble_download_models_timeout_sec
        else:
            self._download_models_timeout_sec = Ensemble.DEFAULT_DOWNLOAD_MODELS_TIMEOUT_IN_SEC

    def _download_fitted_models_for_child_runs(self, logger, child_runs, model_remote_path):
        """Override the base implementation for downloading the fitted pipelines in an async manner.

        :param logger -- logger instance
        :param child_runs -- collection of child runs for which we need to download the pipelines
        :param model_remote_path -- the remote path where we're downloading the pipelines from
        """
        with _async.WorkerPool() as worker_pool:
            task_queue = _async.TaskQueue(worker_pool=worker_pool,
                                          _ident="download_fitted_models",
                                          _parent_logger=logger)
            index = 0
            tasks = []
            for run in child_runs:
                task = task_queue.add(ensemble_base.EnsembleBase._download_model, run, index, model_remote_path)
                tasks.append(task)
                index += 1

            task_queue.flush(source=task_queue.identity, timeout_seconds=self._download_models_timeout_sec)
            return task_queue.results

    def _get_ensemble_and_parent_run(self):
        parent_run_id_length = self._ensemble_run_id.rindex("_")
        parent_run_id = self._ensemble_run_id[0:parent_run_id_length]

        is_remote_run = self._automl_settings.compute_target is not None\
            and self._automl_settings.compute_target != 'local'
        if is_remote_run or self._automl_settings.spark_service:
            # for remote runs/azure databricks (spark cluster) we want to reuse the auth token from the
            # environment variables
            ensemble_run = Run.get_context()
            parent_run = Run(ensemble_run.experiment, parent_run_id)
        else:
            # For local runs
            workspace = Workspace(self._subscription_id, self._resource_group_name, self._workspace_name)
            experiment = Experiment(workspace, self._experiment_name)
            ensemble_run = Run(experiment, self._ensemble_run_id)
            parent_run = Run(experiment, parent_run_id)

        return ensemble_run, parent_run

    def _get_logger(self):
        if (self._automl_settings.compute_target is not None and self._automl_settings.compute_target != 'local') or \
                not os.path.exists(self._automl_settings.debug_log):
            logger = _logging.get_logger(None, self._automl_settings.verbosity)
        else:
            logger = _logging.get_logger(self._automl_settings.debug_log, self._automl_settings.verbosity)

        return logger
