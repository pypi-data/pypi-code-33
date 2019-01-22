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


class FCRCategorisationApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def f_cr_categorisation_get(self, **kwargs):  # noqa: E501
        """Returns FCR categorisation list.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsFCRCategorisationListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.f_cr_categorisation_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.f_cr_categorisation_get_with_http_info(**kwargs)  # noqa: E501
            return data

    def f_cr_categorisation_get_with_http_info(self, **kwargs):  # noqa: E501
        """Returns FCR categorisation list.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] request_params_sorts:
        :param list[str] request_params_filters:
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsFCRCategorisationListRepresentation
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
                    " to method f_cr_categorisation_get" % key
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
            '/api/v2/fcrcategorisation', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsFCRCategorisationListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def f_cr_categorisation_get_0(self, id, **kwargs):  # noqa: E501
        """Get FCR categorisation by given Id  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_0(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int id: FCR categorisation Id (required)
        :return: Assetic3IntegrationRepresentationsFCRCategorisationListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.f_cr_categorisation_get_0_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.f_cr_categorisation_get_0_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def f_cr_categorisation_get_0_with_http_info(self, id, **kwargs):  # noqa: E501
        """Get FCR categorisation by given Id  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_0_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int id: FCR categorisation Id (required)
        :return: Assetic3IntegrationRepresentationsFCRCategorisationListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method f_cr_categorisation_get_0" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params or
                params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `f_cr_categorisation_get_0`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []

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
            '/api/v2/fcrcategorisation/{id}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsFCRCategorisationListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def f_cr_categorisation_get_cause_codes_by_categorisation_id(self, id, **kwargs):  # noqa: E501
        """f_cr_categorisation_get_cause_codes_by_categorisation_id  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_cause_codes_by_categorisation_id(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int id: (required)
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.f_cr_categorisation_get_cause_codes_by_categorisation_id_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.f_cr_categorisation_get_cause_codes_by_categorisation_id_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def f_cr_categorisation_get_cause_codes_by_categorisation_id_with_http_info(self, id, **kwargs):  # noqa: E501
        """f_cr_categorisation_get_cause_codes_by_categorisation_id  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_cause_codes_by_categorisation_id_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int id: (required)
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method f_cr_categorisation_get_cause_codes_by_categorisation_id" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params or
                params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `f_cr_categorisation_get_cause_codes_by_categorisation_id`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []

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
            '/api/v2/fcrcategorisation/{id}/causecodes', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def f_cr_categorisation_get_failure_codes_by_categorisation_id(self, id, **kwargs):  # noqa: E501
        """f_cr_categorisation_get_failure_codes_by_categorisation_id  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_failure_codes_by_categorisation_id(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int id: (required)
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.f_cr_categorisation_get_failure_codes_by_categorisation_id_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.f_cr_categorisation_get_failure_codes_by_categorisation_id_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def f_cr_categorisation_get_failure_codes_by_categorisation_id_with_http_info(self, id, **kwargs):  # noqa: E501
        """f_cr_categorisation_get_failure_codes_by_categorisation_id  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_failure_codes_by_categorisation_id_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int id: (required)
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method f_cr_categorisation_get_failure_codes_by_categorisation_id" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params or
                params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `f_cr_categorisation_get_failure_codes_by_categorisation_id`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []

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
            '/api/v2/fcrcategorisation/{id}/failurecodes', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def f_cr_categorisation_get_remedy_codes_by_categorisation_id(self, id, **kwargs):  # noqa: E501
        """f_cr_categorisation_get_remedy_codes_by_categorisation_id  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_remedy_codes_by_categorisation_id(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int id: (required)
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.f_cr_categorisation_get_remedy_codes_by_categorisation_id_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.f_cr_categorisation_get_remedy_codes_by_categorisation_id_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def f_cr_categorisation_get_remedy_codes_by_categorisation_id_with_http_info(self, id, **kwargs):  # noqa: E501
        """f_cr_categorisation_get_remedy_codes_by_categorisation_id  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.f_cr_categorisation_get_remedy_codes_by_categorisation_id_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int id: (required)
        :return: object
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method f_cr_categorisation_get_remedy_codes_by_categorisation_id" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params or
                params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `f_cr_categorisation_get_remedy_codes_by_categorisation_id`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []

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
            '/api/v2/fcrcategorisation/{id}/remedycodes', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
