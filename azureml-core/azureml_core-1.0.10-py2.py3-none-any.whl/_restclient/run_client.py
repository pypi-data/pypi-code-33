# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Access a experiment client"""
import copy

from azureml.exceptions import AzureMLException
from .clientbase import PAGINATED_KEY
from .contracts.events import (create_start_event, create_completed_event,
                               create_failed_event, create_canceled_event,
                               create_heartbeat_event)
from .constants import ORDER_BY_STARTTIME_EXPRESSION, DEFAULT_PAGE_SIZE, FILTER_KEY
from .experiment_client import ExperimentClient
from .models.create_run_dto import CreateRunDto
from .service_context import ServiceContext
from .utils import _generate_client_kwargs, _validate_order_by
from ._hierarchy.runs import Tree
from ._odata.expressions import and_join


class RunClient(ExperimentClient):
    """
    Experiment APIs

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
    :param experiment_name:
    :type experiment_name: str
    :param run_id:
    :type run_id: str
    """

    def __init__(self,
                 service_context,
                 experiment_name,
                 run_id,
                 **kwargs):
        """
        Constructor of the class.
        """
        super(RunClient, self).__init__(service_context,
                                        experiment_name,
                                        **kwargs)
        self._run_id = run_id
        self._run_arguments = copy.deepcopy(self._experiment_arguments)
        self._run_arguments.append(self._run_id)

    @classmethod
    def create(cls, workspace, experiment_name, run_id, auth=None, endpoint_channel=None,
               **kwargs):
        """Create a run client"""
        auth = auth if auth is not None else workspace._auth_object
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
                                         endpoint_channel=endpoint_channel)

        return cls(service_context, experiment_name, run_id, **kwargs)

    def get_run(self, **kwargs):
        """
        Get detail of a run by its run_id
        This fuction could also be called from the super class,
        ExperimentClient, for a specific run_id
        """
        return super(RunClient, self).get_run(self._run_id, **kwargs)

    def get_runstatus(self, caller=None, custom_headers=None, is_async=False):
        """
        Get status details of a run by its run_id
        :param is_async: execute request asynchronously
        :type is_async: bool
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_headers: dict
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: ~_restclient.models.RunDetailsDto (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        kwargs = _generate_client_kwargs(
            is_async=is_async, caller=caller, custom_headers=custom_headers)

        if self.api_route == RunClient.OLD_ROUTE:
            func = self._client.legacy_run.get_status
        else:
            func = self._client.run.get_details
        return self._execute_with_run_arguments(func, **kwargs)

    def create_child_run(self, child_run_id, script_name=None,
                         target=None, run_name=None, caller=None, custom_headers=None, is_async=False):
        """
        Create a child run
        :param child_run_id: child_run_id(required)
        :type child_run_id: str
        :param script_name: script name
        :type script_name: str
        :param target: run target
        :type target: str
        :param run_name: run_name
        :type run_name: str
        :param is_async: execute request asynchronously
        :type is_async: bool (optional)
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_headers: dict
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: ~_restclient.models.RunDto (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        kwargs = _generate_client_kwargs(
            is_async=is_async, caller=caller, custom_headers=custom_headers)

        create_run_dto = CreateRunDto(run_id=child_run_id,
                                      parent_run_id=self._run_id,
                                      script_name=script_name,
                                      target=target,
                                      name=run_name,
                                      status='NotStarted')

        if self.api_route == RunClient.OLD_ROUTE:
            return self._execute_with_run_arguments(self._client.legacy_run.create_child,
                                                    new_child_run=create_run_dto,
                                                    **kwargs)
        else:
            return self._execute_with_experiment_arguments(self._client.run.patch,
                                                           run_id=child_run_id,
                                                           create_run_dto=create_run_dto,
                                                           **kwargs)

    def get_child_runs(self, root_run_id, recursive=False, _filter_on_server=False,
                       page_size=DEFAULT_PAGE_SIZE, order_by=None,
                       caller=None, custom_headers=None, **kwargs):
        """
        Get child runs by current run_id
        :param root_run_id: optimization id for hierarchy(required)
        :type root_run_id: str
        :param recursive: fetch grandchildren and further descendants(required)
        :type recursive: bool
        :param page_size: number of dto returned by one request (optional)
        :type page_size: int
        :param order_by: keys to sort return values, ('sort_key', 'asc'/'desc')(optional)
        :type order_by: tuple (str, str)
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_headers: dict
        :return: list of dictionary whose keys are property of ~_restclient.models.RunDto
        """
        order_by_expression = _validate_order_by(order_by) if order_by else [ORDER_BY_STARTTIME_EXPRESSION]
        client_kwargs = _generate_client_kwargs(top=page_size, orderby=order_by_expression, caller=caller,
                                                custom_headers=custom_headers, is_paginated=True)
        client_kwargs.update(kwargs)
        filter_expression = self._get_run_filter_expr(**kwargs) if _filter_on_server else None
        if recursive and _filter_on_server:
            raise AzureMLException("Recursive get_child_runs is not yet supported with service side filtering")
        elif recursive:
            root_filter = 'RootRunId eq {0}'.format(root_run_id)
            full_filter = and_join([root_filter, filter_expression]) if _filter_on_server else root_filter

            client_kwargs[FILTER_KEY] = full_filter
            run_dtos = self._execute_with_experiment_arguments(self._client.run.list, **client_kwargs)

            # Filter out nodes outside of the desired sub tree
            run_hierarchy = Tree(run_dtos)
            sub_tree_run_dtos = run_hierarchy.get_subtree_dtos(self._run_id)

            return self._client_filter(sub_tree_run_dtos, **kwargs)
        else:
            route = (self._client.legacy_run.get_child if self.api_route ==
                     RunClient.OLD_ROUTE else self._client.run.get_child)
            run_dtos = self._execute_with_run_arguments(route, **client_kwargs)
            return run_dtos if _filter_on_server else self._client_filter(run_dtos, **kwargs)

    def patch_run(self, create_run_dto, caller=None, custom_headers=None, is_async=False):
        """
        Patch a run to the run history client
        :param create_run_dto: a new run object(required)
        :type ~_restclient.models.CreateRunDto
        :param is_async: execute request asynchronously
        :type is_async: bool (optional)
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_headers: dict
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: ~_restclient.models.RunDto (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        kwargs = _generate_client_kwargs(
            is_async=is_async, caller=caller, custom_headers=custom_headers)
        if self.api_route == RunClient.OLD_ROUTE:
            return self._execute_with_run_arguments(self._client.legacy_run.patch,
                                                    modify_run_dto=create_run_dto,
                                                    **kwargs)

        return self._execute_with_run_arguments(self._client.run.patch,
                                                create_run_dto=create_run_dto,
                                                **kwargs)

    def post_event(self, event, caller=None, custom_headers=None, is_async=False):
        """
        Post an event of a run by its run_id
        This method makes a synchronous call by default. To make an
        asynchronous call, please pass is_async=True
        :param event: event to update (required)
        :type event: models.BaseEvent
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_headers: dict
        :param is_async: execute request asynchronously
        :type is_async: bool
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: None (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        kwargs = _generate_client_kwargs(event_message=event, caller=caller,
                                         custom_headers=custom_headers, is_async=is_async)

        if self.api_route == RunClient.OLD_ROUTE:
            return self._execute_with_run_arguments(self._client.legacy_events.post, **kwargs)

        return self._execute_with_run_arguments(self._client.events.post, **kwargs)

    def post_event_start(self, caller=None, custom_headers=None, is_async=False):
        """
        Post run-started-event for this run_id
        This method makes a synchronous call by default. To make an
        asynchronous call, please pass is_async=True
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_header: dict
        :param is_async: execute request asynchronously
        :type is_async: bool
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: None (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        event = create_start_event(self._run_id)
        return self.post_event(event, is_async=is_async, caller=caller, custom_headers=custom_headers)

    def post_event_completed(self, caller=None, custom_headers=None, is_async=False):
        """
        Post run-completed-event for this run_id
        This method makes a synchronous call by default. To make an
        asynchronous call, please pass is_async=True
        :param is_async: execute request asynchronously
        :type is_async: bool
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_header: dict
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: None (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        event = create_completed_event(self._run_id)
        return self.post_event(event, is_async=is_async, caller=caller, custom_headers=custom_headers)

    def post_event_failed(self, caller=None, custom_headers=None, is_async=False):
        """
        Post run-failed-event for this run_id
        This method makes a synchronous call by default. To make an
        asynchronous call, please pass is_async=True
        :param is_async: execute request asynchronously
        :type is_async: bool
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_header: dict
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: None (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        event = create_failed_event(self._run_id)
        return self.post_event(event, is_async=is_async, caller=caller, custom_headers=custom_headers)

    def post_event_canceled(self, caller=None, custom_headers=None, is_async=False):
        """
        Post run-canceled-event by its run_id
        This method makes a synchronous call by default. To make an
        asynchronous call, please pass is_async=True
        :param is_async: execute request asynchronously
        :type is_async: bool
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_header: dict
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: None (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        event = create_canceled_event(self._run_id)
        return self.post_event(event, is_async=is_async, caller=caller, custom_headers=custom_headers)

    def post_event_heartbeat(self, time, caller=None, custom_headers=None, is_async=False):
        """
        Post run-heartbeat-event by its run_id
        This method makes a synchronous call by default. To make an
        asynchronous call, please pass is_async=True
        :param run_id: run id (required)
        :type run_id: str
        :param time: timeout in seconds (required)
        :type time: int
        :param is_async: execute request asynchronously
        :type is_async: bool
        :param caller: caller function name (optional)
        :type caller: str
        :param custom_headers: headers that will be added to the request (optional)
        :type custom_header: dict
        :return:
            the return type is based on is_async parameter.
            If is_async parameter is True,
            the request is called asynchronously.
        rtype: None (is_async is False) or
            azureml._async.AsyncTask (is_async is True)
        """
        event = create_heartbeat_event(self._run_id, time)
        return self.post_event(event, is_async=is_async, caller=caller, custom_headers=custom_headers)

    def _execute_with_run_arguments(self, func, *args, **kwargs):
        if not callable(func):
            raise TypeError('Argument is not callable')

        if self._custom_headers:
            kwargs["custom_headers"] = self._custom_headers
        args_list = []
        args_list.extend(self._run_arguments)
        if args:
            args_list.extend(args)
        is_paginated = kwargs.pop(PAGINATED_KEY, False)
        if is_paginated:
            return self._call_paginated_api(func, *args_list, **kwargs)
        else:
            return self._call_api(func, *args_list, **kwargs)

    def _combine_with_run_paginated_dto(self, func, count_to_download=0, *args, **kwargs):
        return self._combine_paginated_base(self._execute_with_run_arguments,
                                            func,
                                            count_to_download,
                                            *args,
                                            **kwargs)
