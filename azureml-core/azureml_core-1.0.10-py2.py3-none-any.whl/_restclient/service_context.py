# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""**ServiceContext** container for scope and authentication of a workspace."""
import logging
import os

from azureml._base_sdk_common.service_discovery import get_service_url
from azureml._base_sdk_common.app_settings import AppSettings
from azureml._logging.chained_identity import ChainedIdentity

DEVLEOPER_URL_TEMPLATE = "AZUREML_DEV_URL_{}"

module_logger = logging.getLogger(__name__)


class _ServiceKeys(object):
    """Enum of keys for retrieving service urls from discovery service."""
    MMS_DISCOVERY_KEY = "modelmanagement"
    EXPERIMENTATION_DISCOVERY_KEY = "experimentation"
    HISTORY_DISCOVERY_KEY = "history"
    PIPELINES_DISCOVERY_KEY = "pipelines"
    HYPERDRIVE_DISCOVERY_KEY = "hyperdrive"

    # For datastore:
    # DATASTORE = "datastore"

    ARTIFACTS = "artifacts"
    ASSETS = "assets"
    EXPERIMENTATION = "experimentation"
    HYPERDRIVE = "hyperdrive"
    PIPELINES = "pipelines"
    RUN_HISTORY = "run_history"

    _names = []
    _discovery_keys = []
    _override_env_vars = []
    _name_to_key = {}
    _initialized = False

    @classmethod
    def initialize(cls):
        cls.register_discovery_url(cls.ARTIFACTS, cls.HISTORY_DISCOVERY_KEY)
        cls.register_discovery_url(cls.RUN_HISTORY, cls.HISTORY_DISCOVERY_KEY)
        cls.register_discovery_url(cls.ASSETS, cls.MMS_DISCOVERY_KEY)
        cls.register_discovery_url(cls.EXPERIMENTATION, cls.EXPERIMENTATION_DISCOVERY_KEY)
        cls.register_discovery_url(cls.HYPERDRIVE, cls.HYPERDRIVE_DISCOVERY_KEY)
        cls.register_discovery_url(cls.PIPELINES, cls.PIPELINES_DISCOVERY_KEY)

        # For datastore:
        # cls.register_discover_url(cls.DATASTORE, cls.DATASTORE_DISCOVERY_KEY)
        cls._initialized = True

    @classmethod
    def register_discovery_url(cls, name, discovery_key=None):
        cls._names.append(name)
        discovery_key = discovery_key if discovery_key is not None else name
        cls._discovery_keys.append(discovery_key)

        cls._name_to_key[name] = discovery_key

        env_var = cls.generate_environment_variable(name)
        cls._override_env_vars.append(env_var)

    @classmethod
    def generate_environment_variable(cls, key):
        env_var = DEVLEOPER_URL_TEMPLATE.format(key.upper())
        return env_var

    @classmethod
    def get_discovery_key(cls, name):
        return cls._name_to_key[name]

    @classmethod
    def get_names(cls):
        return cls._names

    @classmethod
    def get_discovery_keys(cls):
        return cls._discovery_keys

    @classmethod
    def get_override_env_vars(cls):
        return cls._override_env_vars


_ServiceKeys.initialize()


class _EndpointChannel(object):
    """Enum of supported service channels."""

    MASTER = "master"
    DEFAULT = "default"


