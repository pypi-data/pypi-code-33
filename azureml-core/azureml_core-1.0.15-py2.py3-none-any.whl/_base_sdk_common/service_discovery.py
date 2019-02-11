# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import sys
import os
import threading
import logging
import requests

from azureml.exceptions import DiscoveryUrlNotFoundException

from six.moves.urllib import parse
from os.path import expanduser, join, dirname

from azureml._base_sdk_common.app_settings import AppSettings
from .workspace.version import VERSION

GALLERY_GLOBAL_ENDPOINT = 'https://gallery.cortanaintelligence.com/project'
CATALOG_GLOBAL_ENDPOINT = 'https://catalog.cortanaanalytics.com'
TRANSIENT_CLUSTER_ENDPOINT = 'AZUREML_EXPERIMENTATION_HOST'
HISTORY_SERVICE_ENDPOINT_KEY = "AZUREML_SERVICE_ENDPOINT"
MMS_TEST_ENDPOINT_KEY = 'AZUREML_MMS_TEST_ENDPOINT'
MMS_TEST_ENDPOINT = "https://mms.azureml-test.net"

# Service name enums
HISTORY_SERVICE_ENUM = "history"
MODEL_MANAGEMENT_ENUM = "modelmanagement"
PIPELINES_SERVICE_ENUM = "pipelines"

if sys.version_info[0] < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

module_logger = logging.getLogger(__name__)


def load_history_service_url_from_env():
    #  Check environment variables for history_service_url overrides
    url_overrides = [TRANSIENT_CLUSTER_ENDPOINT, HISTORY_SERVICE_ENDPOINT_KEY]
    for key in url_overrides:
        history_service_url = os.environ.get(key)
        if history_service_url:
            module_logger.debug("Found history service url in environment variable {}, "
                                "history service url: {}.".format(key, history_service_url))
            return history_service_url

    raise DiscoveryUrlNotFoundException(HISTORY_SERVICE_ENUM)


def load_mms_service_url_from_env():
    #  Check environment variables for history_service_url to construct mms url
    mms_host = os.environ.get(MMS_TEST_ENDPOINT_KEY)
    if mms_host is not None:
        module_logger.debug("Found mms service url in environment variable {}, "
                            "history service url: {}.".format(MMS_TEST_ENDPOINT_KEY, mms_host))
        return mms_host
    elif os.environ.get(TRANSIENT_CLUSTER_ENDPOINT) is not None:
        return MMS_TEST_ENDPOINT
    else:
        history_service_url = load_history_service_url_from_env()
        module_logger.debug("Constructing mms service url in from history url environment variable {}, "
                            "history service url: {}.".format(mms_host, history_service_url))
        parsed_history_service_url = parse.urlparse(history_service_url)
        region = parsed_history_service_url.netloc.split(".")[0]
        if region == "master" or "mms." in parsed_history_service_url.netloc:
            mms_host = MMS_TEST_ENDPOINT
        else:
            mms_host = "https://{}.modelmanagement.azureml.net".format(region)
        return mms_host


def get_service_url(auth, workspace_scope, workspace_id, service_name=HISTORY_SERVICE_ENUM):
    """
    A common method to get service end point url for all services.
    :param auth: The auth object.
    :type auth:azureml.core.authentication.AbstractAuthentication
    :param workspace_scope: The full arm workspace scope.
    :type workspace_scope: str
    :param workspace_id: The workspace id.
    :type workspace_id: str
    :param service_name: The service name like history, pipelines etc.
    :type service_name: str
    :return: The service end point url.
    :rtype: str
    """
    try:
        if service_name == HISTORY_SERVICE_ENUM:
            return load_history_service_url_from_env()
        elif service_name == MODEL_MANAGEMENT_ENUM:
            return load_mms_service_url_from_env()
    except DiscoveryUrlNotFoundException as exception:
        module_logger.debug(exception)

    cached_service_object = CachedServiceDiscovery(auth)
    flight = AppSettings().get_flight()
    return cached_service_object.get_cached_service_url(workspace_scope, service_name, flight,
                                                        unique_id=workspace_id)


