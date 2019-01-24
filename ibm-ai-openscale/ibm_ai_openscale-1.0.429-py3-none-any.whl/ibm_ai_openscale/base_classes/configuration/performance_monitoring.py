# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
from ibm_ai_openscale.base_classes.configuration.metrics_viewer import MetricsViewer
from ibm_ai_openscale.supporting_classes.enums import *


_DEFAULT_LIST_LENGTH = 50


class PerformanceMonitoring(MetricsViewer):
    """Manage performance monitoring for asset."""
    def __init__(self, subscription, ai_client):
        MetricsViewer.__init__(self, ai_client, subscription, MetricTypes.PERFORMANCE_MONITORING, "PerformanceMetrics")

    def enable(self, apt_threshold=None, rpm_threshold=None):
        """
        Enables performance monitoring.

        :param apt_threshold: the threshold for average processing time metric (optional)
        :type apt_threshold: float

        :param rpm_threshold: the threshold for records per minute metric (optional)
        :type rpm_threshold: int

        A way you might use me is:

        >>> subscription.performance_monitoring.enable()
        """
        metrics = []

        if apt_threshold is not None:
            metrics.append({'name': 'average_processing_time', 'threshold': apt_threshold})

        if rpm_threshold is not None:
            metrics.append({'name': 'records_per_minute', 'threshold': rpm_threshold})

        if len(metrics) > 0:
            params = {'metrics': metrics}
        else:
            params = {}

        response = requests_session.put(
            self._ai_client._href_definitions.get_performance_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": True,
                "parameters": params
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'fairness monitoring setup', response)

    def get_details(self):
        """
        Returns details of performance monitoring configuration.

        :return: configuration of performance monitoring
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_performance_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'fairness monitoring configuration', response)

    def disable(self):
        """
        Disables performance monitoring.
        """

        response = requests_session.put(
            self._ai_client._href_definitions.get_performance_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'performance monitoring unset', response)

    def get_deployment_metrics(self, deployment_uid=None):
        """
        Get last performance metrics for deployment(s).

        :param deployment_uid: UID of deployment for which the metrics which be prepared (optional)
        :type deployment_uid: str

        :return: metrics
        :rtype: dict
        """
        return self._subscription.get_deployment_metrics(deployment_uid=deployment_uid, metric_type=MetricTypes.PERFORMANCE_MONITORING)

    def get_metrics(self, deployment_uid):
        """
        Returns performance monitoring metrics.

        :param deployment_uid: deployment uid for which the metrics will be retrieved
        :type deployment_uid: str

        :return: metrics for deployment
        :rtype: dict
        """
        return super(PerformanceMonitoring, self).get_metrics(deployment_uid)

    def show_table(self, limit=10):
        """
        Show records in performance metrics view. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.performance_monitoring.show_table()
        >>> subscription.performance_monitoring.show_table(limit=20)
        >>> subscription.performance_monitoring.show_table(limit=None)
        """
        super(PerformanceMonitoring, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show performance metrics view schema.
        """
        super(PerformanceMonitoring, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of performance metrics view in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas'
        :type format: {str_type}

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> pandas_table_content = subscription.performance_monitoring.get_table_content()
        >>> table_content = subscription.performance_monitoring.get_table_content(format='python')
        >>> pandas_table_content = subscription.performance_monitoring.get_table_content(format='pandas')
        """
        return super(PerformanceMonitoring, self).get_table_content(format=format, limit=limit)

    def describe_table(self):
        """
        Prints description of the content of performance monitoring table (pandas style). It will remove columns with unhashable values.

        A way you might use me is:

        >>> subscription.performance_metrics.describe_table()
        """
        super(PerformanceMonitoring, self).describe_table()

    def _prepare_rows(self, obj, deployment_uid=''):
        return [self._prepare_row([
            obj['timestamp'],
            obj['value']['response_time'],
            obj['value']['records'],
            self._subscription.binding_uid,
            self._subscription.uid,
            deployment_uid,
            obj['process'] if 'process' in obj else '',
            obj['asset_revision'] if 'process' in obj else ''
        ], self._get_schema())]

    def _get_schema(self):
        return {
            'fields': [
                {'name': 'ts', 'type': 'timestamp', 'nullable': False},
                {'name': 'scoring_time', 'type': 'float', 'nullable': False},
                {'name': 'scoring_records', 'type': 'object', 'nullable': False},
                {'name': 'binding_id', 'type': 'string', 'nullable': False},
                {'name': 'subscription_id', 'type': 'string', 'nullable': False},
                {'name': 'deployment_id', 'type': 'string', 'nullable': True},
                {'name': 'process', 'type': 'string', 'nullable': False},
                {'name': 'asset_revision', 'type': 'string', 'nullable': True},
            ]
        }
