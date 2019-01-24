# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.configuration.metrics_viewer import MetricsViewer
from ibm_ai_openscale.supporting_classes import *
from ibm_ai_openscale.engines.watson_machine_learning import WMLConsts


_DEFAULT_LIST_LENGTH = 50


class FairnessMonitoring(MetricsViewer):
    """Manage fairness monitoring for asset."""
    def __init__(self, subscription, ai_client):
        MetricsViewer.__init__(self, ai_client, subscription, MetricTypes.FAIRNESS_MONITORING, "FairnessMetrics")
        self._engine = subscription._ai_client.data_mart.bindings.get_details(subscription.binding_uid)['entity']['service_type']

    def enable(self, features, deployment_uid=None, prediction_column=None, favourable_classes=None, unfavourable_classes=None, min_records=None, training_data_statistics=None):
        """
        Enables fairness monitoring.

        :param features: the features for fairness monitoring. Feature is represented by `Feature` class object. More details can be found in `supporting_classes.Feature` section.
        :type features: list of Feature class objects

        :param prediction_column: the name of column/field with predicted values (optional)
        :type prediction_column: str

        :param favourable_classes: list of favourable classes (optional)
        :type favourable_classes: list of str

        :param unfavourable_classes: list of unfavourable classes (optional)
        :type unfavourable_classes: list of str

        :param min_records: minimal number of records (optional)
        :type min_records: int

        :param training_data_statistics: dictionary with training data characteristics (optional)
        :type training_data_statistics: dict


        A way you might use me is:
        >>> from ibm_ai_openscale.supporting_classes.feature import Feature
        >>>
        >>> subscription.fairness_monitoring.enable(
        >>>    features=[
        >>>        Feature("AGE", majority=[[20,50],[60,70]], minority=[[51,59]], threshold=0.8)],
        >>>    prediction_column='predictedLabel',
        >>>    favourable_classes=['drugY'],
        >>>    unfavourable_classes=['drugA', 'drugB', 'drugC'],
        >>>    min_records=12)
        """

        validate_type(features, 'features', list, True)

        for feature in features:
            validate_type(feature, 'feature', Feature, True)

        validate_type(prediction_column, 'prediction_column', str, False)
        validate_type(favourable_classes, 'favourable_classes', [str, list], False)
        validate_type(unfavourable_classes, 'unfavourable_classes', [str, list], False)
        validate_type(min_records, 'min_records', int, False)
        validate_type(training_data_statistics, 'training_data_statistics', dict, False)

        if deployment_uid is None:
            uids = self._subscription.get_deployment_uids()
            if len(uids) == 0:
                raise ClientError('No deployments existing for subscription.')
            elif len(uids) > 1:
                raise ClientError('More than one deployments existing for subscription: {}'.format(uids))

            deployment_uid = uids[0]

        payload_logging_details = self._subscription.payload_logging.get_details()

        if not payload_logging_details['enabled']:
            self._subscription.payload_logging.enable()

        params = {
            "features": [feature._to_json() for feature in features]
        }

        if prediction_column is not None:
            params["class_label"] = prediction_column

        if favourable_classes is not None:
            params["favourable_class"] = favourable_classes

        if unfavourable_classes is not None:
            params["unfavourable_class"] = unfavourable_classes

        if min_records is not None:
            params["min_records"] = min_records

        payload = {
                "data_mart_id": self._ai_client._service_credentials['data_mart_id'],
                "asset_id": self._subscription.uid,
                "deployment_id": deployment_uid,
                "parameters": params,
        }

        if training_data_statistics is not None:
            if "fairness_configuration" in training_data_statistics.keys():
                payload["distributions"] = training_data_statistics["fairness_configuration"]["distributions"]

        response = requests_session.post(
            self._ai_client._href_definitions.get_fairness_monitoring_configuration_href(),
            json=payload,
            headers=self._ai_client._get_headers()
        )

        handle_response(202, u'fairness monitoring setup', response)

    def get_details(self):
        """
        Returns details of fairness monitoring configuration.

        :return: configuration of fairness monitoring
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_fairness_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'fairness monitoring configuration', response)

    def disable(self):
        """
        Disables fairness monitoring.
        """

        response = requests_session.put(
            self._ai_client._href_definitions.get_fairness_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'fairness monitoring unset', response)

    def get_deployment_metrics(self, deployment_uid=None):
        """
        Get last fairness metrics for deployment(s).

        :param deployment_uid: UID of deployment for which the metrics which be prepared (optional)
        :type deployment_uid: str

        :return: metrics
        :rtype: dict
        """
        return self._subscription.get_deployment_metrics(deployment_uid=deployment_uid, metric_type=MetricTypes.FAIRNESS_MONITORING)

    def run(self, deployment_uid=None):
        if deployment_uid is None:
            uids = self._subscription.get_deployment_uids()
            if len(uids) == 0:
                raise ClientError('No deployments existing for subscription.')
            elif len(uids) > 1:
                raise ClientError('More than one deployments existing for subscription: {}'.format(uids))

            deployment_uid = uids[0]

        response = requests_session.post(
            self._ai_client._href_definitions.get_fairness_monitoring_runs_href(self._subscription.uid),
            json={
                "data_mart_id": self._ai_client._service_credentials['data_mart_id'],
                "deployment_id": deployment_uid,
                "subscription_id": self._subscription.uid
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(202, u'fairness monitoring run', response)

    def get_metrics(self, deployment_uid):
        """
        Returns fairness monitoring metrics.

        :param deployment_uid: deployment uid for which the metrics will be retrieved
        :type deployment_uid: str

        :return: metrics for deployment
        :rtype: dict
        """
        return super(FairnessMonitoring, self).get_metrics(deployment_uid)

    def show_table(self, limit=10):
        """
        Show records in fairness metrics view. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.fairness_monitoring.show_table()
        >>> subscription.fairness_monitoring.show_table(limit=20)
        >>> subscription.fairness_monitoring.show_table(limit=None)
        """
        super(FairnessMonitoring, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show fairness metrics view schema.
        """
        super(FairnessMonitoring, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of fairness metrics view in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas'
        :type format: {str_type}

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> pandas_table_content = subscription.fairness_monitoring.get_table_content()
        >>> table_content = subscription.fairness_monitoring.get_table_content(format='python')
        >>> pandas_table_content = subscription.fairness_monitoring.get_table_content(format='pandas')
        """
        return super(FairnessMonitoring, self).get_table_content(format=format, limit=limit)

    def describe_table(self):
        """
        Prints description of the content of fairness monitoring table (pandas style). It will remove columns with unhashable values.

        A way you might use me is:

        >>> subscription.fairness_metrics.describe_table()
        """
        super(FairnessMonitoring, self).describe_table()

    def _prepare_rows(self, obj, deployment_uid=''):
        schema = self._get_schema()

        return [self._prepare_row([
                    obj['timestamp'],
                    metrics['feature'],
                    value['value'],
                    value['is_biased'],
                    value['fairness_value'],
                    value['fav_class_percent'],
                    self._subscription.binding_uid,
                    self._subscription.uid,
                    obj['asset_revision'],
                    deployment_uid,
                    ''
                ], schema) for metrics in obj['value']['metrics'] for value in metrics['minority']['values']]

    def _get_schema(self):
        return {
            'fields': [
                {'name': 'ts', 'type': 'timestamp', 'nullable': False},
                {'name': 'feature', 'type': 'string', 'nullable': False},
                {'name': 'feature_value', 'type': 'object', 'nullable': False},
                {'name': 'fairness_biased', 'type': 'boolean', 'nullable': False},
                {'name': 'fairness_value', 'type': 'int', 'nullable': False},
                {'name': 'fairness_fav_class', 'type': 'int', 'nullable': False},
                {'name': 'binding_id', 'type': 'string', 'nullable': False},
                {'name': 'subscription_id', 'type': 'string', 'nullable': False},
                {'name': 'asset_revision', 'type': 'string', 'nullable': True},
                {'name': 'deployment_id', 'type': 'string', 'nullable': True},
                {'name': 'process', 'type': 'string', 'nullable': False}
            ]
        }