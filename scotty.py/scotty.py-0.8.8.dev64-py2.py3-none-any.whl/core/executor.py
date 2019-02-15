from datetime import datetime
import logging
import pickle
import sys
from concurrent import futures

from scotty.core.checkout import CheckoutManager
from scotty.core.moduleloader import ModuleLoader
from scotty.core.components import CommonComponentState
from scotty.core.exceptions import ScottyException
from scotty.core.context import Context


logger = logging.getLogger(__name__)


def exec_component(experiment, component, interface_, result_interface):
    logger.info('Execute {} {} for {}'.format(component.type, interface_, component.name))
    component_task = ComponentTask(experiment, component, interface_)
    result = component_task.run()
    if result_interface:
        setattr(component, result_interface, result)
    return component


class ComponentTask(object):
    def __init__(self, experiment, component, interface_):
        self.experiment = experiment
        self.component = component
        self.interface_ = interface_
        self.populate_component()
        self.component_module = self.load_component_module()

    def populate_component(self):
        try:
            CheckoutManager.populate(self.component, self.experiment.workspace.path)
        except Exception:
            self._log_component_exception()

    def load_component_module(self):
        try:
            component_module = ModuleLoader.load_by_component(self.component)
            return component_module
        except Exception:
            self._log_component_exception()

    def run(self):
        if not self.component_module:
            return
        with self.experiment.workspace.cwd():
            context = Context(self.component, self.experiment)
            function_ = self._get_function()
            result = self._exec_function(function_, context)
            if self.component.state == CommonComponentState.ERROR:
                self.experiment.state = CommonComponentState.ERROR
            return result

    def _get_function(self):
        try:
            function_ = getattr(self.component_module, self.interface_)
            return function_
        except AttributeError:
            msg = 'Missing interface {} {}.{}'.format(
                self.component.type,
                self.component.name,
                self.interface_)
            raise ScottyException(msg)

    def _exec_function(self, function_, context):
        try:
            self.component.state = CommonComponentState.ACTIVE
            self.component.starttime = datetime.now()
            result = function_(context)
            self.component.endtime = datetime.now()
            self.component.state = CommonComponentState.COMPLETED
            return result
        except Exception:
            self._log_component_exception()

    def _log_component_exception(self):
        self.component.state = CommonComponentState.ERROR
        msg = 'Error from customer {}.{}'.format(self.component.type, self.component.name)
        logger.exception(msg)


class ComponentExecutor(futures.ProcessPoolExecutor):
    _result_interface = None
    _interface = 'run'

    def __init__(self, experiment):
        super(ComponentExecutor, self).__init__(max_workers=4)
        self._future_to_component = {}
        self.experiment = experiment

    def submit_components(self):
        for component in self.list_components().values():
            self.submit(component)

    def submit(self, component):
        if self.skip_component(component) or self.skip_all():
            return
        future = super(ComponentExecutor, self).submit(
            exec_component,
            self.experiment,
            component,
            self._interface,
            self._result_interface)
        self._future_to_component[future] = component

    def list_components(self):
        return {}

    def skip_component(self, component):
        return False

    def skip_all(self):
        skip = self.experiment.has_errors()
        if skip:
            logger.info(f'Skip {self._interface} resource - something went wrong before')
        return skip

    def copy_task_attributes(self, source_component, target_component):
        target_component.starttime = source_component.starttime
        target_component.endtime = source_component.endtime
        target_component.state = source_component.state
        if self._result_interface:
            result = getattr(source_component, self._result_interface)
            setattr(target_component, self._result_interface, result)

    def check_error(self, component):
        if component.state == CommonComponentState.ERROR:
            self.experiment.state = CommonComponentState.ERROR

    def collect_results(self):
        for future in futures.as_completed(self._future_to_component):
            component = self._future_to_component[future]
            result = future.result()
            self.copy_task_attributes(result, component)
            self.check_error(component)

    @classmethod
    def perform(cls, experiment):
        executor_object = cls(experiment)
        executor_object.submit_components()
        executor_object.collect_results()


class ExperimentExecutor(object):
    def __init__(self, experiment):
        self.experiment = experiment

    @classmethod
    def perform(cls, experiment):
        executor_object = cls(experiment)
        executor_object.submit()


class ExperimentCleanExecutor(ExperimentExecutor):
    def submit(self):
        if self.experiment.has_errors():
            sys.exit(1)


class WorkloadExecutor(ComponentExecutor):
    def list_components(self):
        return self.experiment.components['workload']


class WorkloadRunExecutor(WorkloadExecutor):
    _result_interface = 'result'
    _interface = 'run'


class WorkloadCollectExecutor(WorkloadExecutor):
    _interface = 'collect'


class WorkloadCleanExecutor(WorkloadExecutor):
    _interface = 'clean'

    def skip_all(self):
        return False


class ResourceExecutor(ComponentExecutor):
    def list_components(self):
        return self.experiment.components['resource']


class ResourceExistsExecutor(ResourceExecutor):
    _result_interface = 'exists'
    _interface = 'exists'


class ResourceEndpointExecutor(ResourceExecutor):
    _result_interface = 'endpoint'
    _interface = 'endpoint'


class ResourceDeployExecutor(ResourceExecutor):
    _interface = 'deploy'

    def skip_component(self, component):
        skip = component.exists
        if skip:
            msg = f'Skip deploy for {component.name}, resource will be reused'
            logger.info(msg)
        return skip


class ResourceCleanExecutor(ResourceExecutor):
    _interface = 'clean'

    def skip_component(self, component):
        skip = component.keep
        if skip:
            msg = f'Skip clean for {component.name}, resource will be keeped'
            logger.info(msg)
        return skip

    def skip_all(self):
        return False


class SystemCollectorCollectExecutor(ComponentExecutor):
    _result_interface = 'result'
    _interface = 'collect'

    def list_components(self):
        return self.experiment.components['systemcollector']


class ResultStoreSubmitExecutor(ComponentExecutor):
    _interface = 'submit'

    def list_components(self):
        return self.experiment.components['systemcollector']
