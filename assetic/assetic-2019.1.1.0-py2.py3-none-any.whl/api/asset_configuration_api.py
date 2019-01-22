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


class AssetConfigurationApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def asset_configuration_get_asset_category(self, **kwargs):  # noqa: E501
        """Get a collection of asset category  # noqa: E501

        <br />  <br />              Sample request: <br /><pre>               /api/v2/assetcategory                  </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_category(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: Assetic3IntegrationRepresentationsAssetCategoryConfigurationRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.asset_configuration_get_asset_category_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.asset_configuration_get_asset_category_with_http_info(**kwargs)  # noqa: E501
            return data

    def asset_configuration_get_asset_category_with_http_info(self, **kwargs):  # noqa: E501
        """Get a collection of asset category  # noqa: E501

        <br />  <br />              Sample request: <br /><pre>               /api/v2/assetcategory                  </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_category_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: Assetic3IntegrationRepresentationsAssetCategoryConfigurationRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method asset_configuration_get_asset_category" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

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
            '/api/v2/assetcategory', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsAssetCategoryConfigurationRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def asset_configuration_get_asset_classes(self, **kwargs):  # noqa: E501
        """Get a collection of asset class and asset sub-class  # noqa: E501

        Only pagination is supported for now. Default page size is 20.  <br /><br />  Sample request: <br /><pre>   /api/v2/assetclass  /api/v2/assetclass?requestParams.Page=1  /api/v2/assetclass?requestParams.Page=1&amp;requestParams.PageSize=5      </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_classes(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsAssetClassListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.asset_configuration_get_asset_classes_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.asset_configuration_get_asset_classes_with_http_info(**kwargs)  # noqa: E501
            return data

    def asset_configuration_get_asset_classes_with_http_info(self, **kwargs):  # noqa: E501
        """Get a collection of asset class and asset sub-class  # noqa: E501

        Only pagination is supported for now. Default page size is 20.  <br /><br />  Sample request: <br /><pre>   /api/v2/assetclass  /api/v2/assetclass?requestParams.Page=1  /api/v2/assetclass?requestParams.Page=1&amp;requestParams.PageSize=5      </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_classes_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsAssetClassListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method asset_configuration_get_asset_classes" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
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
            '/api/v2/assetclass', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsAssetClassListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def asset_configuration_get_asset_criticality(self, **kwargs):  # noqa: E501
        """Get a collection of asset criticality  # noqa: E501

        <br />  <br />              Sample request: <br /><pre>               /api/v2/assetcategory/criticality                  </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_criticality(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsAssetCategoryConfigurationRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.asset_configuration_get_asset_criticality_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.asset_configuration_get_asset_criticality_with_http_info(**kwargs)  # noqa: E501
            return data

    def asset_configuration_get_asset_criticality_with_http_info(self, **kwargs):  # noqa: E501
        """Get a collection of asset criticality  # noqa: E501

        <br />  <br />              Sample request: <br /><pre>               /api/v2/assetcategory/criticality                  </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_criticality_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsAssetCategoryConfigurationRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method asset_configuration_get_asset_criticality" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
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
            '/api/v2/assetcategory/criticality', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsAssetCategoryConfigurationRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def asset_configuration_get_asset_criticality_by_id(self, id, **kwargs):  # noqa: E501
        """Get a collection of asset criticality  # noqa: E501

        <br />  <br />              Sample request: <br /><pre>               /api/v2/assetcategory/{id}/criticality                  </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_criticality_by_id(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :return: Assetic3IntegrationRepresentationsAssetCategoryCriticalityConfigurationRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.asset_configuration_get_asset_criticality_by_id_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.asset_configuration_get_asset_criticality_by_id_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def asset_configuration_get_asset_criticality_by_id_with_http_info(self, id, **kwargs):  # noqa: E501
        """Get a collection of asset criticality  # noqa: E501

        <br />  <br />              Sample request: <br /><pre>               /api/v2/assetcategory/{id}/criticality                  </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_criticality_by_id_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :return: Assetic3IntegrationRepresentationsAssetCategoryCriticalityConfigurationRepresentation
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
                    " to method asset_configuration_get_asset_criticality_by_id" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params or
                params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `asset_configuration_get_asset_criticality_by_id`")  # noqa: E501

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
            '/api/v2/assetcategory/{id}/criticality', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsAssetCategoryCriticalityConfigurationRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def asset_configuration_get_asset_types(self, **kwargs):  # noqa: E501
        """Get a collection of asset type and asset sub-type  # noqa: E501

        Only pagination is supported for now. Default page size is 20.  <br /><br />  Sample request: <br /><pre>   /api/v2/assettype  /api/v2/assettype?requestParams.Page=1  /api/v2/assettype?requestParams.Page=1&amp;requestParams.PageSize=5      </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_types(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsAssetTypeListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.asset_configuration_get_asset_types_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.asset_configuration_get_asset_types_with_http_info(**kwargs)  # noqa: E501
            return data

    def asset_configuration_get_asset_types_with_http_info(self, **kwargs):  # noqa: E501
        """Get a collection of asset type and asset sub-type  # noqa: E501

        Only pagination is supported for now. Default page size is 20.  <br /><br />  Sample request: <br /><pre>   /api/v2/assettype  /api/v2/assettype?requestParams.Page=1  /api/v2/assettype?requestParams.Page=1&amp;requestParams.PageSize=5      </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_asset_types_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsAssetTypeListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method asset_configuration_get_asset_types" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
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
            '/api/v2/assettype', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsAssetTypeListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def asset_configuration_get_fiancial_class_and_sub_class(self, **kwargs):  # noqa: E501
        """Get a collection of financial class and financial sub-class  # noqa: E501

        Only pagination is supported for now. Default page size is 20.  <br /><br />  Sample request: <br /><pre>   /api/v2/assetfinancialclass  /api/v2/assetfinancialclass?requestParams.Page=1  /api/v2/assetfinancialclass?requestParams.Page=1&amp;requestParams.PageSize=5      </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_fiancial_class_and_sub_class(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsFinancialClassListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.asset_configuration_get_fiancial_class_and_sub_class_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.asset_configuration_get_fiancial_class_and_sub_class_with_http_info(**kwargs)  # noqa: E501
            return data

    def asset_configuration_get_fiancial_class_and_sub_class_with_http_info(self, **kwargs):  # noqa: E501
        """Get a collection of financial class and financial sub-class  # noqa: E501

        Only pagination is supported for now. Default page size is 20.  <br /><br />  Sample request: <br /><pre>   /api/v2/assetfinancialclass  /api/v2/assetfinancialclass?requestParams.Page=1  /api/v2/assetfinancialclass?requestParams.Page=1&amp;requestParams.PageSize=5      </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_fiancial_class_and_sub_class_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsFinancialClassListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method asset_configuration_get_fiancial_class_and_sub_class" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
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
            '/api/v2/assetfinancialclass', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsFinancialClassListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def asset_configuration_get_work_group(self, **kwargs):  # noqa: E501
        """Get a collection of work group  # noqa: E501

        Only pagination is supported for now. Default page size is 20.  <br /><br />  Sample request: <br /><pre>   /api/v2/workgroup  /api/v2/workgroup?requestParams.Page=1  /api/v2/workgroup?requestParams.Page=1&amp;requestParams.PageSize=5      </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_work_group(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsWorkGroupConfigurationListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.asset_configuration_get_work_group_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.asset_configuration_get_work_group_with_http_info(**kwargs)  # noqa: E501
            return data

    def asset_configuration_get_work_group_with_http_info(self, **kwargs):  # noqa: E501
        """Get a collection of work group  # noqa: E501

        Only pagination is supported for now. Default page size is 20.  <br /><br />  Sample request: <br /><pre>   /api/v2/workgroup  /api/v2/workgroup?requestParams.Page=1  /api/v2/workgroup?requestParams.Page=1&amp;requestParams.PageSize=5      </pre>  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.asset_configuration_get_work_group_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int request_params_page:
        :param int request_params_page_size:
        :return: Assetic3IntegrationRepresentationsWorkGroupConfigurationListRepresentation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['request_params_page', 'request_params_page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method asset_configuration_get_work_group" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
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
            '/api/v2/workgroup', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Assetic3IntegrationRepresentationsWorkGroupConfigurationListRepresentation',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
