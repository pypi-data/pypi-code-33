# coding=utf-8
from watson_machine_learning_client import WatsonMachineLearningAPIClient

import logging
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict

logger = logging.getLogger(__name__)

class WatsonMachineLearningEngine:

    def __init__(self, credentials, target_env, model):
        self._target_env = target_env
        self._client = WatsonMachineLearningAPIClient(dict(credentials))
        self._engine_name = 'watson_machine_learning'
        self._model_metadata = model.metadata
        logger.info('Using Watson Machine Learning Python Client version: {}'.format(self._client.version))

    def _create_pipeline(self, model_name, pipeline_metadata_file):
        logger.info('Creating pipeline for model: {}'.format(self._model_metadata['model_name']))
        pipeline_metadata = jsonFileToDict(pipeline_metadata_file)
        pipeline_props = {
            self._client.repository.DefinitionMetaNames.AUTHOR_NAME: pipeline_metadata['author']['name'],
            self._client.repository.DefinitionMetaNames.NAME: pipeline_metadata['name'],
            self._client.repository.DefinitionMetaNames.FRAMEWORK_NAME: pipeline_metadata['framework']['name'],
            self._client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: pipeline_metadata['framework']['version'],
            self._client.repository.DefinitionMetaNames.RUNTIME_NAME: pipeline_metadata['framework']['runtimes'][0]['name'],
            self._client.repository.DefinitionMetaNames.RUNTIME_VERSION: pipeline_metadata['framework']['runtimes'][0]['version'],
            self._client.repository.DefinitionMetaNames.DESCRIPTION: pipeline_metadata['description'],
            self._client.repository.DefinitionMetaNames.TRAINING_DATA_REFERENCES: pipeline_metadata['training_data_reference']
        }
        self._client.repository.store_definition(self._model_metadata['pipeline_file'], meta_props=pipeline_props)

    def _delete_models(self, model_name):
        logger.info('Checking for models with the name: {}'.format(model_name))
        models = self._client.repository.get_model_details()
        found_model = False
        for model in models['resources']:
            model_guid = model['metadata']['guid']
            if model_name == model['entity']['name']:
                try:
                    found_model = True
                    logger.info('Deleting model: {}'.format(model_name))
                    self._client.repository.delete(model_guid)
                except:
                    logger.warning('Error deleting WML deployment: %s', model_guid)
        if not found_model:
            logger.info('No existing model found with name: {}'.format(model_name))

    def _create_model(self, model_name, model_metadata_file):
        logger.info('Creating new model: {}'.format(model_name))
        metadata = jsonFileToDict(model_metadata_file)
        model_props = {
            self._client.repository.ModelMetaNames.NAME: model_name,
            self._client.repository.ModelMetaNames.FRAMEWORK_NAME: metadata['framework']['name'],
            self._client.repository.ModelMetaNames.FRAMEWORK_VERSION: metadata['framework']['version'],
            self._client.repository.ModelMetaNames.RUNTIME_NAME: metadata['framework']['runtimes'][0]['name'],
            self._client.repository.ModelMetaNames.RUNTIME_VERSION: metadata['framework']['runtimes'][0]['version'],
            self._client.repository.ModelMetaNames.LABEL_FIELD: metadata['label_column'],
            self._client.repository.ModelMetaNames.TRAINING_DATA_SCHEMA: metadata['training_data_schema'],
            self._client.repository.ModelMetaNames.INPUT_DATA_SCHEMA: metadata['input_data_schema']
        }
        if 'evaluation' in metadata:
            model_props[self._client.repository.ModelMetaNames.EVALUATION_METHOD] = metadata['evaluation']['method']
            model_props[self._client.repository.ModelMetaNames.EVALUATION_METRICS] = metadata['evaluation']['metrics']
        if 'output_data_schema' in metadata:
            model_props[self._client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA] = metadata['output_data_schema']
        if 'training_data_reference' in metadata:
            model_props[self._client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE] = metadata['training_data_reference'][0]
        model_details = self._client.repository.store_model(self._model_metadata['model_file'], model_props)
        model_guid = self._client.repository.get_model_uid(model_details)
        logger.info('Created new model: {} (guid: {})'.format(model_name, model_guid))
        return (metadata, model_guid)

    def _list_all_models(self):
        logger.info('Listing all models:')
        self._client.repository.list_models()

    def _deploy_model(self, model_guid, deployment_name, deployment_description):
        logger.info('Creating new deployment: {}'.format(deployment_name))
        deployment_details = self._client.deployments.create(artifact_uid=model_guid, name=deployment_name, description=deployment_description)
        deployment_guid = deployment_details['metadata']['guid']
        logger.info('Created new deployment: {} (guid: {})'.format(deployment_name, deployment_guid))
        return deployment_guid

    def _delete_deployments(self, deployment_name):
        logger.info('Checking for deployments with the name: {}'.format(deployment_name))
        deployment_details = self._client.deployments.get_details()
        found_deployment = False
        for details in deployment_details['resources']:
            deployment_guid = details['metadata']['guid']
            if deployment_name == details['entity']['name']:
                try:
                    found_deployment = True
                    logger.info('Deleting deployment: {}'.format(deployment_name))
                    self._client.deployments.delete(deployment_guid)
                except:
                    logger.warning('Error deleting WML deployment: %s', deployment_guid)
        if not found_deployment:
            logger.info('No existing deployment found with name: {}'.format(deployment_name))

    def _list_all_deployments(self):
        deployment_details = self._client.deployments.get_details()
        for details in deployment_details['resources']:
            logger.info('Name: {}, GUID: {}'.format(details['entity']['name'], details['metadata']['guid']))

    def create_model_and_deploy(self):
        model_name = self._model_metadata['model_name']
        deployment_name = self._model_metadata['deployment_name']

        self._delete_models(model_name)
        # self._create_pipeline(model_name, self._model_metadata['pipeline_metadata_file'])
        model_metadata_dict, model_guid = self._create_model(model_name, self._model_metadata['model_metadata_file'])
        self._delete_deployments(deployment_name)
        deployment_guid = self._deploy_model(model_guid, deployment_name, self._model_metadata['deployment_description'])

        model_deployment_dict = {}
        model_deployment_dict['model_name'] = model_name
        model_deployment_dict['model_guid'] = model_guid
        model_deployment_dict['model_metadata_dict'] = model_metadata_dict
        model_deployment_dict['deployment_name'] = deployment_name
        model_deployment_dict['deployment_guid'] = deployment_guid

        return model_deployment_dict

    def model_cleanup(self):
        model_name = self._model_metadata['model_name']
        deployment_name = self._model_metadata['deployment_name']
        self._delete_models(model_name)
        self._delete_deployments(deployment_name)

    # used for load generator scenario to get existing deployment properties
    # returns info for first-found deployment, if there are multiple
    def get_existing_deployment(self):
        model_name = self._model_metadata['model_name']
        deployment_name = self._model_metadata['deployment_name']

        logger.info('Use existing model named: {}'.format(model_name))
        models = self._client.repository.get_model_details()
        for this_model in models['resources']:
            this_model_name = this_model['entity']['name']
            guid = this_model['metadata']['guid']
            metaData = this_model['metadata']
            if model_name == this_model_name:
                model_guid = guid
                model_metadata_dict = metaData
                break
        deploymentDetails = self._client.deployments.get_details()
        for details in deploymentDetails['resources']:
            dep_guid = details['metadata']['guid']
            dep_name = details['entity']['name']
            if dep_name == deployment_name:
                deployment_guid = dep_guid
                break
        logger.info('Model Name: {}  Model GUID: {}'.format(model_name, model_guid))
        logger.info('Deployment Name: {}  Deployment GUID: {}'.format(deployment_name, deployment_guid))

        model_deployment_dict = {}
        model_deployment_dict['model_metadata_dict'] = model_metadata_dict
        model_deployment_dict['model_guid'] = model_guid
        model_deployment_dict['deployment_guid'] = deployment_guid

        return model_deployment_dict
