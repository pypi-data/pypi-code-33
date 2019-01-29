# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.clients import ClientWithMLGatewaySupport
from ibm_ai_openscale.base_classes import Artifact, SourceDeployment
from .consts import SPSSConsts


class SPSSClient(ClientWithMLGatewaySupport):
    service_type = SPSSConsts.SERVICE_TYPE

    def __init__(self, binding_uid, ai_client, project_id=None):
        ClientWithMLGatewaySupport.__init__(self, ai_client, binding_uid)
        self._ai_client = ai_client
        # TODO workaround since there is no created_at returned by gateway and it is required by API
        self.created_at_time = '0000-01-01T00:00:00.0Z'

    def _make_artifact_from_details(self, details):

        return Artifact(
            source_uid=details['entity']['asset']['asset_id'],
            source_url=details['entity']['asset']['url'],
            binding_uid=self.binding_uid,
            name=details['entity']['name'],
            type='model',
            created=self.created_at_time,
            frameworks=[],
            source_entry=details,
            properties=details['entity']['asset_properties']
        )

    # TODO when created_at will be returned my ml_gateway this function may be removed
    def get_deployments(self, asset=None, deployment_uids=None):

        deployment_details = self._get_deployments_details()

        if asset is None and deployment_uids is None:
            return [
                SourceDeployment(
                    deployment['metadata']['guid'],
                    deployment['metadata']['url'],
                    deployment['entity']['name'],
                    deployment['entity']['type'],
                    deployment['metadata']['created_at'],
                    scoring_endpoint=deployment['entity']['scoring_endpoint'],
                ) for deployment in deployment_details
            ]
        elif asset is not None and deployment_uids is None:
            return [
                SourceDeployment(
                    guid=deployment['metadata']['guid'],
                    url=deployment['metadata']['url'],
                    name=deployment['entity']['name'],
                    deployment_type=deployment['entity']['type'],
                    created=self.created_at_time,
                    scoring_endpoint=deployment['entity']['scoring_endpoint'],
                ) for deployment in deployment_details if deployment['entity']['asset']['asset_id'] == asset.source_uid
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
                ) for deployment in deployment_details if deployment['metadata']['guid'] in deployment_uids
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
                ) for deployment in deployment_details if (deployment['metadata']['guid'] in deployment_uids and deployment['entity']['asset']['asset_id'] == asset.source_uid)
            ]
