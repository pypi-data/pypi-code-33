# coding=utf-8
import datetime
import time
import os
import logging
import requests
import json
from retry import retry
from ibm_ai_openscale import APIClient, APIClient4ICP, WatsonMachineLearningInstance4ICP
from ibm_ai_openscale.engines import WatsonMachineLearningInstance, WatsonMachineLearningAsset, AzureMachineLearningInstance, AzureMachineLearningAsset
from ibm_ai_openscale.supporting_classes import Feature, InputDataType, ProblemType, BluemixCloudObjectStorageReference
from ibm_ai_openscale_cli.utility_classes.utils import get_iam_headers, jsonFileToDict
from watson_machine_learning_client import WatsonMachineLearningAPIClient

logger = logging.getLogger(__name__)
parent_dir = os.path.dirname(__file__)

SERVICE_NAME = 'Watson OpenScale'
class AIOSClient():

    binding_id = None

    def __init__(self, credentials, datamart_name, keep_schema, target_env, model=None, ml_engine_type='wml'):
        self._credentials = credentials
        target_env_name = target_env['name'].lower()
        self._target_env = target_env
        self._datamart_name = datamart_name
        self._keep_schema = keep_schema
        if datamart_name == 'aiosfastpath' and target_env_name != 'ypprod':
            self._datamart_name = datamart_name + target_env_name
        self._model = model
        self.client = None
        self._is_icp = True if target_env_name == 'icp' else False
        self._verify = False if self._is_icp else True
        if self._is_icp:
            self.client = APIClient4ICP(credentials)
        else:
            self.client = APIClient(credentials)
        self._ml_engine_type = ml_engine_type
        self._subscription = None
        self._subscribed_deployment_dict = None
        logger.info('Using {} Python Client version: {}'.format(SERVICE_NAME, self.client.version))

    @retry(tries=5, delay=4, backoff=2)
    def clean_datamart(self, database_credentials):
        logger.info('Clean up datamart, if already present: {}'.format(self._datamart_name))
        subscriptions_uids = self.client.data_mart.subscriptions.get_uids()

        # clean up all metrics and monitors
        self.reset_monitors(database_credentials)

        # clean up all subscriptions in the datamart
        logger.info('Reset datamart subscriptions')
        for subscription_uid in subscriptions_uids:
            subscription = self.client.data_mart.subscriptions.get(subscription_uid)
            self.client.data_mart.subscriptions.delete(subscription_uid)

        # remove bindings
        logger.info('Reset datamart bindings')
        try:
            bindings_uids = self.client.data_mart.bindings.get_uids()
            for binding_uid in bindings_uids:
                self.client.data_mart.bindings.delete(binding_uid)
        except:
            logger.warn('Datamart bindings could not be deleted')

        # remove previous datamart
        logger.info('Reset datamart')
        try:
            self.client.data_mart.delete()
        except Exception as e:
            ignore_exceptions = ['AIQC50005W', 'AISCS0005W'] # datamart does not exist, so cannot delete
            if any(word in str(e) for word in ignore_exceptions):
                logger.debug(e)
            else:
                raise e
        # remove database tables and schema
        if database_credentials is None:
            pass # Cannot remove tables or schema for AIOS internal database instance
        else:
            database = self._get_database(database_credentials)
            database.drop_existing_schema(self._datamart_name, self._keep_schema)

    def _get_database(self, database_credentials):
        if database_credentials['db_type'] == 'postgresql':
            if 'postgres' in database_credentials: # icd
                from ibm_ai_openscale_cli.database_classes.postgres_icd import PostgresICD
                return PostgresICD(database_credentials)
            else: # compose
                from ibm_ai_openscale_cli.database_classes.postgres_compose import PostgresCompose
                return PostgresCompose(database_credentials)
        elif database_credentials['db_type'] == 'db2':
            from ibm_ai_openscale_cli.database_classes.db2 import DB2
            return DB2(database_credentials)
        else:
            raise Exception('Invalid database type specified. Only "postgresql" and "db2" are supported.')

    @retry(tries=5, delay=8, backoff=2)
    def create_datamart(self, database_credentials):
        '''
        Create datamart schema and datamart
        '''
        logger.info('Create datamart: {}'.format(self._datamart_name))

        if database_credentials is None:
            logger.info('PostgreSQL instance: internal')
            self.client.data_mart.setup(internal_db=True)
        else:
            database = self._get_database(database_credentials)
            database.create_new_schema(self._datamart_name, self._keep_schema)
            self.client.data_mart.setup(db_credentials=database_credentials, schema=self._datamart_name)
        logger.info('Datamart {} created'.format(self._datamart_name))

    @retry(tries=5, delay=4, backoff=2)
    def bind_mlinstance(self, credentials):
        '''
        Bind ML instance
        '''
        logger.info('Bind {} instance to {}'.format(self._ml_engine_type, SERVICE_NAME))
        binding_name = None
        if self._ml_engine_type == 'wml':
            if self._is_icp:
                ml_instance = WatsonMachineLearningInstance4ICP()
            else:
                ml_instance = WatsonMachineLearningInstance(credentials)
        elif self._ml_engine_type == 'azureml':
                ml_instance = AzureMachineLearningInstance(credentials)
        binding_name = '{}{}Instance'.format(self._ml_engine_type.upper(), 'ICP' if self._is_icp else ' ')
        AIOSClient.binding_id = self.client.data_mart.bindings.add(binding_name, ml_instance)
        logger.info('Binding complete')

    @retry(tries=5, delay=4, backoff=2)
    def use_existing_binding(self, wml_credentials=None):
        if self._is_icp:
            AIOSClient.binding_id = '999'
        elif self._ml_engine_type == 'wml':
            wml_client = WatsonMachineLearningAPIClient(wml_credentials)
            AIOSClient.binding_id = wml_client.service_instance.get_instance_id()
        elif self._ml_engine_type == 'azureml':
            pass #TODO

    @retry(tries=5, delay=4, backoff=2)
    def subscribe_to_model_deployment(self, model_deployment):
        '''
        Create subscription for the given model
        '''
        logger.info('Subscribe ML deployment to {}'.format(SERVICE_NAME))
        if self._ml_engine_type == 'wml':
            if 'output_data_schema' in model_deployment['model_metadata_dict']:
                self._subscription = self.client.data_mart.subscriptions.add(WatsonMachineLearningAsset(model_deployment['model_guid']))
            else:
                self._subscription = self.client.data_mart.subscriptions.add(WatsonMachineLearningAsset(model_deployment['model_guid'], prediction_column='prediction'))
        elif self._ml_engine_type == 'azureml':
            azure_ml_asset = AzureMachineLearningAsset( source_uid=model_deployment['source_uid'],
                                                        binding_uid=AIOSClient.binding_id,
                                                        input_data_type=InputDataType.STRUCTURED,
                                                        problem_type=ProblemType.BINARY_CLASSIFICATION,
                                                        label_column='Risk',
                                                        prediction_column='Scored Labels',
                                                        probability_column='Scored Probabilities' )
            self._subscription = self.client.data_mart.subscriptions.add(azure_ml_asset)
        self._subscribed_deployment_dict = model_deployment
        logger.info('Subscription complete')

    @retry(tries=5, delay=8, backoff=2)
    def configure_subscription(self):
        '''
        Configure payload logging plus performance, fairness, explainability, and accuracy monitoring
        '''
        logger.info('Enable payload logging')
        self._subscription.payload_logging.enable()

        logger.info('Enable Performance Monitoring')
        self._subscription.performance_monitoring.enable()

    def _get_config_params(self, param_key_name):
        params = self._model.configuration_data[param_key_name]
        param_name = param_key_name.split('_')[0]
        if not params:
            logger.info('{} configuration not available for this model'.format(param_name))
        else:
            logger.info('Configuring {}'.format(param_name))
        return params

    def configure_subscription_monitors(self):
        self.configure_fairness()
        self.configure_quality()
        self.configure_feedback()
        self.configure_explainability()

    @retry(tries=5, delay=8, backoff=2)
    def configure_fairness(self):
        fairness_monitoring_params = self._get_config_params('fairness_configuration')
        if fairness_monitoring_params:
            feature_list = []
            for elem in fairness_monitoring_params['features']:
                feature_list.append(Feature(elem['feature'], elem['majority'], elem['minority'], float(elem['threshold'])))
            fairness_monitoring_params['features'] = feature_list
            if self._model.training_data_stats_fairness:
                fairness_monitoring_params['training_data_statistics'] = jsonFileToDict(self._model.training_data_stats_fairness)
            self._subscription.fairness_monitoring.enable(**fairness_monitoring_params)

    @retry(tries=5, delay=8, backoff=2)
    def configure_quality(self):
        quality_monitoring_params = self._get_config_params('quality_configuration')
        if quality_monitoring_params:
            self._subscription.quality_monitoring.enable(**quality_monitoring_params)

    @retry(tries=5, delay=8, backoff=2)
    def configure_feedback(self):
        feedback_config_params = self._get_config_params('feedback_configuration')
        if feedback_config_params:
            self._subscription.feedback_logging.store(**feedback_config_params)

    @retry(tries=5, delay=8, backoff=2)
    def configure_explainability(self):
        explainability_config_params = self._get_config_params('explainability_configuration')
        if explainability_config_params:
            explainability_config_params['input_data_type'] = self._get_explainability_input_data_type_object(explainability_config_params['input_data_type'])
            explainability_config_params['problem_type'] = self._get_explainability_problem_type_object(explainability_config_params['problem_type'])
            explainability_config_params['training_data_reference'] = None
            if self._model.training_data_stats_explainability:
                explainability_config_params['training_data_statistics'] = jsonFileToDict(self._model.training_data_stats_explainability)
            self._subscription.explainability.enable(**explainability_config_params)

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

    @retry(tries=5, delay=4, backoff=2)
    def generate_sample_metrics(self):
        logger.info('Load historical performance MeasurementFacts to {}'.format(SERVICE_NAME))
        for day in range(self._model._history_days):
            logger.info(' - Loading day {}'.format(day + 1))
            history = self._model.get_performance_history(day)
            self.reliable_post_metrics('performance', history)

        logger.info('Load historical fairness MeasurementFacts to {}'.format(SERVICE_NAME))
        for day in range(self._model._history_days):
            logger.info(' - Loading day {}'.format(day + 1))
            history = self._model.get_fairness_history(day)
            self.reliable_post_metrics('fairness', history)

        logger.info('Load historical quality MeasurementFacts to {}'.format(SERVICE_NAME))
        for day in range(self._model._history_days):
            logger.info(' - Loading day {}'.format(day + 1))
            history = self._model.get_quality_history(day)
            self.reliable_post_metrics('quality', history)

    @retry(tries=5, delay=4, backoff=2)
    def generate_sample_scoring(self, engine_client):
        '''
        Generate historical data
        Generate sample scoring requests
        Trigger fairness check
        '''
        numscores = 100
        logger.info('Generate {} new scoring requests to {}'.format(numscores, SERVICE_NAME))
        start = datetime.datetime.now()
        if self._ml_engine_type == 'wml':
            engine_client = self.client.data_mart.bindings.get_native_engine_client(binding_uid=AIOSClient.binding_id)
            deployment_details = engine_client.deployments.get_details(self._subscribed_deployment_dict['deployment_guid'])
            deployment_url = engine_client.deployments.get_scoring_url(deployment_details)
            if self._is_icp and ':31002' not in deployment_url:
                deployment_url_host = ':'.join(deployment_url.split(':')[:2])
                args_url_host = ':'.join(self._target_env['aios_url'].split(':')[:2])
                deployment_url = deployment_url.replace('{}:16600'.format(deployment_url_host), '{}:31002'.format(args_url_host))
            for _ in range(numscores):
                fields, values = self._model.get_score_input()
                score_input = {'fields': fields, 'values': values }
                engine_client.deployments.score(deployment_url, score_input)
        elif self._ml_engine_type == 'azureml':
            records_list = []
            for _ in range(numscores):
                fields, values = self._model.get_score_input()
                values = values[0]
                value_dict = {}
                for (index, field) in enumerate(fields):
                    value_dict[field] = values[index]
                record = engine_client.score(self._subscription, {'Inputs':{'input1': [value_dict] },'GlobalParameters':{}})
                records_list.append(record)
            self._subscription.payload_logging.store(records=records_list)

        end = datetime.datetime.now()
        elapsed = end - start
        elapsed = (elapsed.days*24*3600 + elapsed.seconds) + elapsed.microseconds/1000000.0
        logger.debug('DEBUG: Generate scoring requests in {} seconds'.format(elapsed))
        logger.debug('DEBUG: Pause 5 seconds to allow payload logging to complete')
        time.sleep(5.0)

        logger.info('Trigger immediate fairness check')
        fairness_monitoring_params = self._model.configuration_data['fairness_configuration']
        if fairness_monitoring_params == 'None':
            logger.info('Skip fairness check for model')
        else:
            self._subscription.fairness_monitoring.run()

        logger.info('Trigger immediate quality check')
        quality_monitoring_params = self._model.configuration_data['quality_configuration']
        if quality_monitoring_params == 'None':
            logger.info('Skip quality check for model')
        else:
            self._subscription.quality_monitoring.run()

    @retry(tries=5, delay=4, backoff=2)
    def payload_logging(self):
        logger.info('Load historical scoring records to Payload Logging')
        records = None
        for day in range(self._model._history_days):
            logger.info(' - Loading day {}'.format(day + 1))
            if self._model.name =='GermanCreditRiskModel' and self._ml_engine_type == 'azureml':
                records = self._model.generate_payload_history()
            else:
                records = self._model.get_payload_history(day)
            start = datetime.datetime.now()
            self._subscription.payload_logging.store(records=records)
            end = datetime.datetime.now()
            elapsed = end - start
            elapsed = (elapsed.days*24*3600 + elapsed.seconds) + elapsed.microseconds/1000000.0
            logger.debug('DEBUG: Load historical scoring records in {} seconds'.format(elapsed))

    @retry(tries=5, delay=4, backoff=2)
    def reliable_post_metrics(self, metric_type, records):
        '''
        Retry the loading metrics so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        metrics_url = '{0}/v1/data_marts/{1}/metrics'.format(self._credentials['url'], self._credentials['data_mart_id'])
        iam_headers = get_iam_headers(self._credentials, self._target_env)
        deployment_guid = None
        model_guid = None
        if self._ml_engine_type == 'wml':
            model_guid = self._subscribed_deployment_dict['model_guid']
            deployment_guid = self._subscribed_deployment_dict['deployment_guid']
        elif self._ml_engine_type == 'azureml':
            model_guid = self._subscribed_deployment_dict['source_uid']
            deployment_guid = self._subscribed_deployment_dict['source_entry_metadata_guid']
        record_json = []
        for record in records:
            record_json.append( {
                'metric_type': metric_type,
                'binding_id': AIOSClient.binding_id,
                'timestamp': record['timestamp'],
                'subscription_id': model_guid,
                'asset_revision': model_guid,
                'value': record['value'],
                'deployment_id': deployment_guid
            })
        start = datetime.datetime.now()
        response = requests.post(metrics_url, json=record_json, headers=iam_headers, verify=self._verify)
        end = datetime.datetime.now()
        elapsed = end - start
        elapsed = (elapsed.days*24*3600 + elapsed.seconds) + elapsed.microseconds/1000000.0
        logger.debug('DEBUG: Load {} metrics in {} seconds'.format(metric_type,elapsed))
        words = ['error', 'exception']
        if any(word in str(response.json()) for word in words):
            logger.warning('WARNING: while posting {} metrics: {}'.format(metric_type, str(response.json())))

    def get_azure_deployment_details(self, deployment_name):
        logger.info('Retrieving azureml assets ...')
        asset_details = self.client.data_mart.bindings.get_asset_details()
        model_deployment_dict = {}
        for detail in asset_details:
            if deployment_name in detail['name']:
                model_deployment_dict['source_uid'] = detail['source_uid']
                model_deployment_dict['scoring_url'] = detail['source_entry']['entity']['scoring_endpoint']['url']
                model_deployment_dict['source_entry_metadata_guid'] = detail['source_entry']['metadata']['guid']
                break
        if not 'source_uid' in model_deployment_dict:
            logger.error('ERROR: Could not find a deployment with the name: {}'.format(deployment_name))
            exit(0)
        return model_deployment_dict

    @retry(tries=5, delay=4, backoff=2)
    def reset_monitors(self, database_credentials):
        '''
        Remove all configured monitors and corresponding metrics and history, but leave the actual model deployments
        (if any) in the datamart. User can proceed to configure the monitors via user interface, API, or fastpath.
        '''
        # first, remove all existing metrics
        self.reset_metrics(database_credentials)

        # next, remove all configured monitors
        logger.info('Reset datamart monitors')
        subscription_uids = self.client.data_mart.subscriptions.get_uids()
        for subscription_uid in subscription_uids:
            subscription = self.client.data_mart.subscriptions.get(subscription_uid)
            subscription.explainability.disable()
            subscription.fairness_monitoring.disable()
            subscription.performance_monitoring.disable()
            subscription.quality_monitoring.disable()
            subscription.payload_logging.disable()

        # finally, drop the monitor-related tables
        if database_credentials is None:
            logger.info('Cannot drop monitor-related tables for {} internal database instance'.format(SERVICE_NAME))
        else:
            database = self._get_database(database_credentials)
            database.drop_metrics_tables(self._datamart_name)

    @retry(tries=5, delay=4, backoff=2)
    def reset_metrics(self, database_credentials):
        '''
        Clean up the payload logging table, monitoring history tables etc, so that it restores the system
        to a fresh state with datamart configured, model deployments added, all monitors configured,
        but no actual metrics in the system yet. The system is ready to go.
        '''
        logger.info('Reset datamart metrics')
        if database_credentials is None:
            logger.info('Cannot reset metrics for {} internal database instance'.format(SERVICE_NAME))
        else:
            database = self._get_database(database_credentials)
            database.reset_metrics_tables(self._datamart_name)
