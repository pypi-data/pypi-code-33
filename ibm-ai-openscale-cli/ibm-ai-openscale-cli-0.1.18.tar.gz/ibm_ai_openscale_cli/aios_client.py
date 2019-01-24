# coding=utf-8
import datetime
import os
import logging
import requests
import json
from retry import retry
from ibm_ai_openscale import APIClient, APIClient4ICP, WatsonMachineLearningInstance4ICP
from ibm_ai_openscale.engines import WatsonMachineLearningInstance, WatsonMachineLearningAsset
from ibm_ai_openscale.supporting_classes import Feature, InputDataType, ProblemType
from ibm_ai_openscale_cli.utility_classes.utils import get_iam_headers
from watson_machine_learning_client import WatsonMachineLearningAPIClient

logger = logging.getLogger(__name__)
parent_dir = os.path.dirname(__file__)

class AIOSClient():

    def __init__(self, credentials, datamart_name, target_env, model):
        self._credentials = credentials
        target_env_name = target_env['name'].lower()
        self._target_env = target_env
        self._datamart_name = datamart_name
        if datamart_name == 'aiosfastpath' and target_env_name != 'ypprod':
            self._datamart_name = datamart_name + target_env_name
        self._model = model
        self._client = None
        self._is_icp = True if target_env_name == 'icp' else False
        self._verify = False if self._is_icp else True
        if self._is_icp:
            self._client = APIClient4ICP(credentials)
        else:
            self._client = APIClient(credentials)
        logger.info('Using AI Openscale (AIOS) Python Client version: {}'.format(self._client.version))

    @retry(tries=5, delay=4, backoff=2)
    def clean_datamart(self):
        logger.info('Clean up datamart, if already present: {}'.format(self._datamart_name))
        subscriptions_uids = self._client.data_mart.subscriptions.get_uids()

        # clean up all subscriptions in the datamart
        for subscription_uid in subscriptions_uids:
            # disable explainability, fairness checking, and payload logging for the subscription
            subscription = self._client.data_mart.subscriptions.get(subscription_uid)
            subscription.explainability.disable()
            subscription.fairness_monitoring.disable()
            subscription.payload_logging.disable()
            # then remove the subscription itself
            self._client.data_mart.subscriptions.delete(subscription_uid)

        # remove bindings
        try:
            bindings_uids = self._client.data_mart.bindings.get_uids()
            for binding_uid in bindings_uids:
                self._client.data_mart.bindings.delete(binding_uid)
        except:
            logger.warn('datamart bindings could not be deleted')

        # remove previous datamart
        try:
            self._client.data_mart.delete()
        except Exception as e:
            if 'AISCS0005W' in str(e): # datamart does not exist, so cannot delete
                logger.debug(e)
            else:
                raise e

    @retry(tries=5, delay=8, backoff=2)
    def create_datamart(self, database_credentials):
        '''
        Create datamart schema and datamart
        '''
        logger.info('Create datamart: {}'.format(self._datamart_name))

        if database_credentials is None:
            logger.info('AIOS PostgreSQL instance: internal')
            self._client.data_mart.setup(internal_db=True)
        else:
            database = None
            if database_credentials['db_type'] == 'postgresql':
                if 'postgres' in database_credentials: # icd
                    from ibm_ai_openscale_cli.database_classes.postgres_icd import PostgresICD
                    database = PostgresICD(database_credentials)
                else: # compose
                    from ibm_ai_openscale_cli.database_classes.postgres_compose import PostgresCompose
                    database = PostgresCompose(database_credentials)
            elif database_credentials['db_type'] == 'db2':
                    from ibm_ai_openscale_cli.database_classes.db2 import DB2
                    database = DB2(database_credentials)
            else:
                raise Exception('Invalid database type specified. Only "postgresql" and "db2" are supported.')
            database.drop_existing_schema(self._datamart_name)
            database.create_new_schema(self._datamart_name)
            self._client.data_mart.setup(db_credentials=database_credentials, schema=self._datamart_name)

        logger.info('Datamart {} created'.format(self._datamart_name))

    @retry(tries=5, delay=4, backoff=2)
    def bind_mlinstance(self, wml_credentials):
        '''
        Bind ML instance to AIOS
        '''
        logger.info('Bind WML instance to AIOS')
        binding_name = None
        if self._is_icp:
            wml_instance = WatsonMachineLearningInstance4ICP()
            binding_name = 'WML ICP instance'
        else:
            wml_instance =  WatsonMachineLearningInstance(wml_credentials)
            binding_name = 'WML instance'
        return self._client.data_mart.bindings.add(binding_name, wml_instance)

    @retry(tries=5, delay=4, backoff=2)
    def get_existing_binding(self, wml_credentials):
        if self._is_icp:
            binding_guid = '999'
        else:
            wml_client = WatsonMachineLearningAPIClient(wml_credentials)
            binding_guid = wml_client.service_instance.get_instance_id()
        return binding_guid

    @retry(tries=5, delay=4, backoff=2)
    def subscribe_to_model_deployment(self, model_deployment):
        '''
        Create subscription in AIOS for the given model
        '''
        logger.info('Register ML instance to AIOS: {}'.format(model_deployment['model_name']))
        if 'output_data_schema' in model_deployment['model_metadata_dict']:
            subscription = self._client.data_mart.subscriptions.add(WatsonMachineLearningAsset(model_deployment['model_guid']))
        else:
            subscription = self._client.data_mart.subscriptions.add(WatsonMachineLearningAsset(model_deployment['model_guid'], prediction_column='prediction'))
        return subscription

    @retry(tries=5, delay=8, backoff=2)
    def configure_subscription(self, model_deployment, subscription):
        '''
        Configure payload logging plus performance, fairness, explainability, and accuracy monitoring
        '''
        model_name = model_deployment['model_name']

        logger.info('Enable payload logging in AIOS: {}'.format(model_name))
        subscription.payload_logging.enable()

        logger.info('Enable Performance Monitoring in AIOS: {}'.format(model_name))
        subscription.performance_monitoring.enable()

        fairness_monitoring_params = self._model.configuration_data['fairness_configuration']
        if fairness_monitoring_params == 'None':
            logger.info('No fairness monitoring configuration for model: {}'.format(model_name))
        else:
            logger.info('Configuring fairness monitoring for model: {}'.format(model_name))
            feature_list = []
            for elem in fairness_monitoring_params['features']:
                feature = Feature(elem['feature'], elem['majority'], elem['minority'], float(elem['threshold']))
                feature_list.append(feature)
            fairness_monitoring_params['features'] = feature_list
            subscription.fairness_monitoring.enable(**fairness_monitoring_params)

        quality_monitoring_params = self._model.configuration_data['quality_configuration']
        if quality_monitoring_params == 'None':
            logger.info('No qaulity monitoring configuration for model: {}'.format(model_name))
        else:
            logger.info('Configuring accuracy monitoring for model: {}'.format(model_name))
            subscription.quality_monitoring.enable(**quality_monitoring_params)

        feedback_params = self._model.configuration_data['feedback_configuration']
        if feedback_params == 'None':
            logger.info('No feedback logging configuration for model: {}'.format(model_name))
        else:
            logger.info('Configuring feedback logging for model: {}'.format(model_name))
            subscription.feedback_logging.store(**feedback_params)

        model_metadata = model_deployment['model_metadata_dict']
        explainability_config_data = self._model.configuration_data['explainability_configuration']
        if explainability_config_data == 'None':
            logger.info('No explainability configuration for model: {}'.format(model_name))
        else:
            logger.info('Configuring explainability for model: {}'.format(model_name))
            subscription.explainability.enable(
                label_column=explainability_config_data['label_column'],
                feature_columns=explainability_config_data['feature_columns'],
                categorical_columns=explainability_config_data['categorical_columns'],
                input_data_type=self._get_explainability_input_data_type_object(explainability_config_data['input_data_type']),
                problem_type=self._get_explainability_problem_type_object(explainability_config_data['problem_type'])
            )

    def _get_explainability_input_data_type_object(self, data):
        if data == 'structured':
            return InputDataType.STRUCTURED
        return None

    def _get_explainability_problem_type_object(self, data):
        if data == 'binary':
            return ProblemType.BINARY_CLASSIFICATION
        elif data == 'multiclass':
            return ProblemType.MULTICLASS_CLASSIFICATION
        elif data == 'regression':
            return ProblemType.REGRESSION
        return None

