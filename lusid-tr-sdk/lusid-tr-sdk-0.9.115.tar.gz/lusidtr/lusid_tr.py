# coding=utf-8
# --------------------------------------------------------------------------
# # License
#
# Copyright &copy; 2018 FINBOURNE TECHNOLOGY LTD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------------

from msrest.service_client import ServiceClient
from msrest import Configuration, Serializer, Deserializer
from .version import VERSION
from msrest.pipeline import ClientRawResponse
from msrest.exceptions import HttpOperationError
from . import models


class LusidTrConfiguration(Configuration):
    """Configuration for LusidTr
    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credentials: Subscription credentials which uniquely identify
     client subscription.
    :type credentials: None
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if not base_url:
            base_url = 'http://localhost'

        super(LusidTrConfiguration, self).__init__(base_url)

        self.add_user_agent('lusidtr/{}'.format(VERSION))

        self.credentials = credentials


class LusidTr(object):
    """LusidTr

    :ivar config: Configuration for client.
    :vartype config: LusidTrConfiguration

    :param credentials: Subscription credentials which uniquely identify
     client subscription.
    :type credentials: None
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, base_url=None):

        self.config = LusidTrConfiguration(credentials, base_url)
        self._client = ServiceClient(self.config.credentials, self.config)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self.api_version = '0.9.115'
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)


    def get_aggregation_by_group(
            self, scope, code, request=None, sort_by=None, start=None, limit=None, custom_headers=None, raw=False, **operation_config):
        """Aggregate data in a group hierarchy.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param request:
        :type request: ~lusidtr.models.AggregationRequest
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ListAggregationResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ListAggregationResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_aggregation_by_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'AggregationRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ListAggregationResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_aggregation_by_group.metadata = {'url': '/data/lusid/aggregation/portfoliogroups/{scope}/{code}/$aggregate'}

    def get_nested_aggregation_by_group(
            self, scope, code, request=None, custom_headers=None, raw=False, **operation_config):
        """Obsolete - Aggregation request data in a group hierarchy into a data
        tree.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param request:
        :type request: ~lusidtr.models.AggregationRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: NestedAggregationResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.NestedAggregationResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_nested_aggregation_by_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'AggregationRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('NestedAggregationResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_nested_aggregation_by_group.metadata = {'url': '/data/lusid/aggregation/portfoliogroups/{scope}/{code}/$aggregatenested'}

    def get_aggregation_by_portfolio(
            self, scope, code, request=None, sort_by=None, start=None, limit=None, custom_headers=None, raw=False, **operation_config):
        """Aggregate data in a portfolio.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param request:
        :type request: ~lusidtr.models.AggregationRequest
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ListAggregationResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ListAggregationResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_aggregation_by_portfolio.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'AggregationRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ListAggregationResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_aggregation_by_portfolio.metadata = {'url': '/data/lusid/aggregation/portfolios/{scope}/{code}/$aggregate'}

    def get_aggregation_by_result_set(
            self, scope, results_key, request=None, sort_by=None, start=None, limit=None, custom_headers=None, raw=False, **operation_config):
        """Aggregate data from a result set.

        :param scope:
        :type scope: str
        :param results_key:
        :type results_key: str
        :param request:
        :type request: ~lusidtr.models.AggregationRequest
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ListAggregationResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ListAggregationResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_aggregation_by_result_set.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'resultsKey': self._serialize.url("results_key", results_key, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'AggregationRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ListAggregationResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_aggregation_by_result_set.metadata = {'url': '/data/lusid/aggregation/results/{scope}/{resultsKey}/$aggregate'}

    def list_analytic_stores(
            self, as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """List all analytic stores in client.

        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param filter:
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfAnalyticStoreKey or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfAnalyticStoreKey or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_analytic_stores.metadata['url']

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfAnalyticStoreKey', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_analytic_stores.metadata = {'url': '/data/lusid/analytics'}

    def create_analytic_store(
            self, request=None, custom_headers=None, raw=False, **operation_config):
        """Create a new analytic store for the given scope for the given date.

        :param request: A valid and fully populated analytic store creation
         request
        :type request: ~lusidtr.models.CreateAnalyticStoreRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: AnalyticStore or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.AnalyticStore or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.create_analytic_store.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'CreateAnalyticStoreRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('AnalyticStore', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_analytic_store.metadata = {'url': '/data/lusid/analytics'}

    def get_analytic_store(
            self, scope, year, month, day, as_at=None, custom_headers=None, raw=False, **operation_config):
        """Get an analytic store.

        :param scope: The analytics data scope
        :type scope: str
        :param year: The year component of the date for the data in the scope
        :type year: int
        :param month: The month component of the date for the data in the
         scope
        :type month: int
        :param day: The day component of the date for the data in the scope
        :type day: int
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: AnalyticStore or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.AnalyticStore or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_analytic_store.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'year': self._serialize.url("year", year, 'int'),
            'month': self._serialize.url("month", month, 'int'),
            'day': self._serialize.url("day", day, 'int')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('AnalyticStore', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_analytic_store.metadata = {'url': '/data/lusid/analytics/{scope}/{year}/{month}/{day}'}

    def delete_analytic_store(
            self, scope, year, month, day, custom_headers=None, raw=False, **operation_config):
        """Create a new analytic store for the given scope for the given date.

        :param scope: The analytics data scope
        :type scope: str
        :param year: The year component of the date for the data in the scope
        :type year: int
        :param month: The month component of the date for the data in the
         scope
        :type month: int
        :param day: The day component of the date for the data in the scope
        :type day: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_analytic_store.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'year': self._serialize.url("year", year, 'int'),
            'month': self._serialize.url("month", month, 'int'),
            'day': self._serialize.url("day", day, 'int')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_analytic_store.metadata = {'url': '/data/lusid/analytics/{scope}/{year}/{month}/{day}'}

    def set_analytics(
            self, scope, year, month, day, data=None, custom_headers=None, raw=False, **operation_config):
        """Set analytic data.

        Store the complete set of analytics for an existing analytic store for
        the specified scope and date.

        :param scope: The scope of the data being stored
        :type scope: str
        :param year: The year component of the date for the data
        :type year: int
        :param month: The month component of the date for the data
        :type month: int
        :param day: The day component of the date for the data
        :type day: int
        :param data: The analytic data being inserted
        :type data: list[~lusidtr.models.InstrumentAnalytic]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: AnalyticStore or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.AnalyticStore or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.set_analytics.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'year': self._serialize.url("year", year, 'int'),
            'month': self._serialize.url("month", month, 'int'),
            'day': self._serialize.url("day", day, 'int')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if data is not None:
            body_content = self._serialize.body(data, '[InstrumentAnalytic]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('AnalyticStore', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    set_analytics.metadata = {'url': '/data/lusid/analytics/{scope}/{year}/{month}/{day}/prices'}

    def list_corporate_action_sources(
            self, effective_at=None, as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Get corporate action sources.

        Gets a list of all corporate action sources.

        :param effective_at: Optional. The start effective date of the data
         range
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by: Optional. Order the results by these fields. Use use
         the '-' sign to denote descending order e.g. -MyFieldName
        :type sort_by: list[str]
        :param start: Optional. When paginating, skip this number of results
        :type start: int
        :param limit: Optional. When paginating, limit the number of returned
         results to this many
        :type limit: int
        :param filter: Optional. Expression to filter the result set
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfCorporateActionSource or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfCorporateActionSource or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_corporate_action_sources.metadata['url']

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfCorporateActionSource', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_corporate_action_sources.metadata = {'url': '/data/lusid/corporateactionsources'}

    def create_corporate_action_source(
            self, request=None, custom_headers=None, raw=False, **operation_config):
        """Create Corporate Action Source.

        Attempt to create a corporate action source.

        :param request: The corporate action source definition
        :type request: ~lusidtr.models.CreateCorporateActionSourceRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: CorporateActionSource or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.CorporateActionSource or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.create_corporate_action_source.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'CreateCorporateActionSourceRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('CorporateActionSource', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_corporate_action_source.metadata = {'url': '/data/lusid/corporateactionsources'}

    def delete_corporate_action_source(
            self, scope, code, effective_at=None, custom_headers=None, raw=False, **operation_config):
        """Delete a corporate action source.

        Deletes a single corporate action source.

        :param scope: The Scope of the Corporate Action Source to be deleted
        :type scope: str
        :param code: The Code of the Corporate Action Source to be deleted
        :type code: str
        :param effective_at: Optional. The start effective date of the data
        :type effective_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_corporate_action_source.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_corporate_action_source.metadata = {'url': '/data/lusid/corporateactionsources/{scope}/{code}'}

    def get_corporate_actions(
            self, scope, code, from_effective_at=None, to_effective_at=None, as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Gets a corporate action based on dates.

        :param scope: Scope
        :type scope: str
        :param code: Corporate action source id
        :type code: str
        :param from_effective_at: Optional. The start effective date of the
         data range
        :type from_effective_at: datetime
        :param to_effective_at: Optional. The end effective date of the data
         range
        :type to_effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param filter:
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfCorporateAction or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfCorporateAction or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_corporate_actions.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if from_effective_at is not None:
            query_parameters['fromEffectiveAt'] = self._serialize.query("from_effective_at", from_effective_at, 'iso-8601')
        if to_effective_at is not None:
            query_parameters['toEffectiveAt'] = self._serialize.query("to_effective_at", to_effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfCorporateAction', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_corporate_actions.metadata = {'url': '/data/lusid/corporateactionsources/{scope}/{code}/corporateactions'}

    def batch_upsert_corporate_actions(
            self, scope, code, actions=None, custom_headers=None, raw=False, **operation_config):
        """Attempt to create/update one or more corporate action. Failed actions
        will be identified in the body of the response.

        :param scope: The intended scope of the corporate action
        :type scope: str
        :param code: Source of the corporate action
        :type code: str
        :param actions: The corporate actions to create
        :type actions: list[~lusidtr.models.CreateCorporateAction]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpsertCorporateActionsResponse or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.UpsertCorporateActionsResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.batch_upsert_corporate_actions.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if actions is not None:
            body_content = self._serialize.body(actions, '[CreateCorporateAction]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('UpsertCorporateActionsResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    batch_upsert_corporate_actions.metadata = {'url': '/data/lusid/corporateactionsources/{scope}/{code}/corporateactions'}

    def create_data_type(
            self, request=None, custom_headers=None, raw=False, **operation_config):
        """Create a new PropertyDataFormat. Note: Only non-default formats can be
        created.

        :param request: The definition of the new format
        :type request: ~lusidtr.models.CreateDataTypeRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DataType or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DataType or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.create_data_type.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'CreateDataTypeRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('DataType', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_data_type.metadata = {'url': '/data/lusid/datatypes'}

    def list_data_types(
            self, scope, include_default=None, include_system=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Lists all property data formats in the specified scope.

        :param scope:
        :type scope: str
        :param include_default:
        :type include_default: bool
        :param include_system:
        :type include_system: bool
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param filter:
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfDataType or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfDataType or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_data_types.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if include_default is not None:
            query_parameters['includeDefault'] = self._serialize.query("include_default", include_default, 'bool')
        if include_system is not None:
            query_parameters['includeSystem'] = self._serialize.query("include_system", include_system, 'bool')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfDataType', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_data_types.metadata = {'url': '/data/lusid/datatypes/{scope}'}

    def get_data_type(
            self, scope, code, custom_headers=None, raw=False, **operation_config):
        """Gets a property data format.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DataType or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DataType or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_data_type.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DataType', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_data_type.metadata = {'url': '/data/lusid/datatypes/{scope}/{code}'}

    def update_data_type(
            self, scope, code, request=None, custom_headers=None, raw=False, **operation_config):
        """Update a PropertyDataFormat. Note: Only non-default formats can be
        updated.

        :param scope: The scope of the format being updated
        :type scope: str
        :param code: The name of the format to update
        :type code: str
        :param request: The new definition of the format
        :type request: ~lusidtr.models.UpdateDataTypeRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DataType or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DataType or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.update_data_type.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'UpdateDataTypeRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DataType', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    update_data_type.metadata = {'url': '/data/lusid/datatypes/{scope}/{code}'}

    def get_units_from_data_type(
            self, scope, code, units=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Return the definitions for the specified list of units.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param units:
        :type units: list[str]
        :param filter:
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfIUnitDefinitionDto or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfIUnitDefinitionDto or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_units_from_data_type.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if units is not None:
            query_parameters['units'] = self._serialize.query("units", units, '[str]', div=',')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfIUnitDefinitionDto', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_units_from_data_type.metadata = {'url': '/data/lusid/datatypes/{scope}/{code}/units'}

    def list_instruments(
            self, as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Get all of the currently mastered instruments in LUSID.

        Lists all instruments that have been mastered within LUSID.

        :param as_at: The AsAt time
        :type as_at: datetime
        :param sort_by: Optional. Order the results by these fields. Use use
         the '-' sign to denote descending order e.g. -MyFieldName
        :type sort_by: list[str]
        :param start: Optional. When paginating, skip this number of results
        :type start: int
        :param limit: Optional. When paginating, limit the number of returned
         results to this many.
        :type limit: int
        :param filter: Optional. Expression to filter the result set
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfInstrument or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfInstrument or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_instruments.metadata['url']

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfInstrument', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_instruments.metadata = {'url': '/data/lusid/instruments'}

    def upsert_instruments(
            self, requests=None, custom_headers=None, raw=False, **operation_config):
        """Upsert instruments.

        Attempt to master one or more instruments in LUSID's instrument master.
        Each instrument is keyed by some unique key. This key is unimportant,
        and serves only as a method to identify created instruments in the
        response.
        The response will return both the collection of successfully created
        instruments, as well as those that were rejected and why their creation
        failed. They will be keyed against the key supplied in the
        request.
        It is important to always check the 'Failed' set for any unsuccessful
        results.

        :param requests: The instrument definitions
        :type requests: dict[str, ~lusidtr.models.InstrumentDefinition]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpsertInstrumentsResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.UpsertInstrumentsResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_instruments.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if requests is not None:
            body_content = self._serialize.body(requests, '{InstrumentDefinition}')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('UpsertInstrumentsResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_instruments.metadata = {'url': '/data/lusid/instruments'}

    def get_instrument(
            self, identifier_type, identifier, effective_at=None, as_at=None, instrument_property_keys=None, custom_headers=None, raw=False, **operation_config):
        """Get instrument definition.

        Get an individual instrument by the one of its unique instrument
        identifiers. Optionally, it is possible to decorate each instrument
        with specified property data.

        :param identifier_type: The type of identifier being supplied
        :type identifier_type: str
        :param identifier: The identifier of the requested instrument
        :type identifier: str
        :param effective_at: Optional. The effective date of the query
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the query
        :type as_at: datetime
        :param instrument_property_keys: Optional. Keys of the properties to
         be decorated on to the instrument
        :type instrument_property_keys: list[str]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Instrument or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Instrument or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_instrument.metadata['url']
        path_format_arguments = {
            'identifierType': self._serialize.url("identifier_type", identifier_type, 'str'),
            'identifier': self._serialize.url("identifier", identifier, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if instrument_property_keys is not None:
            query_parameters['instrumentPropertyKeys'] = self._serialize.query("instrument_property_keys", instrument_property_keys, '[str]', div=',')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('Instrument', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_instrument.metadata = {'url': '/data/lusid/instruments/{identifierType}/{identifier}'}

    def update_instrument_identifier(
            self, identifier_type, identifier, request=None, custom_headers=None, raw=False, **operation_config):
        """Update instrument identifier.

        Adds, updates, or removes an identifier on an instrument.

        :param identifier_type: The type of identifier being supplied
        :type identifier_type: str
        :param identifier: The instrument identifier
        :type identifier: str
        :param request: The identifier to add, update, or remove
        :type request: ~lusidtr.models.UpdateInstrumentIdentifierRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Instrument or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Instrument or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.update_instrument_identifier.metadata['url']
        path_format_arguments = {
            'identifierType': self._serialize.url("identifier_type", identifier_type, 'str'),
            'identifier': self._serialize.url("identifier", identifier, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'UpdateInstrumentIdentifierRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('Instrument', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    update_instrument_identifier.metadata = {'url': '/data/lusid/instruments/{identifierType}/{identifier}'}

    def delete_instrument(
            self, identifier_type, identifier, custom_headers=None, raw=False, **operation_config):
        """Delete instrument.

        Attempt to delete one or more "client" instruments.
        The response will include those instruments that could not be deleted
        (as well as any available details).
        It is important to always check the 'Failed' set for any unsuccessful
        results.

        :param identifier_type: The type of identifier being supplied
        :type identifier_type: str
        :param identifier: The instrument identifier
        :type identifier: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeleteInstrumentResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeleteInstrumentResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_instrument.metadata['url']
        path_format_arguments = {
            'identifierType': self._serialize.url("identifier_type", identifier_type, 'str'),
            'identifier': self._serialize.url("identifier", identifier, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeleteInstrumentResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_instrument.metadata = {'url': '/data/lusid/instruments/{identifierType}/{identifier}'}

    def find_instruments(
            self, aliases=None, effective_at=None, as_at=None, instrument_property_keys=None, custom_headers=None, raw=False, **operation_config):
        """Search instrument definition.

        Get a collection of instruments by a set of identifiers. Optionally, it
        is possible to decorate each instrument with specified property data.

        :param aliases: The list of market aliases (e.g ISIN, Ticker) to find
         instruments by.
        :type aliases: list[~lusidtr.models.Property]
        :param effective_at: Optional. The effective date of the query
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the query
        :type as_at: datetime
        :param instrument_property_keys: Optional. Keys of the properties to
         be decorated on to the instrument
        :type instrument_property_keys: list[str]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfInstrument or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfInstrument or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.find_instruments.metadata['url']

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if instrument_property_keys is not None:
            query_parameters['instrumentPropertyKeys'] = self._serialize.query("instrument_property_keys", instrument_property_keys, '[str]', div=',')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if aliases is not None:
            body_content = self._serialize.body(aliases, '[Property]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfInstrument', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    find_instruments.metadata = {'url': '/data/lusid/instruments/$find'}

    def get_instruments(
            self, identifier_type=None, identifiers=None, effective_at=None, as_at=None, instrument_property_keys=None, custom_headers=None, raw=False, **operation_config):
        """Get instrument definition.

        Get a collection of instruments by a set of identifiers. Optionally, it
        is possible to decorate each instrument with specified property data.

        :param identifier_type: the type of identifiers being specified
        :type identifier_type: str
        :param identifiers: The identifiers of the instruments to get
        :type identifiers: list[str]
        :param effective_at: Optional. The effective date of the request
        :type effective_at: datetime
        :param as_at: Optional. The as at date of the request
        :type as_at: datetime
        :param instrument_property_keys: Optional. Keys of the properties to
         be decorated on to the instrument
        :type instrument_property_keys: list[str]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: GetInstrumentsResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.GetInstrumentsResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_instruments.metadata['url']

        # Construct parameters
        query_parameters = {}
        if identifier_type is not None:
            query_parameters['identifierType'] = self._serialize.query("identifier_type", identifier_type, 'str')
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if instrument_property_keys is not None:
            query_parameters['instrumentPropertyKeys'] = self._serialize.query("instrument_property_keys", instrument_property_keys, '[str]', div=',')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if identifiers is not None:
            body_content = self._serialize.body(identifiers, '[str]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('GetInstrumentsResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_instruments.metadata = {'url': '/data/lusid/instruments/$get'}

    def match_instruments(
            self, identifier_type=None, identifiers=None, custom_headers=None, raw=False, **operation_config):
        """Find externally mastered instruments.

        Search for a set of instruments from an external instrument mastering
        service.

        :param identifier_type: The type of identifiers to search for
        :type identifier_type: str
        :param identifiers: The identifiers of instruments to search for
        :type identifiers: list[str]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: MatchInstrumentsResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.MatchInstrumentsResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.match_instruments.metadata['url']

        # Construct parameters
        query_parameters = {}
        if identifier_type is not None:
            query_parameters['identifierType'] = self._serialize.query("identifier_type", identifier_type, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if identifiers is not None:
            body_content = self._serialize.body(identifiers, '[str]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('MatchInstrumentsResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    match_instruments.metadata = {'url': '/data/lusid/instruments/$match'}

    def upsert_instruments_properties(
            self, instrument_properties=None, custom_headers=None, raw=False, **operation_config):
        """Upsert instrument properties.

        Attempt to upsert property data for one or more instruments,
        properties, and effective dates.
        The response will include the details of any failures that occurred
        during data storage.
        It is important to always check the 'Failed' collection for any
        unsuccessful results.

        :param instrument_properties: The instrument property data
        :type instrument_properties:
         list[~lusidtr.models.UpsertInstrumentPropertyRequest]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpsertInstrumentPropertiesResponse or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.UpsertInstrumentPropertiesResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_instruments_properties.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if instrument_properties is not None:
            body_content = self._serialize.body(instrument_properties, '[UpsertInstrumentPropertyRequest]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('UpsertInstrumentPropertiesResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_instruments_properties.metadata = {'url': '/data/lusid/instruments/$upsertproperties'}

    def get_instrument_identifiers(
            self, custom_headers=None, raw=False, **operation_config):
        """Get allowable instrument identifiers.

        Gets the set of identifiers that have been configured as unique
        identifiers for instruments.
        Only values returned from this end point can be used as identifiers for
        instruments.

        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfString or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfString or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_instrument_identifiers.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfString', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_instrument_identifiers.metadata = {'url': '/data/lusid/instruments/identifiers'}

    def get_lusid_versions(
            self, custom_headers=None, raw=False, **operation_config):
        """Returns the current major application version.

        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: VersionSummaryDto or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.VersionSummaryDto or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_lusid_versions.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('VersionSummaryDto', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_lusid_versions.metadata = {'url': '/data/lusid/metadata/versions'}

    def get_multiple_property_definitions(
            self, property_keys=None, as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Get multiple property definitions.

        Gets one or more property definitions from a supplied set of keys.

        :param property_keys:
        :type property_keys: list[str]
        :param as_at:
        :type as_at: datetime
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param filter:
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfPropertyDefinition or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfPropertyDefinition or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_multiple_property_definitions.metadata['url']

        # Construct parameters
        query_parameters = {}
        if property_keys is not None:
            query_parameters['propertyKeys'] = self._serialize.query("property_keys", property_keys, '[str]', div=',')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfPropertyDefinition', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_multiple_property_definitions.metadata = {'url': '/data/lusid/propertydefinitions'}

    def create_property_definition(
            self, definition=None, custom_headers=None, raw=False, **operation_config):
        """Create property definition.

        Create a new property definition. Property definitions are perpetual -
        i.e. once a property definition has been created, it can be used for
        any effective date.

        :param definition:
        :type definition: ~lusidtr.models.CreatePropertyDefinitionRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PropertyDefinition or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PropertyDefinition or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.create_property_definition.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if definition is not None:
            body_content = self._serialize.body(definition, 'CreatePropertyDefinitionRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('PropertyDefinition', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_property_definition.metadata = {'url': '/data/lusid/propertydefinitions'}

    def get_property_definition(
            self, domain, scope, code, as_at=None, custom_headers=None, raw=False, **operation_config):
        """Get property definition.

        Gets the specified property definition.

        :param domain: Possible values include: 'Trade', 'Portfolio',
         'Holding', 'ReferenceHolding', 'TransactionConfiguration',
         'Instrument', 'CutDefinition'
        :type domain: str
        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param as_at:
        :type as_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PropertyDefinition or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PropertyDefinition or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_property_definition.metadata['url']
        path_format_arguments = {
            'domain': self._serialize.url("domain", domain, 'str'),
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PropertyDefinition', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_property_definition.metadata = {'url': '/data/lusid/propertydefinitions/{domain}/{scope}/{code}'}

    def update_property_definition(
            self, domain, scope, code, definition=None, custom_headers=None, raw=False, **operation_config):
        """Update property definition.

        Updates the specified property definition. Note, there are certain
        parts of the property definition that are not available to change, due
        to the impact on already validated and stored data.

        :param domain: Possible values include: 'Trade', 'Portfolio',
         'Holding', 'ReferenceHolding', 'TransactionConfiguration',
         'Instrument', 'CutDefinition'
        :type domain: str
        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param definition:
        :type definition: ~lusidtr.models.UpdatePropertyDefinitionRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PropertyDefinition or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PropertyDefinition or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.update_property_definition.metadata['url']
        path_format_arguments = {
            'domain': self._serialize.url("domain", domain, 'str'),
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if definition is not None:
            body_content = self._serialize.body(definition, 'UpdatePropertyDefinitionRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PropertyDefinition', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    update_property_definition.metadata = {'url': '/data/lusid/propertydefinitions/{domain}/{scope}/{code}'}

    def delete_property_definition(
            self, domain, scope, code, custom_headers=None, raw=False, **operation_config):
        """Delete property definition.

        Deletes the specified property definition.

        :param domain: Possible values include: 'Trade', 'Portfolio',
         'Holding', 'ReferenceHolding', 'TransactionConfiguration',
         'Instrument', 'CutDefinition'
        :type domain: str
        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_property_definition.metadata['url']
        path_format_arguments = {
            'domain': self._serialize.url("domain", domain, 'str'),
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_property_definition.metadata = {'url': '/data/lusid/propertydefinitions/{domain}/{scope}/{code}'}

    def upsert_quotes(
            self, scope, quotes=None, custom_headers=None, raw=False, **operation_config):
        """Upsert quotes.

        Upsert quotes effective at the specified time. If a quote is added with
        the same id (and is effective at the same time) as an existing quote,
        then the more recently added quote will be returned when queried.

        :param scope: The scope of the quotes
        :type scope: str
        :param quotes: The quotes to upsert
        :type quotes: list[~lusidtr.models.UpsertQuoteRequest]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpsertQuotesResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.UpsertQuotesResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_quotes.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if quotes is not None:
            body_content = self._serialize.body(quotes, '[UpsertQuoteRequest]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('UpsertQuotesResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_quotes.metadata = {'url': '/data/lusid/quotes/{scope}'}

    def delete_quote(
            self, scope, quotes=None, custom_headers=None, raw=False, **operation_config):
        """Delete a quote.

        Delete the specified quotes. In order for a quote to be deleted the id
        and effectiveFrom date must exactly match.

        :param scope: The scope of the quote
        :type scope: str
        :param quotes: The quotes to delete
        :type quotes: list[~lusidtr.models.DeleteQuoteRequest]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeleteQuotesResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeleteQuotesResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_quote.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if quotes is not None:
            body_content = self._serialize.body(quotes, '[DeleteQuoteRequest]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeleteQuotesResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_quote.metadata = {'url': '/data/lusid/quotes/{scope}/$delete'}

    def get_quotes(
            self, scope, quote_ids=None, effective_at=None, as_at=None, max_age=None, page=None, limit=None, custom_headers=None, raw=False, **operation_config):
        """Get quotes.

        Get quotes effective at the specified date/time (if any). An optional
        maximum age of quotes can be specified, and is infinite by default.
        Quotes which are older than this at the time of the effective date/time
        will not be returned.
        MaxAge is a duration of time represented in an ISO8601 format, eg.
        P1Y2M3DT4H30M (1 year, 2 months, 3 days, 4 hours and 30 minutes).
        The results are paged, and by default the 1st page of results is
        returned with a limit of 100 results per page.

        :param scope: The scope of the quotes
        :type scope: str
        :param quote_ids: The ids of the quotes
        :type quote_ids: list[~lusidtr.models.QuoteId]
        :param effective_at: Optional. The date/time from which the quotes are
         effective
        :type effective_at: datetime
        :param as_at: Optional. The 'AsAt' date/time
        :type as_at: datetime
        :param max_age: Optional. The quote staleness tolerance
        :type max_age: str
        :param page: Optional. The page of results to return
        :type page: int
        :param limit: Optional. The number of results per page
        :type limit: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: GetQuotesResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.GetQuotesResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_quotes.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if max_age is not None:
            query_parameters['maxAge'] = self._serialize.query("max_age", max_age, 'str')
        if page is not None:
            query_parameters['page'] = self._serialize.query("page", page, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if quote_ids is not None:
            body_content = self._serialize.body(quote_ids, '[QuoteId]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('GetQuotesResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_quotes.metadata = {'url': '/data/lusid/quotes/{scope}/$get'}

    def get_results(
            self, scope, key, date_parameter, as_at=None, sort_by=None, start=None, limit=None, custom_headers=None, raw=False, **operation_config):
        """Retrieve some previously stored results.

        :param scope: The scope of the data
        :type scope: str
        :param key: The key that identifies the data
        :type key: str
        :param date_parameter: The date for which the data was loaded
        :type date_parameter: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Results or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Results or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_results.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'key': self._serialize.url("key", key, 'str'),
            'date': self._serialize.url("date_parameter", date_parameter, 'iso-8601')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('Results', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_results.metadata = {'url': '/data/lusid/results/{scope}/{key}/{date}'}

    def upsert_results(
            self, scope, key, date_parameter, request=None, custom_headers=None, raw=False, **operation_config):
        """Upsert precalculated results against a specified scope/key/date
        combination.

        :param scope: The scope of the data
        :type scope: str
        :param key: The key that identifies the data
        :type key: str
        :param date_parameter: The date for which the data is relevant
        :type date_parameter: datetime
        :param request: The results to upload
        :type request: ~lusidtr.models.CreateResults
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Results or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Results or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_results.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'key': self._serialize.url("key", key, 'str'),
            'date': self._serialize.url("date_parameter", date_parameter, 'iso-8601')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'CreateResults')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('Results', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_results.metadata = {'url': '/data/lusid/results/{scope}/{key}/{date}'}

    def get_property_schema(
            self, property_keys=None, as_at=None, custom_headers=None, raw=False, **operation_config):
        """Get the schemas for the provided list of property keys.

        :param property_keys: A comma delimited list of property keys in
         string format. e.g.
         "Portfolio/default/PropertyName,Portfolio/differentScope/MyProperty"
        :type property_keys: list[str]
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PropertySchema or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PropertySchema or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_property_schema.metadata['url']

        # Construct parameters
        query_parameters = {}
        if property_keys is not None:
            query_parameters['propertyKeys'] = self._serialize.query("property_keys", property_keys, '[str]', div=',')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PropertySchema', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_property_schema.metadata = {'url': '/data/lusid/schemas/properties'}

    def get_value_types(
            self, sort_by=None, start=None, limit=None, custom_headers=None, raw=False, **operation_config):
        """Gets the available value types that could be returned in a schema.

        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfValueType or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfValueType or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_value_types.metadata['url']

        # Construct parameters
        query_parameters = {}
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfValueType', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_value_types.metadata = {'url': '/data/lusid/schemas/types'}

    def instruments_search(
            self, symbols=None, mastered_effective_at=None, mastered_only=False, custom_headers=None, raw=False, **operation_config):
        """Search instruments.

        Search through instruments that have been mastered in LUSID, and
        optionally augment results with instruments from a symbology service.

        :param symbols: A collection of instrument symbols to search for
        :type symbols: list[~lusidtr.models.InstrumentSearchProperty]
        :param mastered_effective_at: Optional. The effective date for
         searching mastered instruments. If this is not set, then the current
         date is taken.
         This parameter has no effect on instruments that have not been
         mastered within LUSID.
        :type mastered_effective_at: datetime
        :param mastered_only: Optional. If set to true, only search over
         instruments that have been mastered within LUSID. Default to false
        :type mastered_only: bool
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: list or ClientRawResponse if raw=true
        :rtype: list[~lusidtr.models.InstrumentMatch] or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.instruments_search.metadata['url']

        # Construct parameters
        query_parameters = {}
        if mastered_effective_at is not None:
            query_parameters['masteredEffectiveAt'] = self._serialize.query("mastered_effective_at", mastered_effective_at, 'iso-8601')
        if mastered_only is not None:
            query_parameters['masteredOnly'] = self._serialize.query("mastered_only", mastered_only, 'bool')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if symbols is not None:
            body_content = self._serialize.body(symbols, '[InstrumentSearchProperty]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('[InstrumentMatch]', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    instruments_search.metadata = {'url': '/data/lusid/search/Instruments'}

    def list_configuration_transaction_types(
            self, custom_headers=None, raw=False, **operation_config):
        """Gets the list of persisted transaction types.

        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfTransactionConfigurationData or
         ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfTransactionConfigurationData or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_configuration_transaction_types.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfTransactionConfigurationData', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_configuration_transaction_types.metadata = {'url': '/data/lusid/systemconfiguration/transactiontypes'}

    def set_configuration_transaction_types(
            self, types=None, custom_headers=None, raw=False, **operation_config):
        """Uploads a list of transaction types to be used by the movements engine.

        :param types:
        :type types: list[~lusidtr.models.TransactionConfigurationDataRequest]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfTransactionConfigurationData or
         ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfTransactionConfigurationData or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.set_configuration_transaction_types.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if types is not None:
            body_content = self._serialize.body(types, '[TransactionConfigurationDataRequest]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfTransactionConfigurationData', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    set_configuration_transaction_types.metadata = {'url': '/data/lusid/systemconfiguration/transactiontypes'}

    def add_configuration_transaction_type(
            self, type=None, custom_headers=None, raw=False, **operation_config):
        """Adds a new transaction type movement to the list of existing types.

        :param type:
        :type type: ~lusidtr.models.TransactionConfigurationDataRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfTransactionConfigurationData or
         ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfTransactionConfigurationData or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.add_configuration_transaction_type.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if type is not None:
            body_content = self._serialize.body(type, 'TransactionConfigurationDataRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('ResourceListOfTransactionConfigurationData', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    add_configuration_transaction_type.metadata = {'url': '/data/lusid/systemconfiguration/transactiontypes'}

    def reconcile_valuation(
            self, request=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Reconcile valuations performed on one or two sets of holdings using one
        or two configuration recipes.

        Perform valuation of one or two set of holdings using different one or
        two configuration recipes. Produce a breakdown of the resulting
        differences in valuation.

        :param request: The specifications of the inputs to the reconciliation
        :type request: ~lusidtr.models.ValuationsReconciliationRequest
        :param sort_by: Optional. Order the results by these fields. Use use
         the '-' sign to denote descending order e.g. -MyFieldName
        :type sort_by: list[str]
        :param start: Optional. When paginating, skip this number of results
        :type start: int
        :param limit: Optional. When paginating, limit the number of returned
         results to this many.
        :type limit: int
        :param filter: Optional. Expression to filter the result set
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfReconciliationBreak or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfReconciliationBreak or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.reconcile_valuation.metadata['url']

        # Construct parameters
        query_parameters = {}
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'ValuationsReconciliationRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfReconciliationBreak', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    reconcile_valuation.metadata = {'url': '/data/portfolios/$reconcileValuation'}

    def list_portfolios(
            self, effective_at=None, as_at=None, sort_by=None, start=None, limit=None, filter=None, query=None, custom_headers=None, raw=False, **operation_config):
        """List portfolios.

        List all portfolios matching the specified criteria.
        Example query syntax for the query parameter:
        - To see which portfolios have holdings in the specified instruments:
        instrument.identifiers in (('LusidInstrumentId', 'LUID_PPA8HI6M'),
        ('Figi', 'BBG000BLNNH6'))
        * Note that if a query is specified then it is executed for the current
        EffectiveAt and AsAt
        Specifying EffectiveAt or AsAt in addition to the query is not
        supported
        Also note that copy/pasting above examples results in incorrect single
        quote character.

        :param effective_at: Optional. The effective date of the data
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by: Optional. Order the results by these fields. Use use
         the '-' sign to denote descending order e.g. -MyFieldName
        :type sort_by: list[str]
        :param start: Optional. When paginating, skip this number of results
        :type start: int
        :param limit: Optional. When paginating, limit the number of returned
         results to this many.
        :type limit: int
        :param filter: Optional. Expression to filter the result set
        :type filter: str
        :param query: Optional. Expression specifying the criteria that the
         returned portfolios must meet
        :type query: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfPortfolio or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfPortfolio or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_portfolios.metadata['url']

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')
        if query is not None:
            query_parameters['query'] = self._serialize.query("query", query, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfPortfolio', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_portfolios.metadata = {'url': '/data/portfolios/common'}

    def list_portfolios_for_scope(
            self, scope, effective_at=None, as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """List portfolios for scope.

        List all the portfolios in the specified scope.

        :param scope: The scope
        :type scope: str
        :param effective_at: Optional. The effective date of the data
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by: Optional. Order the results by these fields. Use use
         the '-' sign to denote descending order e.g. -MyFieldName
        :type sort_by: list[str]
        :param start: Optional. When paginating, skip this number of results
        :type start: int
        :param limit: Optional. When paginating, limit the number of returned
         results to this many.
        :type limit: int
        :param filter: Optional. Expression to filter the result set
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfPortfolio or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfPortfolio or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_portfolios_for_scope.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfPortfolio', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_portfolios_for_scope.metadata = {'url': '/data/portfolios/common/{scope}'}

    def get_portfolio(
            self, scope, code, effective_at=None, as_at=None, custom_headers=None, raw=False, **operation_config):
        """Get portfolio.

        Gets a single portfolio by code.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: Effective date
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Portfolio or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Portfolio or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_portfolio.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('Portfolio', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_portfolio.metadata = {'url': '/data/portfolios/common/{scope}/{code}'}

    def update_portfolio(
            self, scope, code, request=None, effective_at=None, custom_headers=None, raw=False, **operation_config):
        """Update portfolio.

        :param scope: The scope of the portfolio to be updated
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param request: The update request
        :type request: ~lusidtr.models.UpdatePortfolioRequest
        :param effective_at: The effective date for the change
        :type effective_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Portfolio or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Portfolio or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.update_portfolio.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'UpdatePortfolioRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('Portfolio', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    update_portfolio.metadata = {'url': '/data/portfolios/common/{scope}/{code}'}

    def delete_portfolio(
            self, scope, code, effective_at=None, custom_headers=None, raw=False, **operation_config):
        """Delete portfolio.

        Deletes a portfolio from the given effectiveAt.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: Effective date
        :type effective_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_portfolio.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_portfolio.metadata = {'url': '/data/portfolios/common/{scope}/{code}'}

    def get_portfolio_commands(
            self, scope, code, from_as_at=None, to_as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Get modifications.

        Gets all commands that modified the portfolio.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: The portfolio id
        :type code: str
        :param from_as_at: Filters commands by those that were processed at or
         after this time. Null means there is no lower limit.
        :type from_as_at: datetime
        :param to_as_at: Filters commands by those that were processed at or
         before this time. Null means there is no upper limit (latest).
        :type to_as_at: datetime
        :param sort_by: Optional. Order the results by these fields. Use use
         the '-' sign to denote descending order e.g. -MyFieldName
        :type sort_by: list[str]
        :param start: Optional. When paginating, skip this number of results
        :type start: int
        :param limit: Optional. When paginating, limit the number of returned
         results to this many.
        :type limit: int
        :param filter:
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfProcessedCommand or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfProcessedCommand or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_portfolio_commands.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if from_as_at is not None:
            query_parameters['fromAsAt'] = self._serialize.query("from_as_at", from_as_at, 'iso-8601')
        if to_as_at is not None:
            query_parameters['toAsAt'] = self._serialize.query("to_as_at", to_as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfProcessedCommand', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_portfolio_commands.metadata = {'url': '/data/portfolios/common/{scope}/{code}/commands'}

    def get_portfolio_properties(
            self, scope, code, effective_at=None, as_at=None, sort_by=None, start=None, limit=None, custom_headers=None, raw=False, **operation_config):
        """Get properties.

        Get properties attached to the portfolio.  If the asAt is not specified
        then
        the latest system time is used.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: Effective date
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by: Optional. Order the results by these fields. Use use
         the '-' sign to denote descending order e.g. -MyFieldName
        :type sort_by: list[str]
        :param start: Optional. When paginating, skip this number of results
        :type start: int
        :param limit: Optional. When paginating, limit the number of returned
         results to this many.
        :type limit: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioProperties or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioProperties or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_portfolio_properties.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PortfolioProperties', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_portfolio_properties.metadata = {'url': '/data/portfolios/common/{scope}/{code}/properties'}

    def upsert_portfolio_properties(
            self, scope, code, portfolio_properties=None, effective_at=None, custom_headers=None, raw=False, **operation_config):
        """Update properties.

        Create one or more properties on a portfolio.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param portfolio_properties:
        :type portfolio_properties: dict[str, ~lusidtr.models.PropertyValue]
        :param effective_at: The effective date for the change
        :type effective_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioProperties or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioProperties or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_portfolio_properties.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if portfolio_properties is not None:
            body_content = self._serialize.body(portfolio_properties, '{PropertyValue}')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PortfolioProperties', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_portfolio_properties.metadata = {'url': '/data/portfolios/common/{scope}/{code}/properties'}

    def delete_portfolio_properties(
            self, scope, code, effective_at=None, portfolio_property_keys=None, custom_headers=None, raw=False, **operation_config):
        """Delete one, many or all properties from a portfolio for a specified
        effective date.

        Specifying no properties will delete all properties.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: Effective date
        :type effective_at: datetime
        :param portfolio_property_keys: The keys of the property to be
         deleted. None specified indicates the intent to delete all properties
        :type portfolio_property_keys: list[str]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_portfolio_properties.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if portfolio_property_keys is not None:
            query_parameters['portfolioPropertyKeys'] = self._serialize.query("portfolio_property_keys", portfolio_property_keys, '[str]', div=',')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_portfolio_properties.metadata = {'url': '/data/portfolios/common/{scope}/{code}/properties'}

    def create_derived_portfolio(
            self, scope, portfolio=None, custom_headers=None, raw=False, **operation_config):
        """Create derived portfolio.

        Creates a portfolio that derives from an existing portfolio.

        :param scope: The scope into which to create the new derived portfolio
        :type scope: str
        :param portfolio: The root object of the new derived portfolio,
         containing a populated reference portfolio id and reference scope
        :type portfolio:
         ~lusidtr.models.CreateDerivedTransactionPortfolioRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Portfolio or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Portfolio or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.create_derived_portfolio.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if portfolio is not None:
            body_content = self._serialize.body(portfolio, 'CreateDerivedTransactionPortfolioRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('Portfolio', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_derived_portfolio.metadata = {'url': '/data/portfolios/derivedtransactionportfolios/{scope}'}

    def delete_derived_portfolio_details(
            self, scope, code, effective_at=None, custom_headers=None, raw=False, **operation_config):
        """Delete portfolio details.

        Deletes the portfolio details for the given code.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: The effective date of the change
        :type effective_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_derived_portfolio_details.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_derived_portfolio_details.metadata = {'url': '/data/portfolios/derivedtransactionportfolios/{scope}/{code}/details'}

    def reconcile_holdings(
            self, request=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Perform a reconciliation between two portfolios.

        :param request:
        :type request: ~lusidtr.models.PortfoliosReconciliationRequest
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param filter:
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfReconciliationBreak or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfReconciliationBreak or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.reconcile_holdings.metadata['url']

        # Construct parameters
        query_parameters = {}
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'PortfoliosReconciliationRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfReconciliationBreak', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    reconcile_holdings.metadata = {'url': '/data/portfolios/functions/common/$reconcileholdings'}

    def list_portfolio_groups(
            self, scope, as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """List all groups in a specified scope.

        :param scope:
        :type scope: str
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param filter: A filter expression to apply to the result set
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfPortfolioGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfPortfolioGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_portfolio_groups.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfPortfolioGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_portfolio_groups.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}'}

    def create_portfolio_group(
            self, scope, request=None, custom_headers=None, raw=False, **operation_config):
        """Create a new group.

        :param scope:
        :type scope: str
        :param request:
        :type request: ~lusidtr.models.CreatePortfolioGroupRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.create_portfolio_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'CreatePortfolioGroupRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('PortfolioGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_portfolio_group.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}'}

    def get_portfolio_group(
            self, scope, code, as_at=None, custom_headers=None, raw=False, **operation_config):
        """Get an existing group.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_portfolio_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PortfolioGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_portfolio_group.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}'}

    def update_portfolio_group(
            self, scope, code, request=None, custom_headers=None, raw=False, **operation_config):
        """Update an existing group.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param request:
        :type request: ~lusidtr.models.UpdatePortfolioGroupRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.update_portfolio_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if request is not None:
            body_content = self._serialize.body(request, 'UpdatePortfolioGroupRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('PortfolioGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    update_portfolio_group.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}'}

    def delete_portfolio_group(
            self, scope, code, custom_headers=None, raw=False, **operation_config):
        """Delete a group.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_portfolio_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_portfolio_group.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}'}

    def get_portfolio_group_commands(
            self, scope, code, from_as_at=None, to_as_at=None, sort_by=None, start=None, limit=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Gets all commands that modified the portfolio groups(s) with the
        specified id.

        :param scope: The scope of the portfolio group
        :type scope: str
        :param code: The portfolio group id
        :type code: str
        :param from_as_at: Filters commands by those that were processed at or
         after this time. Null means there is no lower limit.
        :type from_as_at: datetime
        :param to_as_at: Filters commands by those that were processed at or
         before this time. Null means there is no upper limit (latest).
        :type to_as_at: datetime
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param filter: A filter expression to apply to the result set
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfProcessedCommand or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.ResourceListOfProcessedCommand or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_portfolio_group_commands.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if from_as_at is not None:
            query_parameters['fromAsAt'] = self._serialize.query("from_as_at", from_as_at, 'iso-8601')
        if to_as_at is not None:
            query_parameters['toAsAt'] = self._serialize.query("to_as_at", to_as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfProcessedCommand', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_portfolio_group_commands.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}/commands'}

    def get_portfolio_group_expansion(
            self, scope, code, effective_at=None, as_at=None, property_filter=None, custom_headers=None, raw=False, **operation_config):
        """Get a full expansion of an existing group.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param effective_at:
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param property_filter:
        :type property_filter: list[str]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ExpandedGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ExpandedGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_portfolio_group_expansion.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if property_filter is not None:
            query_parameters['propertyFilter'] = self._serialize.query("property_filter", property_filter, '[str]', div=',')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ExpandedGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_portfolio_group_expansion.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}/expansion'}

    def add_portfolio_to_group(
            self, scope, code, identifier=None, custom_headers=None, raw=False, **operation_config):
        """Add a portfolio to an existing group.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param identifier:
        :type identifier: ~lusidtr.models.ResourceId
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.add_portfolio_to_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if identifier is not None:
            body_content = self._serialize.body(identifier, 'ResourceId')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('PortfolioGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    add_portfolio_to_group.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}/portfolios'}

    def delete_portfolio_from_group(
            self, scope, code, portfolio_scope, portfolio_code, custom_headers=None, raw=False, **operation_config):
        """Remove a portfolio that is currently present within an existing group.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param portfolio_scope:
        :type portfolio_scope: str
        :param portfolio_code:
        :type portfolio_code: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_portfolio_from_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'portfolioScope': self._serialize.url("portfolio_scope", portfolio_scope, 'str'),
            'portfolioCode': self._serialize.url("portfolio_code", portfolio_code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PortfolioGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_portfolio_from_group.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}/portfolios/{portfolioScope}/{portfolioCode}'}

    def add_sub_group_to_group(
            self, scope, code, identifier=None, custom_headers=None, raw=False, **operation_config):
        """Add a sub group to an existing group.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param identifier:
        :type identifier: ~lusidtr.models.ResourceId
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.add_sub_group_to_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if identifier is not None:
            body_content = self._serialize.body(identifier, 'ResourceId')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('PortfolioGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    add_sub_group_to_group.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}/subgroups'}

    def delete_sub_group_from_group(
            self, scope, code, subgroup_scope, subgroup_code, custom_headers=None, raw=False, **operation_config):
        """Remove a subgroup that is currently present within an existing group.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param subgroup_scope:
        :type subgroup_scope: str
        :param subgroup_code:
        :type subgroup_code: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioGroup or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioGroup or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_sub_group_from_group.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'subgroupScope': self._serialize.url("subgroup_scope", subgroup_scope, 'str'),
            'subgroupCode': self._serialize.url("subgroup_code", subgroup_code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PortfolioGroup', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_sub_group_from_group.metadata = {'url': '/data/portfolios/portfoliogroups/{scope}/{code}/subgroups/{subgroupScope}/{subgroupCode}'}

    def create_reference_portfolio(
            self, scope, reference_portfolio=None, custom_headers=None, raw=False, **operation_config):
        """Create a new reference portfolio.

        :param scope: The intended scope of the portfolio
        :type scope: str
        :param reference_portfolio: The portfolio creation request object
        :type reference_portfolio:
         ~lusidtr.models.CreateReferencePortfolioRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Portfolio or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Portfolio or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.create_reference_portfolio.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if reference_portfolio is not None:
            body_content = self._serialize.body(reference_portfolio, 'CreateReferencePortfolioRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('Portfolio', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_reference_portfolio.metadata = {'url': '/data/portfolios/referenceportfolios/{scope}'}

    def get_reference_portfolio_constituents(
            self, scope, code, effective_at, as_at=None, sort_by=None, start=None, limit=None, custom_headers=None, raw=False, **operation_config):
        """Get all the constituents in a reference portfolio.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param effective_at:
        :type effective_at: datetime
        :param as_at:
        :type as_at: datetime
        :param sort_by:
        :type sort_by: list[str]
        :param start:
        :type start: int
        :param limit:
        :type limit: int
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: GetReferencePortfolioConstituentsResponse or
         ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.GetReferencePortfolioConstituentsResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_reference_portfolio_constituents.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'effectiveAt': self._serialize.url("effective_at", effective_at, 'iso-8601')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('GetReferencePortfolioConstituentsResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_reference_portfolio_constituents.metadata = {'url': '/data/portfolios/referenceportfolios/{scope}/{code}/{effectiveAt}/constituents'}

    def upsert_reference_portfolio_constituents(
            self, scope, code, constituents=None, custom_headers=None, raw=False, **operation_config):
        """Add constituents to a specific reference portfolio.

        :param scope:
        :type scope: str
        :param code:
        :type code: str
        :param constituents:
        :type constituents:
         ~lusidtr.models.UpsertReferencePortfolioConstituentsRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpsertReferencePortfolioConstituentsResponse or
         ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.UpsertReferencePortfolioConstituentsResponse
         or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_reference_portfolio_constituents.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if constituents is not None:
            body_content = self._serialize.body(constituents, 'UpsertReferencePortfolioConstituentsRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('UpsertReferencePortfolioConstituentsResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_reference_portfolio_constituents.metadata = {'url': '/data/portfolios/referenceportfolios/{scope}/{code}/constituents'}

    def list_constituents_adjustments(
            self, scope, code, from_effective_at=None, to_effective_at=None, as_at_time=None, custom_headers=None, raw=False, **operation_config):
        """Gets constituents adjustments in an interval of effective time.

        Specify a time period in which you'd like to see the list of times that
        adjustments where made to this portfolio.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param from_effective_at: Events between this time (inclusive) and the
         toEffectiveAt are returned.
        :type from_effective_at: datetime
        :param to_effective_at: Events between this time (inclusive) and the
         fromEffectiveAt are returned.
        :type to_effective_at: datetime
        :param as_at_time: The as-at time for which the result is valid.
        :type as_at_time: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfConstituentsAdjustmentHeader or
         ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.ResourceListOfConstituentsAdjustmentHeader or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_constituents_adjustments.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if from_effective_at is not None:
            query_parameters['fromEffectiveAt'] = self._serialize.query("from_effective_at", from_effective_at, 'iso-8601')
        if to_effective_at is not None:
            query_parameters['toEffectiveAt'] = self._serialize.query("to_effective_at", to_effective_at, 'iso-8601')
        if as_at_time is not None:
            query_parameters['asAtTime'] = self._serialize.query("as_at_time", as_at_time, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfConstituentsAdjustmentHeader', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_constituents_adjustments.metadata = {'url': '/data/portfolios/referenceportfolios/{scope}/{code}/constituentsadjustments'}

    def create_portfolio(
            self, scope, create_request=None, custom_headers=None, raw=False, **operation_config):
        """Create portfolio.

        Creates a new portfolio.

        :param scope: The intended scope of the portfolio
        :type scope: str
        :param create_request: The portfolio creation request object
        :type create_request:
         ~lusidtr.models.CreateTransactionPortfolioRequest
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Portfolio or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.Portfolio or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.create_portfolio.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if create_request is not None:
            body_content = self._serialize.body(create_request, 'CreateTransactionPortfolioRequest')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [201]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 201:
            deserialized = self._deserialize('Portfolio', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_portfolio.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}'}

    def get_details(
            self, scope, code, effective_at=None, as_at=None, custom_headers=None, raw=False, **operation_config):
        """Get portfolio details.

        Gets the details for a portfolio.  For a derived portfolio this can be
        the details of another reference portfolio.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: Effective date
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioDetails or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioDetails or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_details.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PortfolioDetails', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_details.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/details'}

    def upsert_portfolio_details(
            self, scope, code, details=None, effective_at=None, custom_headers=None, raw=False, **operation_config):
        """Add/update portfolio details.

        Update the portfolio details for the given code or add if it doesn't
        already exist. Updates with
        null values will remove any existing values.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param details:
        :type details: ~lusidtr.models.CreatePortfolioDetails
        :param effective_at: The effective date of the change
        :type effective_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PortfolioDetails or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.PortfolioDetails or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_portfolio_details.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if details is not None:
            body_content = self._serialize.body(details, 'CreatePortfolioDetails')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('PortfolioDetails', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_portfolio_details.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/details'}

    def upsert_executions(
            self, scope, code, executions=None, custom_headers=None, raw=False, **operation_config):
        """Upsert executions.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param executions: The executions to be updated
        :type executions: list[~lusidtr.models.ExecutionRequest]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpsertPortfolioExecutionsResponse or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.UpsertPortfolioExecutionsResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_executions.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if executions is not None:
            body_content = self._serialize.body(executions, '[ExecutionRequest]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('UpsertPortfolioExecutionsResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_executions.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/executions'}

    def get_holdings(
            self, scope, code, by_taxlots=None, effective_at=None, as_at=None, sort_by=None, start=None, limit=None, filter=None, instrument_property_keys=None, custom_headers=None, raw=False, **operation_config):
        """Get holdings.

        Get the aggregate holdings of a portfolio.  If no effectiveAt or asAt
        are supplied then values will be defaulted to the latest system time.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param by_taxlots: Option to expand holdings to return the underlying
         tax-lots
        :type by_taxlots: bool
        :param effective_at: Effective date
        :type effective_at: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by: The columns to sort the returned data by
        :type sort_by: list[str]
        :param start: How many items to skip from the returned set
        :type start: int
        :param limit: How many items to return from the set
        :type limit: int
        :param filter: A filter on the results
        :type filter: str
        :param instrument_property_keys: Keys for the instrument properties to
         be decorated onto the holdings
        :type instrument_property_keys: list[str]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: VersionedResourceListOfPortfolioHolding or ClientRawResponse
         if raw=true
        :rtype: ~lusidtr.models.VersionedResourceListOfPortfolioHolding or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_holdings.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if by_taxlots is not None:
            query_parameters['byTaxlots'] = self._serialize.query("by_taxlots", by_taxlots, 'bool')
        if effective_at is not None:
            query_parameters['effectiveAt'] = self._serialize.query("effective_at", effective_at, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')
        if instrument_property_keys is not None:
            query_parameters['instrumentPropertyKeys'] = self._serialize.query("instrument_property_keys", instrument_property_keys, '[str]', div=',')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('VersionedResourceListOfPortfolioHolding', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_holdings.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/holdings'}

    def set_holdings(
            self, scope, code, effective_at, holding_adjustments=None, custom_headers=None, raw=False, **operation_config):
        """Set All Holdings.

        Create transactions in a specific portfolio to bring all holdings to
        the specified targets.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: Effective date
        :type effective_at: datetime
        :param holding_adjustments:
        :type holding_adjustments: list[~lusidtr.models.AdjustHoldingRequest]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: AdjustHolding or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.AdjustHolding or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.set_holdings.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'effectiveAt': self._serialize.url("effective_at", effective_at, 'iso-8601')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if holding_adjustments is not None:
            body_content = self._serialize.body(holding_adjustments, '[AdjustHoldingRequest]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.put(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('AdjustHolding', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    set_holdings.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/holdings/{effectiveAt}'}

    def adjust_holdings(
            self, scope, code, effective_at, holding_adjustments=None, custom_headers=None, raw=False, **operation_config):
        """Adjust Selected Holdings.

        Create transactions in a specific portfolio to bring the selected
        holdings up to the specified targets.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: Effective date
        :type effective_at: datetime
        :param holding_adjustments:
        :type holding_adjustments: list[~lusidtr.models.AdjustHoldingRequest]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: AdjustHolding or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.AdjustHolding or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.adjust_holdings.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'effectiveAt': self._serialize.url("effective_at", effective_at, 'iso-8601')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if holding_adjustments is not None:
            body_content = self._serialize.body(holding_adjustments, '[AdjustHoldingRequest]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('AdjustHolding', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    adjust_holdings.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/holdings/{effectiveAt}'}

    def cancel_adjust_holdings(
            self, scope, code, effective_at, custom_headers=None, raw=False, **operation_config):
        """Cancel adjust-holdings.

        Cancels a previous adjust holdings request.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: Effective date
        :type effective_at: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.cancel_adjust_holdings.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'effectiveAt': self._serialize.url("effective_at", effective_at, 'iso-8601')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    cancel_adjust_holdings.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/holdings/{effectiveAt}'}

    def list_holdings_adjustments(
            self, scope, code, from_effective_at=None, to_effective_at=None, as_at_time=None, custom_headers=None, raw=False, **operation_config):
        """Gets holdings adjustments in an interval of effective time.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param from_effective_at: Events between this time (inclusive) and the
         toEffectiveAt are returned.
        :type from_effective_at: datetime
        :param to_effective_at: Events between this time (inclusive) and the
         fromEffectiveAt are returned.
        :type to_effective_at: datetime
        :param as_at_time: The as-at time for which the result is valid.
        :type as_at_time: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: ResourceListOfHoldingsAdjustmentHeader or ClientRawResponse
         if raw=true
        :rtype: ~lusidtr.models.ResourceListOfHoldingsAdjustmentHeader or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.list_holdings_adjustments.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if from_effective_at is not None:
            query_parameters['fromEffectiveAt'] = self._serialize.query("from_effective_at", from_effective_at, 'iso-8601')
        if to_effective_at is not None:
            query_parameters['toEffectiveAt'] = self._serialize.query("to_effective_at", to_effective_at, 'iso-8601')
        if as_at_time is not None:
            query_parameters['asAtTime'] = self._serialize.query("as_at_time", as_at_time, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('ResourceListOfHoldingsAdjustmentHeader', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    list_holdings_adjustments.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/holdingsadjustments'}

    def get_holdings_adjustment(
            self, scope, code, effective_at, as_at_time=None, custom_headers=None, raw=False, **operation_config):
        """Get a holdings adjustment for a single portfolio at a specific
        effective time.
        If no adjustment exists at this effective time, not found is returned.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param effective_at: The effective time of the holdings adjustment.
        :type effective_at: datetime
        :param as_at_time: The as-at time for which the result is valid.
        :type as_at_time: datetime
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: HoldingsAdjustment or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.HoldingsAdjustment or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_holdings_adjustment.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'effectiveAt': self._serialize.url("effective_at", effective_at, 'iso-8601')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if as_at_time is not None:
            query_parameters['asAtTime'] = self._serialize.query("as_at_time", as_at_time, 'iso-8601')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('HoldingsAdjustment', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_holdings_adjustment.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/holdingsadjustments/{effectiveAt}'}

    def get_transactions(
            self, scope, code, from_transaction_date=None, to_transaction_date=None, as_at=None, sort_by=None, start=None, limit=None, instrument_property_keys=None, filter=None, custom_headers=None, raw=False, **operation_config):
        """Get transactions.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param from_transaction_date: Include transactions with a transaction
         date equal or later than this date. If not supplied, no lower filter
         is applied
        :type from_transaction_date: datetime
        :param to_transaction_date: Include transactions with a transaction
         date equal or before this date. If not supplied, no upper filter is
         applied
        :type to_transaction_date: datetime
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by: The columns to sort the returned data by
        :type sort_by: list[str]
        :param start: How many items to skip from the returned set
        :type start: int
        :param limit: How many items to return from the set
        :type limit: int
        :param instrument_property_keys: Keys for the instrument properties to
         be decorated onto the transactions
        :type instrument_property_keys: list[str]
        :param filter: Transaction filter
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: VersionedResourceListOfTransaction or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.VersionedResourceListOfTransaction or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.get_transactions.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if from_transaction_date is not None:
            query_parameters['fromTransactionDate'] = self._serialize.query("from_transaction_date", from_transaction_date, 'iso-8601')
        if to_transaction_date is not None:
            query_parameters['toTransactionDate'] = self._serialize.query("to_transaction_date", to_transaction_date, 'iso-8601')
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if instrument_property_keys is not None:
            query_parameters['instrumentPropertyKeys'] = self._serialize.query("instrument_property_keys", instrument_property_keys, '[str]', div=',')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('VersionedResourceListOfTransaction', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_transactions.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/transactions'}

    def upsert_transactions(
            self, scope, code, transactions=None, custom_headers=None, raw=False, **operation_config):
        """Upsert transactions.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param transactions: The transactions to be updated
        :type transactions: list[~lusidtr.models.TransactionRequest]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpsertPortfolioTransactionsResponse or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.UpsertPortfolioTransactionsResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.upsert_transactions.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if transactions is not None:
            body_content = self._serialize.body(transactions, '[TransactionRequest]')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('UpsertPortfolioTransactionsResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    upsert_transactions.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/transactions'}

    def delete_transactions(
            self, scope, code, id=None, custom_headers=None, raw=False, **operation_config):
        """Delete transactions.

        Delete one or more transactions from a portfolio.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param id: Ids of transactions to delete
        :type id: list[str]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_transactions.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if id is not None:
            query_parameters['id'] = self._serialize.query("id", id, '[str]', div=',')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_transactions.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/transactions'}

    def add_transaction_property(
            self, scope, code, transaction_id, transaction_properties=None, custom_headers=None, raw=False, **operation_config):
        """Add/update transaction properties.

        Add one or more properties to a specific transaction in a portfolio.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param transaction_id: Id of transaction to add properties to
        :type transaction_id: str
        :param transaction_properties: Transaction properties to add
        :type transaction_properties: dict[str,
         ~lusidtr.models.PerpetualPropertyValue]
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: AddTransactionPropertyResponse or ClientRawResponse if
         raw=true
        :rtype: ~lusidtr.models.AddTransactionPropertyResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.add_transaction_property.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'transactionId': self._serialize.url("transaction_id", transaction_id, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if transaction_properties is not None:
            body_content = self._serialize.body(transaction_properties, '{PerpetualPropertyValue}')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('AddTransactionPropertyResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    add_transaction_property.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/transactions/{transactionId}/properties'}

    def delete_property_from_transaction(
            self, scope, code, transaction_id, transaction_property_key=None, custom_headers=None, raw=False, **operation_config):
        """Delete transaction property.

        Delete a property from a specific transaction.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param transaction_id: Id of the transaction to delete the property
         from
        :type transaction_id: str
        :param transaction_property_key: The key of the property to be deleted
        :type transaction_property_key: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeletedEntityResponse or ClientRawResponse if raw=true
        :rtype: ~lusidtr.models.DeletedEntityResponse or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.delete_property_from_transaction.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str'),
            'transactionId': self._serialize.url("transaction_id", transaction_id, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if transaction_property_key is not None:
            query_parameters['transactionPropertyKey'] = self._serialize.query("transaction_property_key", transaction_property_key, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('DeletedEntityResponse', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    delete_property_from_transaction.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/transactions/{transactionId}/properties'}

    def build_transactions(
            self, scope, code, as_at=None, sort_by=None, start=None, limit=None, instrument_property_keys=None, filter=None, parameters=None, custom_headers=None, raw=False, **operation_config):
        """Get transactions.

        :param scope: The scope of the portfolio
        :type scope: str
        :param code: Code for the portfolio
        :type code: str
        :param as_at: Optional. The AsAt date of the data
        :type as_at: datetime
        :param sort_by: The columns to sort the returned data by
        :type sort_by: list[str]
        :param start: How many items to skip from the returned set
        :type start: int
        :param limit: How many items to return from the set
        :type limit: int
        :param instrument_property_keys: Keys for the instrument properties to
         be decorated onto the trades
        :type instrument_property_keys: list[str]
        :param filter: Trade filter
        :type filter: str
        :param parameters: Core query parameters
        :type parameters: ~lusidtr.models.TransactionQueryParameters
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: VersionedResourceListOfOutputTransaction or ClientRawResponse
         if raw=true
        :rtype: ~lusidtr.models.VersionedResourceListOfOutputTransaction or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<lusidtr.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.build_transactions.metadata['url']
        path_format_arguments = {
            'scope': self._serialize.url("scope", scope, 'str'),
            'code': self._serialize.url("code", code, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if as_at is not None:
            query_parameters['asAt'] = self._serialize.query("as_at", as_at, 'iso-8601')
        if sort_by is not None:
            query_parameters['sortBy'] = self._serialize.query("sort_by", sort_by, '[str]', div=',')
        if start is not None:
            query_parameters['start'] = self._serialize.query("start", start, 'int')
        if limit is not None:
            query_parameters['limit'] = self._serialize.query("limit", limit, 'int')
        if instrument_property_keys is not None:
            query_parameters['instrumentPropertyKeys'] = self._serialize.query("instrument_property_keys", instrument_property_keys, '[str]', div=',')
        if filter is not None:
            query_parameters['filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        if parameters is not None:
            body_content = self._serialize.body(parameters, 'TransactionQueryParameters')
        else:
            body_content = None

        # Construct and send request
        request = self._client.post(url, query_parameters)
        response = self._client.send(
            request, header_parameters, body_content, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('VersionedResourceListOfOutputTransaction', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    build_transactions.metadata = {'url': '/data/portfolios/transactionportfolios/{scope}/{code}/transactions/$build'}

    def enable_search_lambda(
            self, custom_headers=None, raw=False, **operation_config):
        """Enable Search.

        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: None or ClientRawResponse if raw=true
        :rtype: None or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        # Construct URL
        url = self.enable_search_lambda.metadata['url']

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters)
        response = self._client.send(request, header_parameters, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise HttpOperationError(self._deserialize, response)

        if raw:
            client_raw_response = ClientRawResponse(None, response)
            return client_raw_response
    enable_search_lambda.metadata = {'url': '/data/portfolios/enablesearch'}
