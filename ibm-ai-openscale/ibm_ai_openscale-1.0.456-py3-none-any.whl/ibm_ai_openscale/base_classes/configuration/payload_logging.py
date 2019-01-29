# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import datetime
import uuid
from ibm_ai_openscale.utils import *
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale.base_classes.configuration.table_from_rest_api_viewer import TableFromRestApiViewer


_DEFAULT_LIST_LENGTH = 50


class PayloadLogging(TableFromRestApiViewer):
    """Manage payload logging for asset."""
    def __init__(self, subscription, ai_client):
        TableFromRestApiViewer.__init__(self, ai_client, subscription, self)
        self._ai_client = ai_client

    def enable(self, dynamic_schema_update=None):
        """
        Enables payload logging.

        :param dynamic_schema_update: schema will be automatically updated when asset will be scored (optional)
        :type dynamic_schema_update: bool
        """

        payload = {
            "enabled": True,
        }

        if dynamic_schema_update is not None:
            payload['parameters'] = {
                'dynamic_schema_update': dynamic_schema_update
            }

        response = requests_session.put(
            self._ai_client._href_definitions.get_payload_logging_href(self._subscription.binding_uid, self._subscription.uid),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'payload logging setup', response)

    def get_details(self):
        """
        Will return details of payload logging. Info about configuration.

        :return: configuration of payload logging
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_payload_logging_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'payload logging configuration', response)

    def disable(self):
        """
        Disables payload logging.
        """

        response = requests_session.put(
            self._ai_client._href_definitions.get_payload_logging_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'payload logging unset', response)

    def store(self, request=None, response=None, records=None, scoring_id=None, scoring_timestamp=None, response_time=None, deployment_id=None):
        """
         Stores payload records in payload logging table.

         :param records: PayloadRecord objects containing request, response and additional metrics to be stored.
         :type records: list of PayloadRecord objects

         :param deployment_id: deployment identifier (optional). If not provided first deployment id from subscription is taken.
         :type deployment_id: str


         A way you might use me is:

         >>> from ibm_ai_openscale.supporting_classes import PayloadRecord
         >>>
         >>> records_list = [PayloadRecord(request=request1, response=response1, response_time=time1), PayloadRecord(request=request2, response=response2, response_time=time2)]
         >>> subscription.payload_logging.store(records_list)

        """

        if request is not None:
            # DeprecationWarning does not work in notebook - need to use print as workaround sic!
            # TODO remove in next major release support for this
            print("DeprecationWarning: 'request, response, scoring_id, scoring_timestamp, response_time' parameters are deprecated and will be removed in 1.1.0 release; use 'records' instead.")
            self._store_deprecated(request=request, response=response, scoring_id=scoring_id, scoring_timestamp=scoring_timestamp, response_time=response_time, deployment_id=deployment_id)
        else:
            self._store_multiple_records(records=records, deployment_id=deployment_id)

    def _store_multiple_records(self, records, deployment_id=None):
        """
        Stores payload records in payload logging table.

        :param records: PayloadRecord objects containing request, response and additional metrics to be stored.
        :type records: list of PayloadRecord objects

        :param deployment_id: deployment identifier (optional). If not provided first deployment id from subscription is taken.
        :type deployment_id: str


        A way you might use me is:

        >>> from ibm_ai_openscale.supporting_classes import PayloadRecord
        >>>
        >>> records_list = [PayloadRecord(request=request1, response=response1, response_time=time1), PayloadRecord(request=request2, response=response2, response_time=time2)]
        >>> subscription.payload_logging.store(records_list)

        """
        validate_type(records, "records", list, True)
        validate_type(records[0], "record", PayloadRecord, True)
        validate_type(deployment_id, "deployment_id", str, False)

        if deployment_id is not None:
            deployment_uid = deployment_id
        else:
            deployments = self._subscription.get_details()['entity']['deployments']
            if len(deployments) > 0:
                deployment_uid = deployments[0]['deployment_id']
            else:
                deployment_uid = 'generic_deployment'

        payload = []

        for record in records:
            payload.append(record._to_json(binding_uid=self._subscription.binding_uid, subscription_uid=self._subscription.uid, deployment_uid=deployment_uid))

        response = requests_session.post(
            self._ai_client._href_definitions.get_payload_logging_storage_href(),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        handle_response(202, u'payload logging storage', response)

    def _store_deprecated(self, request, response, scoring_id=None, scoring_timestamp=None, response_time=None, deployment_id=None):
        """
        Stores payload logging in payload logging table.

        :param request: scoring request
        :type request: dict

        :param response: scoring response
        :type response: dict

        :param scoring_id: scoring identifier (optional). If not provided random uid is assigned.
        :type scoring_id: str

        :param scoring_timestamp: scoring request timestamp (optional). If not provided current time is assigned.
        :type scoring_timestamp: str

        :param response_time: scoring response time in ms (optional)
        :type response: int or float

        :param deployment_id: deployment identifier (optional). If not provided first deployment id from subscription is taken.
        :type deployment_id: str

        """

        validate_type(request, "request", dict, True)
        validate_type(response, "response", dict, True)
        validate_type(scoring_id, "scoring_id", str, False)
        validate_type(deployment_id, "deployment_id", str, False)
        validate_type(scoring_timestamp, "scoring_timestamp", str, False)
        validate_type(response_time, "response_time", [int, float], False)

        if deployment_id is not None:
            deployment_uid = deployment_id
        else:
            deployments = self._subscription.get_details()['entity']['deployments']
            if len(deployments) > 0:
                deployment_uid = deployments[0]['deployment_id']
            else:
                deployment_uid = 'generic_deployment'

        payload = {
                    "binding_id": self._subscription.binding_uid,
                    "subscription_id": self._subscription.uid,
                    "deployment_id": deployment_uid,
                    "request": request,
                    "response": response
        }

        if scoring_timestamp is not None:
            payload['scoring_timestamp'] = scoring_timestamp
        else:
            payload['scoring_timestamp'] = str(datetime.datetime.utcnow().isoformat()) + 'Z'

        if scoring_id is not None:
            payload['scoring_id'] = scoring_id
        else:
            payload['scoring_id'] = str(uuid.uuid4())

        if response_time is not None:
            payload['response_time'] = str(response_time)

        response = requests_session.post(
            self._ai_client._href_definitions.get_payload_logging_storage_href(),
            json=[payload],
            headers=self._ai_client._get_headers()
        )

        handle_response(202, u'payload logging storage', response)

    def show_table(self, limit=10):
        """
        Show records in payload logging table. By default 10 records will be shown. Maximal number of records is 1000.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.payload_logging.show_table()
        >>> subscription.payload_logging.show_table(limit=20)
        >>> subscription.payload_logging.show_table(limit=None)
        """
        super(PayloadLogging, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show payload logging table schema.
        """
        super(PayloadLogging, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of payload logging table in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas'
        :type format: {str_type}

        :param limit: maximal number of fetched rows (upper limit is 1000). (optional)
        :type limit: int

        A way you might use me is:

        >>> pandas_table_content = subscription.payload_logging.get_table_content()
        >>> table_content = subscription.payload_logging.get_table_content(format='python')
        >>> pandas_table_content = subscription.payload_logging.get_table_content(format='pandas')
        """
        return super(PayloadLogging, self).get_table_content(format=format, limit=limit)

    def describe_table(self):
        """
        Prints description of the content of payload logging table (pandas style). It will remove columns with unhashable values.

        A way you might use me is:

        >>> subscription.payload_logging.describe_table()
        """
        return super(PayloadLogging, self).describe_table()

    def _get_data_from_rest_api(self, limit=None):
        if limit is None:
            limit = 1000

        response = requests_session.get(
            self._ai_client._href_definitions.get_payload_transactions_href(self._subscription.uid) + "&limit={}".format(limit) if limit is not None else "",
            headers=self._ai_client._get_headers()
        )

        response_json = handle_response(200, u'payload logging transactions', response)

        values = (response_json['scoring_payload'] if 'scoring_payload' in response_json else response_json)['values']

        return [self._prepare_row(value, self._get_schema()) for value in values]

    def _get_schema(self):
        response = requests_session.get(
            self._ai_client._href_definitions.get_payload_logging_schema_href(self._subscription.binding_uid,
                                                                              self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'payload logging get table schema', response)['table_schema']

    def _get_table_name(self):
        table_name = self.get_details()['parameters']['table_name']

        return table_name.split('.')[-1]