#    @retry(tries=5, delay=4, backoff=2)
    def generate_sample_scoring(self, model_deployment, bindingGuid, subscription):
        '''
        Generate historical data
        Generate sample scoring requests
        Trigger fairness check
        '''
        model_name = model_deployment['model_name']

        wml_client = self._client.data_mart.bindings.get_native_engine_client(binding_uid=bindingGuid)
        deployment_details = wml_client.deployments.get_details(model_deployment['deployment_guid'])
        deployment_url = wml_client.deployments.get_scoring_url(deployment_details)

        logger.info('Load historical scoring records to Payload Logging in AIOS: {}'.format(model_name))
        self.reliable_payload_logging(subscription)

        logger.info('Load historical performance tables in AIOS: {}'.format(model_name))
        history = self._model.get_performance_history()
        self.reliable_post_metrics('performance', history, bindingGuid, model_deployment)

        logger.info('Load historical fairness MeasurementFacts to AIOS: {}'.format(model_name))
        history = self._model.get_fairness_history()
        self.reliable_post_metrics('fairness', history, bindingGuid, model_deployment)

        logger.info('Load historical quality MeasurementFacts to AIOS: {}'.format(model_name))
        history = self._model.get_quality_history()
        self.reliable_post_metrics('quality', history, bindingGuid, model_deployment)

        numscores = 100
        logger.info('Generate {} new scoring requests to AIOS: {}'.format(numscores, model_name))
        if self._is_icp and ':31002' not in deployment_url:
                deployment_url_host = ':'.join(deployment_url.split(':')[:2])
                args_url_host = ':'.join(self._target_env['aios_url'].split(':')[:2])
                deployment_url = deployment_url.replace('{}:16600'.format(deployment_url_host), '{}:31002'.format(args_url_host))
        for _ in range(numscores):
            wml_client.deployments.score(deployment_url, self._model.get_score_input())

        logger.info('Trigger immediate fairness check AIOS: {}'.format(model_name))
        fairness_monitoring_params = self._model.configuration_data['fairness_configuration']
        if fairness_monitoring_params == 'None':
            logger.info('Skip fairness check for model: {}'.format(model_name))
        else:
            subscription.fairness_monitoring.run()

        logger.info('Trigger immediate quality check AIOS: {}'.format(model_name))
        quality_monitoring_params = self._model.configuration_data['quality_configuration']
        if quality_monitoring_params == 'None':
            logger.info('Skip quality check for model: {}'.format(model_name))
        else:
            subscription.quality_monitoring.run()

    @retry(tries=5, delay=4, backoff=2)
    def reliable_payload_logging(self, subscription):
        records = self._model.get_payload_history()
        if len(records) > 0:
            subscription.payload_logging.store(records=records)

    @retry(tries=5, delay=4, backoff=2)
    def reliable_post_metrics(self, metric_type, records, binding_id, model_deployment):
        '''
        Retry the loading metrics so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        metrics_url = '{0}/v1/data_marts/{1}/metrics'.format(self._credentials['url'], self._credentials['data_mart_id'])
        iam_headers = get_iam_headers(self._credentials, self._target_env)
        model_guid = model_deployment['model_guid']
        deployment_guid = model_deployment['deployment_guid']
        for record in records:
            record_json = {
                'metric_type': metric_type,
                'binding_id': binding_id,
                'timestamp': record['timestamp'],
                'subscription_id': model_guid,
                'asset_revision': model_guid,
                'value': record['value'],
                'deployment_id': deployment_guid,

            }
            requests.post(metrics_url, json=[record_json], headers=iam_headers, verify=self._verify)
