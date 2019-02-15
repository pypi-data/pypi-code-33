import logging
import os

logger = logging.getLogger(__name__)


class BaseUtils(object):
    def __init__(self, context):
        self.context = context
        self.__experiment = context.v1._ContextV1__experiment
        self.basepath = self.__experiment.workspace.path
        self._init(context)

    def _init(self, context):
        pass

    @property
    def experiment_uuid(self):
        return self.__experiment.uuid

    @property
    def experiment_workspace(self):
        return self.__experiment.workspace

    def _real_path(self, path):
        basename = os.path.basename(os.path.normpath(path))
        return os.path.join(self.basepath, basename)

    def open_file(self, path, mode):
        real_path = self._real_path(path)
        return open(real_path, mode)

    def exists_file(self, path):
        real_path = self._real_path(path)
        return os.path.isfile(real_path)
