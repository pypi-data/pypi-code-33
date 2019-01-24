# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.clients import Client
from ibm_ai_openscale.base_classes.configuration import *
from ibm_ai_openscale.base_classes import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType
from ibm_ai_openscale.supporting_classes.storage_reference import StorageReference


class Subscription:
    """
    Describes subscription in AI OpenScale

    :var uid: uid of subscription
    :vartype uid: str
    :var url: url of subscription
    :vartype url: str
    :var source_uid: uid of asset
    :vartype source_uid: str
    :var source_url: url of asset
    :vartype source_url: str
    :var binding_uid: uid of binding containing this subscription
    :vartype binding_uid: str
    :var payload_logging: object managing payload logging for this subscription
    :vartype payload_logging: PayloadLogging
    :var fairness_monitoring: object managing fairness monitoring for this subscription
    :vartype fairness_monitoring: FairnessMonitoring
    :var performance_monitoring: object managing performance monitoring for this subscription
    :vartype performance_monitoring: PerformanceMonitoring
    :var quality_monitoring: object managing quality monitoring for this subscription
    :vartype quality_monitoring: QualityMonitoring
    :var feedback_logging: object managing feedback logging for this subscription
    :vartype feedback_monitoring: FeedbackLogging
    :var explainability: object managing explainability for this subscription
    :vartype explainability: Explainability
    """

    def __init__(self, uid, url, source_uid, source_url, client, ai_client):
        validate_type(uid, "uid", str, True)
        validate_type(source_uid, "source_uid", str, True)
        validate_type(client, "client", Client, True, subclass=True)

        self.uid = uid
        self.url = url
        self.source_uid = source_uid
        self.source_url = source_url
        self.binding_uid = client.binding_uid

        from ibm_ai_openscale.engines.watson_machine_learning.client import WMLClient

        if type(client) is WMLClient:
            self._engine_client = client._client
        else:
            self._engine_client = None

        self._service_type = client.service_type
        self._ai_client = ai_client
        self._binding_client = client
        self.payload_logging = PayloadLogging(self, ai_client)
        self.fairness_monitoring = FairnessMonitoring(self, ai_client)
        self.explainability = Explainability(self, ai_client)
        self.performance_monitoring = PerformanceMonitoring(self, ai_client)
        self.quality_monitoring = QualityMonitoring(self, ai_client)
        self.feedback_logging = FeedbackLogging(self, ai_client)

    def get_details(self):
        """
        Get subscription details.

        :return: subscription details
        :rtype: dict
        """
        response = requests_session.get(
            self._ai_client._href_definitions.get_subscription_href(self.binding_uid, self.uid),
            headers=self._ai_client._get_headers()
        )

        return handle_response(200, 'getting subscription details', response, True)

    def get_deployment_uids(self):
        """
        Get deployment uids for this subscription.

        :return: deployment uids
        :rtype: list of str
        """
        deployments_details = self.get_details()['entity']['deployments']
        return [d['deployment_id'] for d in deployments_details]

    def list_deployments(self):
        """
        List deployment for this subscription.
        """
        deployments_details = self.get_details()['entity']['deployments']

        records = [[c['deployment_id'], c['name'], c['created_at'], c['deployment_type']] for c in deployments_details]
        table = Table(['uid', 'name', 'created', 'type'], records)
        table.list(title="Deployments for subscription with uid='{}'".format(self.uid))

    def get_deployment_metrics(self, deployment_uid=None, metric_type=None):
        """
        Get subscription last metrics for deployments.

        :param deployment_uid: UID of deployment for which the metrics which be prepared (optional)
        :type deployment_uid: str

        :param metric_type: metric type which should be returned (optional)
        :type metric_type: str

        :return: subscription metrics
        :rtype: dict
        """
        return self._ai_client.data_mart.get_deployment_metrics(subscription_uid=self.uid, deployment_uid=deployment_uid,
                                                                metric_type=metric_type)

    def update(self, add_all_deployments=True, deployment_uids=None, problem_type=None, input_data_type=None,
               training_data_reference=None, label_column=None, prediction_column=None, probability_column=None,
               training_data_statistics=None, feature_columns=None, categorical_columns = None,
               _training_data_schema=None, _input_data_schema=None, _output_data_schema=None):
        """
        Refresh deployments for this subscription. If deployment_uids list will be passed, the missing uids on the list will be removed from deployment monitoring.

        :param add_all_deployments: if set to True all deployments will be added
        :type add_all_deployments: bool

        :param deployment_uids: list of deployment uids to add (optional)
        :type deployment_uids: list of str

        :param problem_type: type of the problem
        :type problem_type: ProblemType/str

        :param input_data_type: input data type
        :type input_data_type: InputDataType/str

        :param training_data_reference: training data reference
        :type training_data_reference: StorageReference

        :param label_column: label column
        :type label_column: str

        :param prediction_column: prediction column
        :type prediction_column: str

        :param probability_column: probability column
        :type probability_column: str

        :param training_data_statistics: statistics which are generated using training_statistics notebook
        :type training_data_statistics: dict

        :param feature_columns: list of feature columns
        :type feature_columns: list

        :param categorical_columns: list of categorical columns
        :type categorical_columns: list
        """

        artifact = self._binding_client.get_artifact(self.source_uid)

        if deployment_uids is not None or add_all_deployments:
            deployments = self._binding_client.get_deployments(artifact, deployment_uids)

            current_deployment_uids = self.get_deployment_uids()

            for deployment in deployments:
                if deployment.guid not in current_deployment_uids:
                    response = requests_session.put(
                        self._ai_client._href_definitions.get_deployment_href(self.binding_uid, self.uid, deployment.guid),
                        json=deployment._to_json(),
                        headers=self._ai_client._get_headers()
                    )

                    handle_response(200, 'adding deployment monitoring', response)
                    print('Monitoring of deployment with uid={} successfully added.'.format(deployment.guid))
                else:
                    current_deployment_uids.remove(deployment.guid)

            for uid in current_deployment_uids:
                response = requests_session.delete(
                    self._ai_client._href_definitions.get_deployment_href(self.binding_uid, self.uid, uid),
                    headers=self._ai_client._get_headers()
                )

                handle_response(200, 'removing deployment monitoring', response)
                print('Monitoring of deployment with uid={} successfully removed.'.format(uid))

        patch_payload = []

        # TODO what if exists?

        # problem_type

        if problem_type is not None:
            validate_enum(problem_type, 'problem_type', ProblemType, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/problem_type",
                "value": problem_type
            })

        # input_data_type

        if input_data_type is not None:
            validate_enum(input_data_type, 'input_data_type', InputDataType, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/input_data_type",
                "value": input_data_type
            })

        # training_data_reference

        if training_data_reference is not None:
            validate_type(training_data_reference, 'training_data_reference', StorageReference, True, subclass=True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/training_data_reference",
                "value": training_data_reference._get_explainability_payload()
            })

        # label_column

        if label_column is not None:
            validate_type(label_column, 'label_column', str, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/label_column",
                "value": label_column
            })

        # predicted_target_field

        if prediction_column is not None:
            if not self._service_type == "amazon_sagemaker": # TODO should be for all cases `predicted_target_field`
                validate_type(prediction_column, 'prediction_column', str, True)
                patch_payload.append({
                    "op": "add",
                    "path": "/asset_properties/predicted_target_field",
                    "value": prediction_column
                })
            else:
                validate_type(prediction_column, 'prediction_column', str, True)
                patch_payload.append({
                    "op": "add",
                    "path": "/asset_properties/prediction_field",
                    "value": prediction_column
                })

        # probability_column

        if probability_column is not None:
            validate_type(probability_column, 'probability_column', str, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/prediction_probability_field",
                "value": probability_column
            })

        # training_data_statistics

        if training_data_statistics is not None:
            validate_type(training_data_statistics, 'training_data_statistics', dict, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/training_statistics",
                "value": training_data_statistics
            })

        # feature_columns

        if feature_columns is not None:
            validate_type(feature_columns, 'feature_columns', list, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/feature_fields",
                "value": feature_columns
            })

        # categorical_columns

        if categorical_columns is not None:
            validate_type(categorical_columns, 'categorical_columns', list, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/categorical_fields",
                "value": categorical_columns
            })

        # training_data_schema

        if _training_data_schema is not None:
            validate_type(_training_data_schema, '_training_data_schema', dict, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/training_data_schema",
                "value": _training_data_schema
            })

        # input_data_schema

        if _input_data_schema is not None:
            validate_type(_input_data_schema, '_input_data_schema', dict, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/input_data_schema",
                "value": _input_data_schema
            })

        # output_data_schema

        if _output_data_schema is not None:
            validate_type(_output_data_schema, '_output_data_schema', dict, True)
            patch_payload.append({
                "op": "add",
                "path": "/asset_properties/output_data_schema",
                "value": _output_data_schema
            })

        if len(patch_payload) != 0:
            response = requests_session.patch(
                self._ai_client._href_definitions.get_subscription_href(
                    self.binding_uid,
                    self.uid
                ),
                json=patch_payload,
                headers=self._ai_client._get_headers()
            )

            handle_response(200, "update asset", response)
