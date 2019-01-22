# coding: utf-8

"""
    Assetic Integration API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: v2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from assetic.api_client import ApiClient


class MaintenanceConfigurationApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def maintenance_configuration_get(self, **kwargs):  # noqa: E501
        """Gets maintenance asset type and sub type based on request parameters  Pagination is currently not supported for this API  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsMaintenanceAssetTypeListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.maintenance_configuration_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.maintenance_configuration_get_with_http_info(**kwargs)  # noqa: E501
            return data

    def maintenance_configuration_get_with_http_info(self, **kwargs):  # noqa: E501
        """Gets maintenance asset type and sub type based on request parameters  Pagination is currently not supported for this API  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsMaintenanceAssetTypeListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_sorts', 'request_params_filters', 'request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method maintenance_configuration_get" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'request_params_sorts' in params:
            query_params.append(('requestParams.sorts', params['request_params_sorts']))  # noqa: E501
            collection_formats['requestParams.sorts'] = 'multi'  # noqa: E501
        if 'request_params_filters' in params:
            query_params.append(('requestParams.filters', params['request_params_filters']))  # noqa: E501
            collection_formats['requestParams.filters'] = 'multi'  # noqa: E501
        if 'request_params_page' in params:
            query_params.append(('requestParams.page', params['request_params_page']))  # noqa: E501
        if 'request_params_page_size' in params:
            query_params.append(('requestParams.pageSize', params['request_params_page_size']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'text/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/api/v2/maintenanceassettype', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsMaintenanceAssetTypeListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def maintenance_configuration_get_bill_of_material(self, **kwargs):  # noqa: E501
        """Gets bill of material based on request parameters  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_bill_of_material(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsBillOfMaterialListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.maintenance_configuration_get_bill_of_material_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.maintenance_configuration_get_bill_of_material_with_http_info(**kwargs)  # noqa: E501
            return data

    def maintenance_configuration_get_bill_of_material_with_http_info(self, **kwargs):  # noqa: E501
        """Gets bill of material based on request parameters  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_bill_of_material_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsBillOfMaterialListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_sorts', 'request_params_filters', 'request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method maintenance_configuration_get_bill_of_material" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'request_params_sorts' in params:
            query_params.append(('requestParams.sorts', params['request_params_sorts']))  # noqa: E501
            collection_formats['requestParams.sorts'] = 'multi'  # noqa: E501
        if 'request_params_filters' in params:
            query_params.append(('requestParams.filters', params['request_params_filters']))  # noqa: E501
            collection_formats['requestParams.filters'] = 'multi'  # noqa: E501
        if 'request_params_page' in params:
            query_params.append(('requestParams.page', params['request_params_page']))  # noqa: E501
        if 'request_params_page_size' in params:
            query_params.append(('requestParams.pageSize', params['request_params_page_size']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'text/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/api/v2/billofmaterial', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsBillOfMaterialListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def maintenance_configuration_get_interruption_factor(self, **kwargs):  # noqa: E501
        """Get asset down time factors  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_interruption_factor(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsInterruptionFactorListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.maintenance_configuration_get_interruption_factor_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.maintenance_configuration_get_interruption_factor_with_http_info(**kwargs)  # noqa: E501
            return data

    def maintenance_configuration_get_interruption_factor_with_http_info(self, **kwargs):  # noqa: E501
        """Get asset down time factors  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_interruption_factor_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsInterruptionFactorListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_sorts', 'request_params_filters', 'request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method maintenance_configuration_get_interruption_factor" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'request_params_sorts' in params:
            query_params.append(('requestParams.sorts', params['request_params_sorts']))  # noqa: E501
            collection_formats['requestParams.sorts'] = 'multi'  # noqa: E501
        if 'request_params_filters' in params:
            query_params.append(('requestParams.filters', params['request_params_filters']))  # noqa: E501
            collection_formats['requestParams.filters'] = 'multi'  # noqa: E501
        if 'request_params_page' in params:
            query_params.append(('requestParams.page', params['request_params_page']))  # noqa: E501
        if 'request_params_page_size' in params:
            query_params.append(('requestParams.pageSize', params['request_params_page_size']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'text/json', 'application/hal+json', 'application/hal+xml'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/api/v2/interruptionfactor', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsInterruptionFactorListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def maintenance_configuration_get_managed_resources(self, **kwargs):  # noqa: E501
        """Gets managed resources based on request parameters  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_managed_resources(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsResourceDetailsGroupCraftUnitListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.maintenance_configuration_get_managed_resources_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.maintenance_configuration_get_managed_resources_with_http_info(**kwargs)  # noqa: E501
            return data

    def maintenance_configuration_get_managed_resources_with_http_info(self, **kwargs):  # noqa: E501
        """Gets managed resources based on request parameters  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_managed_resources_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsResourceDetailsGroupCraftUnitListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_sorts', 'request_params_filters', 'request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method maintenance_configuration_get_managed_resources" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'request_params_sorts' in params:
            query_params.append(('requestParams.sorts', params['request_params_sorts']))  # noqa: E501
            collection_formats['requestParams.sorts'] = 'multi'  # noqa: E501
        if 'request_params_filters' in params:
            query_params.append(('requestParams.filters', params['request_params_filters']))  # noqa: E501
            collection_formats['requestParams.filters'] = 'multi'  # noqa: E501
        if 'request_params_page' in params:
            query_params.append(('requestParams.page', params['request_params_page']))  # noqa: E501
        if 'request_params_page_size' in params:
            query_params.append(('requestParams.pageSize', params['request_params_page_size']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'text/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/api/v2/managedresource', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsResourceDetailsGroupCraftUnitListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def maintenance_configuration_get_resource_craft(self, id, **kwargs):  # noqa: E501
        """Gets resource craft and group craft based on request parameters  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_resource_craft(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsResourceGroupCraftListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.maintenance_configuration_get_resource_craft_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.maintenance_configuration_get_resource_craft_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def maintenance_configuration_get_resource_craft_with_http_info(self, id, **kwargs):  # noqa: E501
        """Gets resource craft and group craft based on request parameters  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_resource_craft_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsResourceGroupCraftListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'request_params_sorts', 'request_params_filters', 'request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method maintenance_configuration_get_resource_craft" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params or
                params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `maintenance_configuration_get_resource_craft`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []
        if 'request_params_sorts' in params:
            query_params.append(('requestParams.sorts', params['request_params_sorts']))  # noqa: E501
            collection_formats['requestParams.sorts'] = 'multi'  # noqa: E501
        if 'request_params_filters' in params:
            query_params.append(('requestParams.filters', params['request_params_filters']))  # noqa: E501
            collection_formats['requestParams.filters'] = 'multi'  # noqa: E501
        if 'request_params_page' in params:
            query_params.append(('requestParams.page', params['request_params_page']))  # noqa: E501
        if 'request_params_page_size' in params:
            query_params.append(('requestParams.pageSize', params['request_params_page_size']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'text/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/api/v2/resource/{id}/craft', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsResourceGroupCraftListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def maintenance_configuration_get_service_activity(self, **kwargs):  # noqa: E501
        """Gets service activity based on request parameters  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_service_activity(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsServiceActivityListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.maintenance_configuration_get_service_activity_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.maintenance_configuration_get_service_activity_with_http_info(**kwargs)  # noqa: E501
            return data

    def maintenance_configuration_get_service_activity_with_http_info(self, **kwargs):  # noqa: E501
        """Gets service activity based on request parameters  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_service_activity_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsServiceActivityListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_sorts', 'request_params_filters', 'request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method maintenance_configuration_get_service_activity" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'request_params_sorts' in params:
            query_params.append(('requestParams.sorts', params['request_params_sorts']))  # noqa: E501
            collection_formats['requestParams.sorts'] = 'multi'  # noqa: E501
        if 'request_params_filters' in params:
            query_params.append(('requestParams.filters', params['request_params_filters']))  # noqa: E501
            collection_formats['requestParams.filters'] = 'multi'  # noqa: E501
        if 'request_params_page' in params:
            query_params.append(('requestParams.page', params['request_params_page']))  # noqa: E501
        if 'request_params_page_size' in params:
            query_params.append(('requestParams.pageSize', params['request_params_page_size']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'text/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/api/v2/serviceactivity', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsServiceActivityListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def maintenance_configuration_get_work_type(self, **kwargs):  # noqa: E501
        """Gets work types including budget types  Pagination is currently not supported for this API  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_work_type(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsWorkTypeListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.maintenance_configuration_get_work_type_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.maintenance_configuration_get_work_type_with_http_info(**kwargs)  # noqa: E501
            return data

    def maintenance_configuration_get_work_type_with_http_info(self, **kwargs):  # noqa: E501
        """Gets work types including budget types  Pagination is currently not supported for this API  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.maintenance_configuration_get_work_type_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsWorkTypeListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_sorts', 'request_params_filters', 'request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method maintenance_configuration_get_work_type" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'request_params_sorts' in params:
            query_params.append(('requestParams.sorts', params['request_params_sorts']))  # noqa: E501
            collection_formats['requestParams.sorts'] = 'multi'  # noqa: E501
        if 'request_params_filters' in params:
            query_params.append(('requestParams.filters', params['request_params_filters']))  # noqa: E501
            collection_formats['requestParams.filters'] = 'multi'  # noqa: E501
        if 'request_params_page' in params:
            query_params.append(('requestParams.page', params['request_params_page']))  # noqa: E501
        if 'request_params_page_size' in params:
            query_params.append(('requestParams.pageSize', params['request_params_page_size']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json', 'text/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/api/v2/worktype', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsWorkTypeListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
