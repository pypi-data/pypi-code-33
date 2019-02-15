import logging

from scotty.utils.base import BaseUtils


class WorkloadUtils(BaseUtils):
    def __init__(self, context):
        super(WorkloadUtils, self).__init__(context)
        try:
            self.current_workload = context.v1.workload
        except KeyError as e:
            raise ScottyException('WorkloadUtils can only used in workload context')
        self.basepath = self.experiment_workspace.get_component_data_path(
            self.current_workload,
            True
        )
        self._resources = None

    @property
    def resources(self):
        if not self._resources:
            self._resources = {}
            resource_list = self.current_workload.resources
            for resource_key, resource_name in resource_list.items():
                resource_component = self._get_resource_component(resource_name)
                self._resources[resource_key] = resource_component
        return self._resources

    def _get_resource_component(self, resource_name):
        resource_components = self._BaseUtils__experiment.components['resource']
        resource_component = resource_components.get(resource_name, None)
        if not resource_component:
            raise ScottyException(f'Could not found resource \'{resourcen_name}\'')
        return resource_component
