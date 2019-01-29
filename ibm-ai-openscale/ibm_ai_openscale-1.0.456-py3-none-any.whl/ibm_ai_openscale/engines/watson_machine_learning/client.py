# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.clients import KnownServiceClient
from ibm_ai_openscale.base_classes.assets import KnownServiceAsset
from ibm_ai_openscale.base_classes import Artifact, SourceDeployment, Framework
from ibm_ai_openscale.base_classes.assets.properties import Properties
from ibm_ai_openscale.utils import validate_type
from .consts import WMLConsts
from ibm_ai_openscale.utils.client_errors import ClientError


class WMLClient(KnownServiceClient):
    service_type = WMLConsts.SERVICE_TYPE

    def __init__(self, binding_uid, service_credentials, project_id=None):
        KnownServiceClient.__init__(self, binding_uid)
        try:
            from watson_machine_learning_client import WatsonMachineLearningAPIClient
        except Exception as e:
            raise ClientError("Error during import of 'watson_machine_learning_client' module.", e)
        self._client = WatsonMachineLearningAPIClient(service_credentials, project_id)

    def _make_artifact_from_details(self, details):
        asset_type = 'function' if 'functions' in details['metadata']['url'] else 'model'

        if asset_type == 'model':
            frameworks = [Framework(details['entity']['model_type'].split('-')[0], details['entity']['model_type'].split('-')[1])]
        else:
            frameworks = []

        return Artifact(
            source_uid=details['metadata']['guid'],
            source_url=details['metadata']['url'],
            binding_uid=self.binding_uid,
            name=details['entity']['name'],
            type=asset_type,
            created=details['metadata']['created_at'],
            frameworks=frameworks,
            source_entry=details,
            properties=self._make_artifact_properties_from_details(details)
        )

    def _make_artifact_properties_from_details(self, details):
        properties = {}
        properties_names = Properties.get_properties_names()
        details_keys = details['entity'].keys()

        for name in properties_names:
            if name in details_keys:
                properties[name] = details['entity'][name]

        return properties

    def get_artifact(self, source_uid):
        asset_details = self._client.repository.get_details(source_uid)
        return self._make_artifact_from_details(asset_details)

    # TODO use evaluation_method from learning_system if available - need to read details from repo
    # def prepare_artifact(self, asset)

    def get_artifacts(self):
        models = self._client.repository.get_model_details()['resources']
        try:
            import logging
            logging.getLogger('watson_machine_learning_client.wml_client_error').disabled = True
            functions = self._client.repository.get_function_details()['resources']
        except:
            functions = []
        finally:
            import logging
            logging.getLogger('watson_machine_learning_client.wml_client_error').disabled = False

        return [self._make_artifact_from_details(asset) for asset in models + functions]

    def get_deployments(self, asset, deployment_uids=None):
        deployments = self._client.deployments.get_details()['resources']
        deployments = list(filter(lambda d: d['entity']['deployable_asset']['guid'] == asset.source_uid, deployments))

        if deployment_uids is not None:
            deployments = list(filter(lambda d: d['metadata']['guid'] in deployment_uids, deployments))

        return [
            SourceDeployment(
                guid=deployment['metadata']['guid'],
                url=deployment['metadata']['url'],
                name=deployment['entity']['name'],
                deployment_type=deployment['entity']['type'],
                created=deployment['metadata']['created_at'],
                scoring_endpoint={'url': deployment['entity']['scoring_url']},
            ) for deployment in deployments
        ]
