import logging
from datetime import datetime
import shutil
import sys
import functools

from scotty.workflows.base import Workflow
from scotty.core.components import ExperimentFactory
from scotty.core.executor import ExperimentCleanExecutor
from scotty.core.executor import ResourceExistsExecutor, ResourceEndpointExecutor
from scotty.core.executor import ResourceDeployExecutor, ResourceCleanExecutor
from scotty.core.executor import WorkloadRunExecutor, WorkloadCollectExecutor
from scotty.core.executor import WorkloadCleanExecutor
from scotty.core.executor import SystemCollectorCollectExecutor
from scotty.core.executor import ResultStoreSubmitExecutor

logger = logging.getLogger(__name__)


class ExperimentPerformWorkflow(Workflow):
    run_executors = [
        (ResourceExistsExecutor, 'Run resource.exists for all resources'),
        (ResourceDeployExecutor, 'Run resource.deploy for all resources'),
        (ResourceEndpointExecutor, 'Run resource.endpoint for all resources'),
        (SystemCollectorCollectExecutor, 'Run system state snapshot'),
        (WorkloadRunExecutor, 'Run workload.run for all workloads'),
        (WorkloadCollectExecutor, 'Run workload.collect for all workloads'),
        (ResultStoreSubmitExecutor, 'Transfer workload results to resultstore'),
    ]
    clean_executors = [
        (WorkloadCleanExecutor, 'Run workload.clean for all workloads'),
        (ResourceCleanExecutor, 'Run resource.clean for all resources'),
        (ExperimentCleanExecutor, 'Run experiment clean'),
    ]

    def _prepare(self):
        logger.info('Prepare experiment')
        self.experiment = ExperimentFactory.build(
            workspace_path=self._options.workspace,
            cfg_path=self._options.config
        )
        self.experiment.starttime = datetime.now()

    def _run(self):
        for executor_item in self.run_executors:
            self.perform(*executor_item)

    def perform(self, executor, info):
        logger.info(info)
        executor.perform(self.experiment)

    def _clean(self):
        for executor_item in self.clean_executors:
            self.perform(*executor_item)


class ExperimentCleanWorkflow(Workflow):
    def _prepare(self):
        self.experiment = ExperimentFactory.build(workspace_path=self._options.workspace)

    def _run(self):
        msg = ('Delete scotty path ({})')
        logger.info(msg.format(self.experiment.workspace.scotty_path))
        shutil.rmtree(self.experiment.workspace.scotty_path)

    def _clean(self):
        pass
