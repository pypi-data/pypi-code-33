# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.supporting_classes import *
from ibm_ai_openscale.engines.watson_machine_learning.consts import WMLConsts
from ibm_ai_openscale.base_classes.configuration.table_from_rest_api_viewer import TableFromRestApiViewer
from ibm_ai_openscale.supporting_classes.enums import *


_DEFAULT_LIST_LENGTH = 50


class Explainability(TableFromRestApiViewer):
    """Manage explainability for asset."""
    def __init__(self, subscription, ai_client):
        TableFromRestApiViewer.__init__(self, ai_client, subscription, self, 'Explanations')
        self._ai_client = ai_client
        self._subscription = subscription
        self._engine = subscription._ai_client.data_mart.bindings.get_details(subscription.binding_uid)['entity']['service_type']

    def enable(self, feature_columns=None, categorical_columns=None, label_column=None, problem_type=None, input_data_type=None, training_data_reference=None, training_data_statistics=None):
        """
        Enables explainability.

        :param problem_type: model (problem) type (required if not part of model's metadata)
        :type problem_type: str

        :param input_data_type: model input data type (required if not part of model's metadata)
        :type input_data_type: str

        :param label_column: the column/field name containing target/label values (required if not part of model's metadata)
        :type label_column: str

        :param feature_columns: feature columns (optional)
        :type feature_columns: list of str

        :param categorical_columns: categorical columns (optional)
        :type categorical_columns: list of str

        :param training_data_reference: training data reference (optional)
        :type training_data_reference: BluemixCloudObjectStorageReference

        :param training_data_statistics: dictionary with training data characteristics (optional)
        :type training_data_statistics: dict

        A way you might use me is:

        >>> from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType
        >>>
        >>> subscription.explainability.enable(
        >>>            problem_type=ProblemType.MULTICLASS_CLASSIFICATION,
        >>>            input_data_type=InputDataType.STRUCTURED,
        >>>            feature_columns=["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION"],
        >>>            label_column='label',
        >>>            training_data_reference={},
        >>>            categorical_columns=["GENDER", "MARITAL_STATUS", "PROFESSION"])
        """

        subscription_details = self._subscription.get_details()
        asset_properties = subscription_details['entity']['asset_properties']

        from ibm_ai_openscale.engines.azure_machine_learning.consts import AzureConsts

        if self._subscription._service_type == AzureConsts.SERVICE_TYPE: # TODO
            output_data_schema = asset_properties['output_data_schema']
            if 'Scored Probabilities' not in output_data_schema:
                output_data_schema['fields'].append({
                    "name": "Scored Probabilities",
                    "type": {
                        "type": "array",
                        "elementType": "double",
                        "containsNull": False
                    },
                    "nullable": False,
                    "metadata": {
                        "modeling_role": "probability"
                    }
                })
        else:
            output_data_schema = None

        self._subscription.update(
            feature_columns=feature_columns,
            categorical_columns=categorical_columns,
            label_column=label_column,
            problem_type=problem_type,
            input_data_type=input_data_type,
            training_data_reference=training_data_reference,
            _output_data_schema=output_data_schema
        )

        subscription_details = self._subscription.get_details()
        asset_properties = subscription_details['entity']['asset_properties']

        payload_logging_details = self._subscription.payload_logging.get_details()

        if not payload_logging_details['enabled']:
            self._subscription.payload_logging.enable()

        params = {}

        if training_data_statistics is None and 'training_statistics' in asset_properties:
            training_data_statistics = asset_properties['training_statistics']

        if training_data_statistics is not None:
            validate_meta_prop(training_data_statistics, 'explainability_configuration', dict, True)
            params['training_statistics'] = training_data_statistics["explainability_configuration"]

        if training_data_reference is None and 'training_data_reference' in asset_properties:
            training_data_reference = asset_properties['training_data_reference']

        if training_data_reference is None and training_data_statistics is None:
            raise MissingMetaProp('training_data_reference or training_data_statistics')

        response = requests_session.post(
            self._ai_client._href_definitions.get_model_explanation_configurations_href(),
            json={
                "data_mart_id": self._ai_client._service_credentials['data_mart_id'],
                "service_binding_id": self._subscription.binding_uid,
                "model_id": self._subscription.source_uid,
                "enabled": True,
                "parameters": params
                },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'explainability setup', response)

    def get_details(self):
        """
        Will return details of explainability. Info about configuration.

        :return: configuration of explainability
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_explainability_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'explainability get details', response)

    def disable(self):
        """
        Disables explainability.
        """

        response = requests_session.put(
            self._ai_client._href_definitions.get_explainability_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'explainability unset', response)

    def get_run_details(self, run_uid):
        """
        Returns details of run.

        :param run_id: id of run (it can be taken from `run` function when background_mode == True)
        :type run_id: str

        :return: details of run
        :rtype: str
        """
        validate_type(run_uid, "run_uid", str, True)

        response = requests_session.get(
            self._ai_client._href_definitions.get_model_explanation_href(run_uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'explainability get details', response, True)

    def run(self, transaction_id, background_mode=False):
        """
        Runs explainability.

        :param transaction_id: id of transaction used for scoring
        :type transaction_id: str

        :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result
        :type background_mode: bool

        :return: result of run, or run details if in background mode
        :rtype: str
        """

        headers = self._ai_client._get_headers()

        response = requests_session.post(
            self._ai_client._href_definitions.get_model_explanations_href(),
            json={
                "transaction_id": transaction_id,
                "data_mart_id": self._ai_client._service_credentials['data_mart_id']
            },
            headers=headers
        )

        result = handle_response(200, u'explainability run', response, True)

        request_id = result['metadata']['request_id']

        if background_mode:
            return result

        def check_state():
            details = self.get_run_details(request_id)
            return details['entity']['status']

        def get_result():
            details = self.get_run_details(request_id)
            state = details['entity']['status']

            if state in ['success', 'finished']:
                return "Successfully finished run", None, details
            else:
                return "Run failed with status: {}".format(state), 'Reason: {}'.format(details['entity']['error']['error_msg']), None

        return print_synchronous_run(
            'Looking for explanation for {}'.format(transaction_id),
            check_state,
            get_result=get_result,
            run_states=['in_progress']
        )

    def show_table(self, limit=10):
        """
        Show records in explainability view. By default 10 records will be shown. Maximal number of records is 1000.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.explainability.show_table()
        >>> subscription.explainability.show_table(limit=20)
        >>> subscription.explainability.show_table(limit=None)
        """
        super(Explainability, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show explainability view schema.
        """
        super(Explainability, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of explainability view in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas'
        :type format: {str_type}

        :param limit: maximal number of fetched rows (upper limit is 1000). (optional)
        :type limit: int

        A way you might use me is:

        >>> pandas_table_content = subscription.explainability.get_table_content()
        >>> table_content = subscription.explainability.get_table_content(format='python')
        >>> pandas_table_content = subscription.explainability.get_table_content(format='pandas')
        """
        return super(Explainability, self).get_table_content(format=format, limit=limit)

    def describe_table(self):
        """
        Prints description of the content of explainability table (pandas style). It will remove columns with unhashable values.

        A way you might use me is:

        >>> subscription.explainability.describe_table()
        """
        super(Explainability, self).describe_table()

    def _prepare_row(self, row, schema):
        return [
            row['request_id'],
            row['scoring_id'], # transaction_id
            row['explanation']['entity']['asset']['id'],
            row['explanation']['entity']['asset']['type'],
            row['deployment_id'],
            row['subscription_id'],
            row['binding_id'],
            row['explanation'] if 'explanation' in row else None,
            row['error'] if 'error' in row else None,
            row['explanation']['entity']['status'],
            row['created_by'],
            row['created_at']
        ]

    def _get_data_from_rest_api(self, limit=None):
        if limit is None:
            limit = 1000

        response = requests_session.get(
            self._ai_client._href_definitions.get_explainability_storing_href() + "?limit={}".format(limit) if limit is not None else "",
            headers=self._ai_client._get_headers()
        )

        response_json = handle_response(200, u'getting stored explainability records', response)

        schema = self._get_schema()
        return [self._prepare_row(x, schema) for x in response_json['explanations']]

    def _get_schema(self):
        return {
            'fields': [
                {'name': 'request_id', 'type': 'string', 'nullable': False},
                {'name': 'transaction_id', 'type': 'string', 'nullable': False},
                {'name': 'asset_id', 'type': 'string', 'nullable': False},
                {'name': 'asset_type', 'type': 'string', 'nullable': False},
                {'name': 'deployment_id', 'type': 'string', 'nullable': False},
                {'name': 'subscription_id', 'type': 'string', 'nullable': False},
                {'name': 'service_binding_id', 'type': 'string', 'nullable': False},
                {'name': 'explanation', 'type': 'json', 'nullable': False},
                {'name': 'error', 'type': 'json', 'nullable': False},
                {'name': 'status', 'type': 'string', 'nullable': False},
                {'name': 'created_by', 'type': 'timestamp', 'nullable': False},
                {'name': 'created_at', 'type': 'timestamp', 'nullable': False}
            ]
        }
