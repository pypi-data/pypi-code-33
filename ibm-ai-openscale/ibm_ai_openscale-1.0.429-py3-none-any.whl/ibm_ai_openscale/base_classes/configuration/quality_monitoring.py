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


class QualityMonitoring(MetricsViewer):
    """Manage fairness monitoring for asset."""
    def __init__(self, subscription, ai_client):
        MetricsViewer.__init__(self, ai_client, subscription, MetricTypes.QUALITY_MONITORING, 'QualityMetrics')

    def enable(self, threshold, min_records, problem_type=None, evaluation_method=None):
        """
        Enables model quality monitoring. The monitor is being run hourly.

        :param problem_type: type of model (problem) [BINARY_CLASSIFICATION, MULTICLASS_CLASSIFICATION, REGRESSION].
        Required if not part of model's metadata.
        :type problem_type: str

        :param threshold: the threshold for quality metric (accuracy, areaUnderROC or r2).
        :type threshold: float

        :param min_records: minial feedback record count that triggers monitoring
        :type min_records: int

        A way you might use me is:
        >>> from ibm_ai_openscale.supporting_classes.enums import ProblemType
        >>>
        >>> subscription.quality_monitoring.enable(problem_type=ProblemType.MULTICLASS_CLASSIFICATION,
        >>>                                        threshold=0.8,
        >>>                                        min_records=5)
        """

        asset_properties = self._subscription.get_details()['entity']['asset_properties']

        if evaluation_method is not None:
            problem_type = evaluation_method
            print("DeprecationWarning: 'evaluation_method' parameter is deprecated and will be removed in 1.1.0 release; use 'problem_type' instead.")

        if problem_type is None:
            if 'problem_type' in asset_properties.keys():
                problem_type = asset_properties['problem_type']
            else:
                raise MissingValue('Missing required parameter: problem_type.')

        if threshold is None or min_records is None:
            raise MissingValue('Missing one of required parameters: threshold, min_records.')

        params = {
                    "evaluation_definition": {
                        "method": problem_type,
                        "threshold": threshold
                    },
                    "min_feedback_data_size": min_records,
                  }

        response = requests_session.put(
            self._ai_client._href_definitions.get_quality_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": True,
                "parameters": params
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'quality monitoring setup', response)

    def run(self, background_mode=True):
        """
        Run model quality evaluation on demand.

        :param background_mode: if set to True, run will be in asynchronous mode, if set to False it will wait for result
        :type background_mode: bool

        :return: result of run, or run details if in background mode
        :rtype: str
        """

        response = requests_session.post(
            self._ai_client._href_definitions.get_evaluation_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        result = handle_response(202, u'quality evaluation run', response)

        request_id = result['id']

        if background_mode:
            return result

        def check_state():
            details = self.get_run_details(request_id)
            return details['status']

        def get_result():
            details = self.get_run_details(request_id)
            state = details['status']

            if state in ['completed']:
                return "Successfully finished run", None, details
            else:
                return "Run failed with status: {}".format(state), 'Reason: {}'.format(details['error']), None

        return print_synchronous_run(
            'Waiting for end of quality monitoring run {}'.format(request_id),
            check_state,
            get_result=get_result,
            success_states=['completed']
        )

    def get_run_details(self, run_uid=None):
        """
        Returns details of run.

        :param run_id: id of run (it can be taken from `run` function when background_mode == True)
        :type run_id: str

        :return: details of run
        :rtype: str
        """

        if run_uid is not None:
            response = requests_session.get(self._ai_client._href_definitions.get_evaluation_run_details_href(self._subscription.binding_uid, self._subscription.uid, run_uid),
                headers = self._ai_client._get_headers())
        else:
            response = requests_session.get(
                self._ai_client._href_definitions.get_evaluation_href(self._subscription.binding_uid, self._subscription.uid),
                headers=self._ai_client._get_headers())

        return handle_response(200, u'quality evaluation run details', response)

    def get_details(self):
        """
        Returns details of quality monitoring configuration.

        :return: configuration of quality monitoring
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_quality_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, u'quality monitoring configuration', response)

    def disable(self):
        """
        Disables quality monitoring.
        """

        response = requests_session.put(
            self._ai_client._href_definitions.get_quality_monitoring_href(self._subscription.binding_uid, self._subscription.uid),
            json={
                "enabled": False
            },
            headers=self._ai_client._get_headers()
        )

        handle_response(200, u'quality monitoring unset', response)

    def get_deployment_metrics(self, deployment_uid=None):
        """
        Get last quality metrics for deployment(s).

        :param deployment_uid: UID of deployment for which the metrics which be prepared (optional)
        :type deployment_uid: str

        :return: metrics
        :rtype: dict
        """
        return self._subscription.get_deployment_metrics(deployment_uid=deployment_uid, metric_type=MetricTypes.QUALITY_MONITORING)

    def get_metrics(self, deployment_uid):
        """
        Returns quality monitoring metrics.

        :param deployment_uid: deployment uid for which the metrics will be retrieved
        :type deployment_uid: str

        :return: metrics for deployment
        :rtype: dict
        """
        return super(QualityMonitoring, self).get_metrics(deployment_uid)

    def show_table(self, limit=10):
        """
        Show records in quality metrics view. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> subscription.quality_monitoring.show_table()
        >>> subscription.quality_monitoring.show_table(limit=20)
        >>> subscription.quality_monitoring.show_table(limit=None)
        """
        super(QualityMonitoring, self).show_table(limit=limit)

    def print_table_schema(self):
        """
        Show quality metrics view schema.
        """
        super(QualityMonitoring, self).print_table_schema()

    def get_table_content(self, format='pandas', limit=None):
        """
        Get content of quality metrics view in chosen format. By default the format is 'pandas'.

        :param format: format of returned content, may be one of following: ['python', 'pandas'], by default is set 'pandas'
        :type format: {str_type}

        :param limit: maximal number of fetched rows. (optional)
        :type limit: int

        A way you might use me is:

        >>> pandas_table_content = subscription.quality_monitoring.get_table_content()
        >>> table_content = subscription.quality_monitoring.get_table_content(format='python')
        >>> pandas_table_content = subscription.quality_monitoring.get_table_content(format='pandas')
        """
        return super(QualityMonitoring, self).get_table_content(format=format, limit=limit)

    def describe_table(self):
        """
        Prints description of the content of quality monitoring table (pandas style). It will remove columns with unhashable values.

        A way you might use me is:

        >>> subscription.quality_metrics.describe_table()
        """
        super(QualityMonitoring, self).describe_table()

    def _prepare_rows(self, obj, deployment_uid=''):
        return [self._prepare_row([
                obj['timestamp'],
                obj['value']['quality'],
                obj['value']['threshold'],
                self._subscription.binding_uid,
                self._subscription.uid,
                deployment_uid,
                obj['process'] if 'process' in obj else '',
                ''
            ], self._get_schema())]

    def _get_schema(self):
        return {
            'fields': [
                {'name': 'ts', 'type': 'timestamp', 'nullable': False},
                {'name': 'quality', 'type': 'float', 'nullable': False},
                {'name': 'quality_threshold', 'type': 'float', 'nullable': False},
                {'name': 'binding_id', 'type': 'string', 'nullable': False},
                {'name': 'subscription_id', 'type': 'string', 'nullable': False},
                {'name': 'deployment_id', 'type': 'string', 'nullable': True},
                {'name': 'process', 'type': 'string', 'nullable': False},
                {'name': 'asset_revision', 'type': 'string', 'nullable': True}
            ]
        }