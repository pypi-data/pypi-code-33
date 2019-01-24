# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.clients import KnownServiceClient, Client
from ibm_ai_openscale.base_classes import Artifact, SourceDeployment
from ibm_ai_openscale.base_classes.assets import KnownServiceAsset
from ibm_ai_openscale.utils import *
from ibm_ai_openscale.utils.client_errors import *
from .consts import SageMakerConsts


class SageMakerClient(KnownServiceClient):
    service_type = SageMakerConsts.SERVICE_TYPE

    def __init__(self, binding_uid, ai_client, project_id=None):
        Client.__init__(self, binding_uid)
        self._ai_client = ai_client
        self._deployment_details = self._get_deployments_details()

    def _make_artifact_from_details(self, details):

        return Artifact(
            details['entity']['asset']['asset_id'],
            details['entity']['asset']['url'],
            self.binding_uid,
            details['entity']['asset']['name'],
            details['entity']['asset']['asset_type'],
            details['entity']['asset']['created_at'],
            [],
            details,
            details['entity']['asset_properties'],
            details['entity']['asset']['asset_rn'],
        )

    def get_artifact(self, source_uid):
        asset_details = None

        for detail in self._deployment_details:
            if detail['entity']['asset']['asset_id'] == source_uid:
                asset_details = detail

        if asset_details is not None:
            return self._make_artifact_from_details(asset_details)
        else:
            raise IncorrectValue(source_uid)

    def get_artifacts(self):
        unique_models = []
        unique_source_uids = set()

        for model in self._deployment_details:
            model_uid = model['entity']['asset']['asset_id']
            if model_uid not in unique_source_uids:
                unique_models.append(model)
            unique_source_uids.add(model_uid)

        return [self._make_artifact_from_details(asset) for asset in unique_models]

    def _get_deployments_details(self):

        response = requests_session.get(self._ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=self.binding_uid),
                                headers=self._ai_client._get_headers())

        deployments_details = handle_response(200, 'get deployments', response, True)

        return deployments_details['resources']

    def get_deployments(self, asset=None, deployment_uids=None):

        if asset is None and deployment_uids is None:
            return [
                SourceDeployment(
                    deployment['metadata']['guid'],
                    deployment['metadata']['url'],
                    deployment['entity']['name'],
                    deployment['entity']['type'],
                    deployment['metadata']['created_at'],
                    scoring_endpoint=deployment['entity']['scoring_endpoint'],
                    rn=deployment['entity']['deployment_rn']
                ) for deployment in self._deployment_details
            ]
        elif asset is not None and deployment_uids is None:
            return [
                SourceDeployment(
                    deployment['metadata']['guid'],
                    deployment['metadata']['url'],
                    deployment['entity']['name'],
                    deployment['entity']['type'],
                    deployment['metadata']['created_at'],
                    scoring_endpoint=deployment['entity']['scoring_endpoint'],
                    rn=deployment['entity']['deployment_rn']
                ) for deployment in self._deployment_details if deployment['entity']['asset']['asset_id'] == asset.source_uid
            ]
        elif asset is None and deployment_uids is not None:
            return [
                SourceDeployment(
                    deployment['metadata']['guid'],
                    deployment['metadata']['url'],
                    deployment['entity']['name'],
                    deployment['entity']['type'],
                    deployment['metadata']['created_at'],
                    scoring_endpoint=deployment['entity']['scoring_endpoint'],
                    rn=deployment['entity']['deployment_rn']
                ) for deployment in self._deployment_details if deployment['metadata']['guid'] in deployment_uids
            ]
        else:
            return [
                SourceDeployment(
                    deployment['metadata']['guid'],
                    deployment['metadata']['url'],
                    deployment['entity']['name'],
                    deployment['entity']['type'],
                    deployment['metadata']['created_at'],
                    scoring_endpoint=deployment['entity']['scoring_endpoint'],
                    rn=deployment['metadata']['rn']
                ) for deployment in self._deployment_details if (deployment['metadata']['guid'] in deployment_uids and deployment['entity']['asset']['asset_id'] == asset.source_uid)
            ]