class ServiceContext(ChainedIdentity):
    """
    A container for workspace scope, authentication, and service location information.

    :param subscription_id: The subscription id.
    :type subscription_id: str
    :param resource_group_name: The name of the resource group.
    :type resource_group_name: str
    :param workspace_name: The name of the workspace.
    :type workspace_name: str
    :param authentication: The auth object.
    :type authentication: azureml.core.authentication.AbstractAuthentication
    :param endpoint_channel: The channel for service discovery.
    :type endpoint_channel: str
    :param kwargs:
    """

    def __init__(self,
                 subscription_id, resource_group_name, workspace_name, workspace_id,
                 authentication, endpoint_channel=None,
                 **kwargs):
        """
        Store scope information and fetch service locations.

        :param subscription_id: The subscription id.
        :type subscription_id: str
        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param workspace_name: The name of the workspace.
        :type workspace_name: str
        :param authentication: The auth object.
        :type authentication: azureml.core.authentication.AbstractAuthentication
        :param endpoint_channel: The channel for service discovery.
        :type endpoint_channel: str
        :param kwargs:
        """
        super(ServiceContext, self).__init__(**kwargs)

        self._sub_id = subscription_id
        self._rg_name = resource_group_name
        self._ws_name = workspace_name
        self._workspace_id = workspace_id

        endpoint_channel = endpoint_channel if endpoint_channel is not None else AppSettings().get_flight()
        assert endpoint_channel in [_EndpointChannel.MASTER, _EndpointChannel.DEFAULT]
        self._channel = endpoint_channel

        from azureml.core.authentication import AbstractAuthentication
        assert isinstance(authentication, AbstractAuthentication)
        self._authentication = authentication

        self._endpoints = self._fetch_endpoints()

    @property
    def subscription_id(self):
        """
        Return the subscription id for this workspace.

        :return: The subscription id.
        :rtype: str
        """
        return self._sub_id

    @property
    def resource_group_name(self):
        """
        Return the resource group name for this workspace.

        :return: The resource group name.
        :rtype: str
        """
        return self._rg_name

    @property
    def workspace_name(self):
        """
        Return the workspace name.

        :return: The workspace name.
        :rtype: str
        """
        return self._ws_name

    @property
    def endpoint_channel(self):
        """
        Return the workspace name.

        :return: The service channel.
        :rtype: str
        """
        return self._channel

    def get_auth(self):
        """
        Return the authentication object.

        :return: The authentication object.
        :rtype: azureml.core.authentication.AbstractAuthentication
        """
        return self._authentication

    def _get_workspace_scope(self):
        """
        Return the scope information for the workspace.

        :param workspace_object: The workspace object.
        :type workspace_object: azureml.core.workspace.Workspace
        :return: The scope information for the workspace.
        :rtype: str
        """
        return ("/subscriptions/{}/resourceGroups/{}/providers"
                "/Microsoft.MachineLearningServices"
                "/workspaces/{}").format(self.subscription_id,
                                         self.resource_group_name,
                                         self.workspace_name)

    def _get_developer_override(self, key):
        environment_variable = _ServiceKeys.generate_environment_variable(key)
        developer_endpoint = os.environ.get(environment_variable)
        if developer_endpoint is not None:
            self._logger.debug("Loaded endpoint {} from environment variable {}.".format(
                developer_endpoint, environment_variable))
        return developer_endpoint

    def _fetch_endpoints(self):
        """
        Fetch service endpoints from service discovery.

        :return: Dictionary of service discovery key to service url.
        :rtype: dict[str] -> str
        """
        scope = self._get_workspace_scope()
        endpoints = {}
        for discovery_key in _ServiceKeys.get_discovery_keys():
            url = get_service_url(self._authentication, scope, self._workspace_id,
                                  service_name=discovery_key)
            endpoints[discovery_key] = url
        return endpoints

    def _get_endpoint(self, key):
        """
        Get service endpoint from environment variable if set, otherwise from service discovery.

        :return: The service endpoint.
        :rtype: str
        """
        developer_endpoint = self._get_developer_override(key)
        if developer_endpoint is not None:
            endpoint = developer_endpoint
        else:
            discovery_key = _ServiceKeys.get_discovery_key(key)
            endpoint = self._endpoints[discovery_key]
        return endpoint

    def _get_run_history_url(self):
        """
        Return the url to the run history service.

        :return: The run history service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.RUN_HISTORY)

    def _get_experimentation_url(self):
        """
        Return the url to the experimentation service.

        :return: The experimentation service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.EXPERIMENTATION)

    def _get_artifacts_url(self):
        """
        Return the url to the artifacts service.

        :return: The artifacts service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.ARTIFACTS)

    def _get_pipelines_url(self):
        """
        Return the url to the pipelines service.

        :return: The pipelines service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.PIPELINES)

    def _get_hyperdrive_url(self):
        """
        Return the url to the hyperdrive service.

        :return: The hyperdrive service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.HYPERDRIVE)

    def _get_assets_url(self):
        """
        Return the url to the model management service.

        :return: The model management service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.ASSETS)
