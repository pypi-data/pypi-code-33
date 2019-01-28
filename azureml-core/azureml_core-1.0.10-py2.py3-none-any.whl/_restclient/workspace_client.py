# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""Access workspace client"""
from .clientbase import ClientBase, PAGINATED_KEY

from .service_context import ServiceContext


class WorkspaceClient(ClientBase):
    """
    Run History APIs

    :param host: The base path for the server to call.
    :type host: str
    :param auth: Client authentication
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id:
    :type subscription_id: str
    :param resource_group_name:
    :type resource_group_name: str
    :param workspace_name:
    :type workspace_name: str
    """
    OLD_ROUTE = "old"
    NEW_ROUTE = "new"

    def __init__(self, service_context, host=None, **kwargs):
        """
        Constructor of the class.
        """
        self._service_context = service_context
        host = host if host is not None else self._get_cluster_url()
        self._workspace_arguments = [self._service_context.subscription_id,
                                     self._service_context.resource_group_name,
                                     self._service_context.workspace_name]
        super(WorkspaceClient, self).__init__(host, self._service_context.get_auth(),
                                              **kwargs)
        self._custom_headers = {}
        self.api_route = WorkspaceClient.NEW_ROUTE

    @classmethod
    def create(cls, workspace, auth=None, endpoint_channel=None,
               **kwargs):
        auth = auth if auth is not None else workspace._auth_object
        """create a new workspace client"""
        # In remote context, we can't fetch workspace id. It is also not needed.
        try:
            workspace_id = workspace._workspace_id
        except Exception:
            workspace_id = None

        service_context = ServiceContext(workspace.subscription_id,
                                         workspace.resource_group,
                                         workspace.name,
                                         workspace_id,
                                         auth,
                                         endpoint_channel=endpoint_channel,
                                         _ident="WorkspaceCreateServiceContext")

        return cls(service_context, **kwargs)

    @property
    def auth(self):
        return self._service_context.get_auth()

    def get_cluster_url(self):
        """get service url"""
        return self._host

    def _get_cluster_url(self):
        """get service url"""
        return self._service_context._get_run_history_url()

    def get_workspace_uri_path(self):
        return self._service_context._get_workspace_scope()

    def _execute_with_workspace_arguments(self, func, *args, **kwargs):
        if not callable(func):
            raise TypeError('Argument is not callable')

        if self._custom_headers:
            kwargs["custom_headers"] = self._custom_headers

        args_list = []
        args_list.extend(self._workspace_arguments)
        if args:
            args_list.extend(args)
        is_paginated = kwargs.pop(PAGINATED_KEY, False)
        if is_paginated:
            return self._call_paginated_api(func, *args_list, **kwargs)
        else:
            return self._call_api(func, *args_list, **kwargs)

    def _combine_with_workspace_paginated_dto(self, func, count_to_download=0, *args, **kwargs):
        return self._combine_paginated_base(self._execute_with_workspace_arguments,
                                            func,
                                            count_to_download,
                                            *args,
                                            **kwargs)

    def list_experiments(self):
        """
        list all experiments
        :return: a generator of ~_restclient.models.ExperimentDto
        """
        if self.api_route == WorkspaceClient.OLD_ROUTE:
            self._logger.debug("Experiment calls do not support old routes, calling experiment route")
        return self._execute_with_workspace_arguments(self._client.experiment.list,
                                                      is_paginated=True)

    def get_experiment(self, experiment_name, is_async=False):
        """
        list all experiments in a workspace
        :return: a generator of ~_restclient.models.ExperimentDto
        :param is_async bool: execute request asynchronously
        :return:
            If is_async parameter is True,
            the request is called asynchronously.
            The method returns azureml._async_task.AsyncTask object
            If parameter is_async is False or missing,
            return: ~_restclient.models.ExperimentDto
        """
        if self.api_route == WorkspaceClient.OLD_ROUTE:
            self._logger.debug("Experiment calls do not support old routes, calling experiment route")
        return self._execute_with_workspace_arguments(self._client.experiment.get,
                                                      experiment_name=experiment_name,
                                                      is_async=is_async)
