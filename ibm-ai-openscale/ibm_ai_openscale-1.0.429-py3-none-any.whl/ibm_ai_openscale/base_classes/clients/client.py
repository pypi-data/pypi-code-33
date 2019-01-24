# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
from ibm_ai_openscale.base_classes.assets.asset import Asset


class Client:
    service_type = None

    def __init__(self, binding_uid):
        validate_type(binding_uid, "binding_uid", str, True)
        self.binding_uid = binding_uid

    def get_artifact(self, source_uid):
        raise NotImplemented()

    def get_artifacts(self):
        raise NotImplemented()

    def get_deployments(self, asset, deployment_uids=None):
        raise NotImplemented()

    def get_subscription(self, uid, url, source_uid, source_url, ai_client):
        from ibm_ai_openscale.base_classes.subscriptions import Subscription
        return Subscription(uid, url, source_uid, source_url, self, ai_client)

    def contains_source_uid(self, uid):
        validate_type(uid, "uid", str, True)

        uids = [x.source_uid for x in self.get_artifacts()]
        return uid in uids

    def prepare_artifact(self, asset):
        validate_type(asset, 'Asset', Asset, True)
        artifact = self.get_artifact(source_uid=asset.source_uid)

        if asset.input_data_type is not None:
            artifact.properties['input_data_type'] = asset.input_data_type

        if asset.problem_type is not None:
            artifact.properties['problem_type'] = asset.problem_type

        if asset.training_data_reference is not None:
            artifact.properties['training_data_reference'] = asset.training_data_reference

        if asset.label_column is not None:
            artifact.properties['label_column'] = asset.label_column

        if asset.prediction_column is not None:
            artifact.properties['predicted_target_field'] = asset.prediction_column

        if asset.probability_column is not None:
            artifact.properties['prediction_probability_field'] = asset.probability_column

        if asset.training_data_statistics is not None:
            artifact.properties['training_statistics'] = asset.training_data_statistics

        if asset.feature_columns is not None:
            artifact.properties['feature_fields'] = asset.feature_columns

        if asset.categorical_columns is not None:
            artifact.properties['categorical_fields'] = asset.categorical_columns

        return artifact