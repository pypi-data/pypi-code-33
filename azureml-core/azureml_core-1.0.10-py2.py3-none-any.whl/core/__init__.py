# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains core packages, modules and classes for Azure Machine Learning.

Main areas include managing compute targets, creating/managing workspaces and experiments, and submitting/accessing
model runs and run output/logging.
"""
from azureml.core.workspace import Workspace
from azureml.core.experiment import Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.core.script_run import ScriptRun
from azureml.core.run import Run, get_run
from azureml.core.datastore import Datastore
from azureml.core.script_run_config import ScriptRunConfig
from azureml.core.compute_target import (
    prepare_compute_target,
    is_compute_target_prepared,
    attach_legacy_compute_target,
    remove_legacy_compute_target)
from azureml.core.compute import ComputeTarget
from azureml.core.image import Image
from azureml.core.webservice import Webservice
from azureml._logging.debug_mode import diagnostic_log

from azureml._base_sdk_common import __version__ as VERSION

__version__ = VERSION

__all__ = [
    "Datastore",
    "Experiment",
    "Run",
    "RunConfiguration",
    "ScriptRun",
    "ScriptRunConfig",
    "Workspace",
    "prepare_compute_target",
    "is_compute_target_prepared",
    "attach_legacy_compute_target",
    "remove_legacy_compute_target",
    "ComputeTarget",
    "Image",
    "Webservice",
    "diagnostic_log",
    "get_run"
]

import azureml._base_sdk_common.user_agent as user_agent
user_agent.append("azureml-sdk-core", __version__)
