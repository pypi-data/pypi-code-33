# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from polyaxon_client.exceptions import PolyaxonClientException
from polyaxon_client.tracking import (
    Experiment,
    Job,
    get_data_paths,
    get_log_level,
    get_outputs_path,
    get_outputs_refs_paths
)

get_data_paths = get_data_paths
get_outputs_path = get_outputs_path
get_outputs_refs_paths = get_outputs_refs_paths
get_log_level = get_log_level

try:
    experiment = Experiment()
except PolyaxonClientException:
    experiment = None


def get_tf_config(envvar='TF_CONFIG'):
    """Returns the TF_CONFIG defining the cluster and the current task.

    if `envvar` is not null, it will set and env variable with `envvar`.
    """
    return Experiment.get_tf_config(envvar)


def get_cluster_def():
    """Returns cluster definition created by polyaxon.

    {
        "master": ["plxjob-master0-8eefb7a1146f476ca66e3bee9b88c1de:2000"],
        "worker": ["plxjob-worker1-8eefb7a1146f476ca66e3bee9b88c1de:2000",
                   "plxjob-worker2-8eefb7a1146f476ca66e3bee9b88c1de:2000"],
        "ps": ["plxjob-ps3-8eefb7a1146f476ca66e3bee9b88c1de:2000"],
    }

    :return: dict
    """
    return Experiment.get_cluster_def()


def get_declarations():
    """Returns all the experiment declarations based on both:

        * declarations section
        * matrix section
    """
    return Experiment.get_declarations()


def get_experiment_info():
    """Returns information about the experiment:
        * project_name
        * experiment_group_name
        * experiment_name
        * project_uuid
        * experiment_group_uuid
        * experiment_uuid
    """
    return Experiment.get_experiment_info()


def get_task_info():
    """Returns the task info: {"type": str, "index": int}."""
    return Experiment.get_task_info()


def get_job_info():
    """Returns information about the job:
        * project_name
        * job_name
        * project_uuid
        * job_uuid
        * role
        * type
        * app
    """
    return Job.get_job_info()


def send_metrics(**metrics):
    """Sends metrics to polyaxon api.

    Example:
        send_metric(precision=0.9, accuracy=0.89, loss=0.01)
    """
    experiment.log_metrics(**metrics)
