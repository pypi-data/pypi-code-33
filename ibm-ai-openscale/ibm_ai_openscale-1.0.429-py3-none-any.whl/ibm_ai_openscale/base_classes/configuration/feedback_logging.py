# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
from ibm_ai_openscale.base_classes.configuration.table_from_rest_api_viewer import TableFromRestApiViewer
from ibm_ai_openscale.engines.watson_machine_learning import WMLConsts


_DEFAULT_LIST_LENGTH = 50


class FeedbackLogging(TableFromRestApiViewer):
    """Manage payload logging for asset."""
    def __init__(self, subscription, ai_client):
        TableFromRestApiViewer.__init__(self, ai_client, subscription, subscription.quality_monitoring)
        self._schema = subscription._ai_client.data_mart.get_details()['database_configuration']['location']['schema']
        self._engine = subscription._ai_client.data_mart.bindings.get_details(subscription.binding_uid)['entity']['service_type']

    def _validate_if_table_accessible(self):
        quality_details = self._subscription.quality_monitoring.get_details()

        if not quality_details['enabled']:
            raise ClientError('Quality monitoring is not enabled. No information about table name.')

        try:
            tablename = quality_details['parameters']['feedback_data_reference']['location']['table_name']
        except:
            raise ClientError('No information about table name. Table cannot be accessed.')

        if not tablename.startswith(self._schema + '.'):
            raise ClientError('Table is outside AIOS schema. It cannot be accessed.')

    def store(self, feedback_data, fields=None):
        """
            Send feedback data to learning system.

            :param feedback_data: rows of feedback data to be send
            :type feedback_data: list of rows
            :param fields: list of fields (optional for Watson Machine Learning)
            :type fields: list of strings

            A way you might use me is

            >>> subscription.feedback_logging.store([["a1", 1, 1.0], ["a2", 2, 3.4]])
            >>> subscription.feedback_logging.store([["a1", 1.0], ["a2", 3.4]], fields=["id", "value"])
        """
        validate_type(feedback_data, "feedback_data", list, True)

        if self._engine == WMLConsts.SERVICE_TYPE:
            validate_type(fields, "fields", list, False)
        else:
            validate_type(fields, "fields", list, True)

        params = {
            "binding_id": self._subscription.binding_uid,
            "subscription_id": self._subscription.uid,
            "fields": fields,
            "values": feedback_data
        }

        response = requests_session.post(
            self._ai_client._href_definitions.get_feedback_logging_storage_href(),
            json=params,
            headers=self._ai_client._get_headers()
        )

        handle_response(204, u'feedback records storing', response, json_response=False)

    def show_table(self, limit=10):
        """
        Show records in feedback logging table. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.feedback_logging.show_table()
        >>> subscription.feedback_logging.show_table(limit=20)
        >>> subscription.feedback_logging.show_table(limit=None)
        """
        self._validate_if_table_accessible()
        super(FeedbackLogging, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show feedback logging table schema.
        """
        self._validate_if_table_accessible()
        super(FeedbackLogging, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of feedback logging table in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas'
        :type format: {str_type}

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> pandas_table_content = subscription.feedback_logging.get_table_content()
        >>> table_content = subscription.feedback_logging.get_table_content(format='python')
        >>> pandas_table_content = subscription.feedback_logging.get_table_content(format='pandas')
        """
        self._validate_if_table_accessible()
        return super(FeedbackLogging, self).get_table_content(format=format, limit=limit)

    def describe_table(self):
        """
        Prints description of the content of feedback logging table (pandas style). It will remove columns with unhashable values.

        A way you might use me is:

        >>> subscription.feedback_logging.describe_table()
        """
        self._validate_if_table_accessible()
        super(FeedbackLogging, self).describe_table()

    def _get_schema(self):
        schema = self._subscription.get_details()['entity']['asset_properties']['training_data_schema']
        schema['fields'].append({
            "name": "_training",
            "type": "timestamp",
            "nullable": False,
            "metadata": {}
        })

        return schema

    def _get_data_from_rest_api(self, limit=None): # Warning - limit here is not used
        response = requests_session.get(
            self._ai_client._href_definitions.get_feedback_transactions_href(
                self._subscription.binding_uid,
                self._subscription.uid
            ),
            headers=self._ai_client._get_headers()
        )

        response_json = handle_response(200, u'feedback logging get transactions', response)
        schema = self._get_schema()

        return [self._prepare_row(row, schema) for row in response_json]
