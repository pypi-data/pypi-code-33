from typing import List, Dict

from sidecar.apps_configuration_end_tracker import AppsConfigurationEndTracker, AppConfigurationEndStatus
from sidecar.const import AppNetworkStatus
from sidecar.health_check.app_health_check_state import AppHealthCheckState
from sidecar.model.objects import SidecarApplication


class AppConfigurationStartStatus:
    START = "start"
    WAIT = "wait"


class AppConfigurationStartPolicy:
    def __init__(self,
                 app_health_check_state: AppHealthCheckState,
                 apps_config_end_tracker: AppsConfigurationEndTracker,
                 apps: List[SidecarApplication]):
        self._apps = apps
        self._app_health_check_state = app_health_check_state
        self._apps_config_end_tracker = apps_config_end_tracker
        self._app_dependencies = self._build_app_dependencies(apps)

    def get_app_configuration_start_status(self, app_name: str) -> str:
        app_dependency_names = self._app_dependencies[app_name]
        if not app_dependency_names:
            return AppConfigurationStartStatus.START

        app_dependency_statuses = self._apps_config_end_tracker.get_app_configuration_statuses(*app_dependency_names)
        all_instances_completed_with_success = all(
            config_end_status.is_ended_with_status(AppConfigurationEndStatus.COMPLETED) for config_end_status in
            app_dependency_statuses.values())

        all_apps_completed_private_network_health_check = all(
            AppNetworkStatus.passed_internal_network_test(status)
            for status
            in self._app_health_check_state.get_apps_state(app_dependency_names).values())

        if all_instances_completed_with_success and all_apps_completed_private_network_health_check:
            return AppConfigurationStartStatus.START

        return AppConfigurationStartStatus.WAIT

    @staticmethod
    def _build_app_dependencies(apps: List[SidecarApplication]) -> Dict[str, List[str]]:
        _app_dependencies = {app.name: list(app.dependencies) for app in apps}
        return _app_dependencies
