import logging
import os

from scotty.utils.base import BaseUtils
from scotty.core import settings

logger = logging.getLogger(__name__)


class ResultstoreUtils(BaseUtils):
    def __init__(self, context):
        try:
            self.current_resultstore = context.v1.resultstore
        except KeyError as e:
            logger.error('ResultStoreUtils can only used in resultstore context')
            raise

    @property
    def workloads(self):
        workloads = self._BaseUtils__experiment.components['workload']
        return workloads

    @property
    def remote_base_dir(self):
        return "scotty"

    @property
    def remote_experiment_dir(self):
        remote_experiment_dir = os.path.join(self.remote_base_dir, str(self.experiment_uuid))
        return remote_experiment_dir

    def local_result_dir(self, workload_name):
        local_result_dir = os.path.join('.scotty/data/workload', workload_name)
        return local_result_dir
