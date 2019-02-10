import threading
from datetime import datetime
from typing import List

from retrying import retry

from sidecar.azure_clp.azure_cosmos_service import AzureCosmosService
from sidecar.azure_clp.retrying_helpers import retry_if_connection_error, retry_if_result_none_or_empty
from sidecar.const import Const


class AzureStatusMaintainer:
    ROOT_SPEC_KEY = "spec"
    EXPECTED_APPS_KEY = "expected_apps"
    ROOT_APPS_KEY = "apps"
    INSTANCES_KEY = "instances"

    def __init__(self, cosmos_service: AzureCosmosService, sandbox_id: str):
        self._cosmos_service = cosmos_service
        self._sandbox_id = sandbox_id
        self._lock = threading.RLock()

        self._cached_realtime_apps = None
        self._cached_spec = None
        self._cache_sandbox_data()

    def _cache_sandbox_data(self):
        sandbox_document = self._get_sandbox_document_with_retries()
        if not sandbox_document:
            raise Exception("Failed to get sandbox data from cosmos_db after 5 retries")

        self._cached_realtime_apps = sandbox_document[self.ROOT_APPS_KEY]
        self._cached_spec = sandbox_document[self.ROOT_SPEC_KEY]

    @retry(stop_max_attempt_number=5, wait_fixed=1000, retry_on_result=retry_if_result_none_or_empty,
           retry_on_exception=retry_if_connection_error)
    def _get_sandbox_document_with_retries(self):
        return self._cosmos_service.find_document_by_id(id=self._sandbox_id)

    def _construct_instances_key_path(self, instance_logical_id):
        return '{apps_key}.{instance_logical_id}.{instances_key}'.format(apps_key=self.ROOT_APPS_KEY,
                                                                         instance_logical_id=instance_logical_id,
                                                                         instances_key=self.INSTANCES_KEY)

    def update_app_instance_status(self, instance_logical_id, instance_id, app_name, status):
        with self._lock:

            instances_under_logical_id = self._cached_realtime_apps[instance_logical_id][self.INSTANCES_KEY]
            apps_under_instance_id = instances_under_logical_id.setdefault(instance_id, {"apps": {}})["apps"]
            apps_under_instance_id[app_name] = {Const.APP_STATUS_TAG: status}

            instances_key_path = self._construct_instances_key_path(instance_logical_id)
            self._cosmos_service.update_document(id=self._sandbox_id,
                                                 update_param={
                                                     '$set': {
                                                         instances_key_path: instances_under_logical_id
                                                     }})

    def get_app_names_on_instance(self, instance_logical_id: str) -> List[str]:
        return self._cached_spec[self.EXPECTED_APPS_KEY][instance_logical_id]["apps"]

    def update_sandbox_end_status(self, sandbox_deployment_end_status: str):
        # assume that DB-level lock is good enough here
        self._cosmos_service.update_document(id=self._sandbox_id,
                                             update_param={
                                                 '$set': {
                                                     Const.SANDBOX_DEPLOYMENT_END_STATUS: sandbox_deployment_end_status,
                                                     Const.SANDBOX_DEPLOYMENT_END_STATUS_v2: sandbox_deployment_end_status
                                                 }})

    def update_sandbox_start_status(self, sandbox_start_time: datetime):
        # assume that DB-level lock is good enough here
        self._cosmos_service.update_document(id=self._sandbox_id,
                                             update_param={
                                                 '$set': {
                                                     Const.SANDBOX_START_TIME: str(sandbox_start_time),
                                                     Const.SANDBOX_START_TIME_v2: str(sandbox_start_time)
                                                 }})