class ServiceDiscovery(object):
    def __init__(self, auth):
        """
        :param auth: auth object.
        :type auth: azureml.core.authentication.AbstractAuthentication
        """
        self._auth_object = auth

    def get_service_url(self, arm_scope, service_name, flight):
        return self.get_flight(arm_scope, flight)[service_name]

    def get_flight(self, arm_scope, flight):
        discovery_url = self.get_discovery_url(arm_scope)
        parsed_url = parse.urlparse(discovery_url)

        region = parsed_url.netloc.split(".", 2)[0]
        params = {}
        if flight is not None and flight != "default" and region != "master":
            params = {'flight': flight}

        status = requests.get(discovery_url, params=params)
        status.raise_for_status()
        return status.json()

    def discover_services_uris(self, discovery_url):
        status = requests.get(discovery_url)
        status.raise_for_status()
        return status.json()

    def get_discovery_url(self, arm_scope):
        try:
            return load_history_service_url_from_env() + "/discovery"
        except DiscoveryUrlNotFoundException as exception:
            module_logger.debug(
                "Failed to load url from env with exception {}, "
                "calling arm for discovery urls.".format(exception))
            resource = self._get_team_resource(arm_scope)
            discovery_uri = resource['properties']['discoveryUrl']
            if discovery_uri is None:
                raise ValueError("cannot acquire discovery uri for resource {}".format(arm_scope))
            return discovery_uri

    def _get_team_resource(self, arm_scope):
        arm_endpoint = self._auth_object._get_arm_end_point()
        headers = self._auth_object.get_authentication_header()
        query_parameters = {'api-version': VERSION}
        status = requests.get(urljoin(arm_endpoint, arm_scope), headers=headers, params=query_parameters)

        status.raise_for_status()
        return status.json()


def _function_lock_decorator(lock_to_use):
    """
    A decorator to apply on a function to execute the function
    by acquiring lock_to_use in exclusive manner.
    :param lock_to_use:
    :return:
    """
    def actual_decorator(test_function):
        def wrapper(self, *args, **kwargs):
            try:
                lock_to_use.acquire()
                return test_function(self, *args, **kwargs)
            finally:
                lock_to_use.release()
        return wrapper

    return actual_decorator


class CachedServiceDiscovery(ServiceDiscovery):
    _cache_file_writing_lock = threading.Lock()

    def __init__(self, auth, file_path=join(expanduser("~"), ".azureml", ".discovery")):
        super(CachedServiceDiscovery, self).__init__(auth)
        dir_name = dirname(file_path)
        try:
            os.mkdir(os.path.abspath(dir_name))
        except OSError:
            # Ignoring error if the path already exists.
            pass
        self.file_path = file_path

    @_function_lock_decorator(_cache_file_writing_lock)
    def get_cached_flight(self, arm_scope, service_name, flight, unique_id=None):
        """
        Gets the cached flight.
        :param arm_scope: The arm scope of a resource
        :type arm_scope: str
        :param service_name:
        :type service_name: str
        :param flight: Either default or master.
        :type flight: str
        :param unique_id: A unique id of the resource, like workspace Id for a workspace.
        :type unique_id: str
        :return: The flight dict
        :rtype: dict
        """
        # Concatenating arm_scope and unique_id, useful to detect reincarnations of a workspace.
        cache_key = arm_scope
        if unique_id:
            cache_key = cache_key + "/" + unique_id

        cache = {}
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r") as file:
                    cache = json.load(file)

            if cache is not None and cache_key in cache:
                account_cache = cache.get(cache_key)
                if flight in account_cache:
                    flight_cache = account_cache.get(flight)
                    if service_name in flight_cache:
                        service_url = flight_cache[service_name]
                        if service_url is not None:
                            return flight_cache

        except Exception:
            # This is a bad cache
            cache = {}

        if cache is None:
            cache = {}
        if cache.get(cache_key) is None:
            cache[cache_key] = {}

        # Actual service discovery only understands arm_scope
        cache[cache_key][flight] = super(CachedServiceDiscovery, self).get_flight(arm_scope, flight)
        try:
            with open(self.file_path, "w+") as file:
                json.dump(cache, file)
        except FileNotFoundError as exception:
            module_logger.warning("Could not write to .discovery cache, failed with: {}.".format(exception))
        except Exception as exception:
            module_logger.warning(
                "Could not write to .discovery cache, failed with unexpected exception: {}.".format(exception))
        return cache[cache_key][flight]

    def get_cached_service_url(self, arm_scope, service_name, flight, unique_id=None):
        """
        Returns the cached service url or fetches it, caches it and then returns it.
        :param arm_scope:
        :type arm_scope: str
        :param service_name:
        :type service_name: str
        :param flight: Either default or master
        :type flight: str
        :param unique_id: A unique id of the resource, like workspace Id for a workspace.
        :type unique_id: str
        :return: The service url
        :rtype: str
        """
        return self.get_cached_flight(arm_scope, service_name, flight, unique_id=unique_id)[service_name]
