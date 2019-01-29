# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import logging
import unittest
import time
from ibm_ai_openscale import APIClient
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *
from datasets_classes import BostonDataset


@unittest.skip("Deep learning models are not supported by AIOS quality monitoring.")
class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    aios_model_uid = None
    definition_url = None
    definition_uid = None
    experiment_uid = None
    experiment_run_uid = None
    train_run_uid = None
    scoring_url = None
    labels = None
    logger = logging.getLogger(__name__)
    ai_client = None
    wml_client = None
    subscription = None
    test_uid = str(uuid.uuid4())

    @classmethod
    def setUpClass(self):
        TestAIOpenScaleClient.logger.info("Service Instance: setting up credentials")

        clean_env()

        self.aios_credentials = get_aios_credentials()
        self.wml_credentials = get_wml_credentials()
        self.postgres_credentials = get_postgres_credentials()
        self.spark_credentials = get_spark_reference()
        self.cos_resource = get_cos_resource()
        self.bucket_names = prepare_cos(self.cos_resource)
        BostonDataset.upload_to_cos(self.cos_resource, self.bucket_names['data'])

    @classmethod
    def tearDownClass(self):
        clean_cos(self.cos_resource, self.bucket_names)

    def test_01_create_client(self):
        TestAIOpenScaleClient.ai_client = APIClient(self.aios_credentials)

    def test_02_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.postgres_credentials, schema=get_schema_name())

    def test_03_bind_wml_instance_and_get_wml_client(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.add("My WML instance", WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_save_definition(self):
        TestAIOpenScaleClient.logger.info("Save model definition ...")

        metadata = {
            self.wml_client.repository.DefinitionMetaNames.NAME: "my_training_definition",
            self.wml_client.repository.DefinitionMetaNames.DESCRIPTION: "my_description",
            self.wml_client.repository.DefinitionMetaNames.AUTHOR_EMAIL: "js@js.com",
            self.wml_client.repository.DefinitionMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.wml_client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: "1.5",
            self.wml_client.repository.DefinitionMetaNames.RUNTIME_NAME: "python",
            self.wml_client.repository.DefinitionMetaNames.RUNTIME_VERSION: "3.5",
            self.wml_client.repository.DefinitionMetaNames.EXECUTION_COMMAND: "python3 keras_boston.py --epochs_iters 1"
        }

        model_content_path = './artifacts/keras_boston.zip'
        definition_details = self.wml_client.repository.store_definition(training_definition=model_content_path, meta_props=metadata)
        TestAIOpenScaleClient.definition_url = self.wml_client.repository.get_definition_url(definition_details)
        TestAIOpenScaleClient.definition_uid = self.wml_client.repository.get_definition_uid(definition_details)
        TestAIOpenScaleClient.logger.info("Saved model definition url: " + str(TestAIOpenScaleClient.definition_url))

        details = self.wml_client.repository.get_definition_details(TestAIOpenScaleClient.definition_uid)
        print("Definition details:" + str(details))

        self.assertIsNotNone(TestAIOpenScaleClient.definition_url)

    def test_06_save_experiment(self):
        metadata = {
            self.wml_client.repository.ExperimentMetaNames.NAME: "my_experiment",
            self.wml_client.repository.ExperimentMetaNames.DESCRIPTION: "boston house prices",
            self.wml_client.repository.ExperimentMetaNames.AUTHOR_NAME: "John Smith",
            self.wml_client.repository.ExperimentMetaNames.EVALUATION_METHOD: "multiclass",
            self.wml_client.repository.ExperimentMetaNames.EVALUATION_METRICS: ["accuracy"],
            self.wml_client.repository.ExperimentMetaNames.TRAINING_DATA_REFERENCE: get_cos_training_data_reference(
                self.bucket_names),
            self.wml_client.repository.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE: get_cos_training_results_reference(
                self.bucket_names),
            self.wml_client.repository.ExperimentMetaNames.TRAINING_REFERENCES: [
                {
                    "name": "boston_nn",
                    "training_definition_url": TestAIOpenScaleClient.definition_url,
                    "compute_configuration": {"name": "k80"}
                }
            ]
        }

        print(get_cos_training_data_reference(self.bucket_names))
        print(get_cos_training_results_reference(self.bucket_names))
        experiment_details = self.wml_client.repository.store_experiment(meta_props=metadata)
        TestAIOpenScaleClient.experiment_uid = self.wml_client.repository.get_experiment_uid(experiment_details)

        experiment_specific_details = self.wml_client.repository.get_experiment_details(TestAIOpenScaleClient.experiment_uid)
        self.assertTrue(TestAIOpenScaleClient.experiment_uid in str(experiment_specific_details))

    def test_07_run_experiment(self):
        created_experiment_run_details = self.wml_client.experiments.run(TestAIOpenScaleClient.experiment_uid, asynchronous=False)
        self.assertIsNotNone(created_experiment_run_details)
        TestAIOpenScaleClient.experiment_run_uid = self.wml_client.experiments.get_run_uid(created_experiment_run_details)
        print("Experiment run id:\n{}".format(TestAIOpenScaleClient.experiment_run_uid))

    def test_08_get_status(self):
        start_time = time.time()
        diff_time = start_time - start_time
        while True and diff_time < 60 * 10:
            time.sleep(3)
            status = self.wml_client.experiments.get_status(TestAIOpenScaleClient.experiment_run_uid)
            if status['state'] == 'completed' or status['state'] == 'error' or status['state'] == 'canceled':
                break
            diff_time = time.time() - start_time
        self.assertIsNotNone(status)
        self.assertTrue(status['state'] == 'completed')

    def test_09_get_experiment_run_details(self):
        details = self.wml_client.experiments.get_run_details(TestAIOpenScaleClient.experiment_run_uid)
        print("Experiment run details:\n{}".format(details))
        self.assertIsNotNone(details)

        self.assertIsNotNone(self.wml_client.experiments.get_training_runs(details))
        self.assertIsNotNone(self.wml_client.experiments.get_training_uids(details))

    def test_10_store_model(self):
        TestAIOpenScaleClient.train_run_uid = self.wml_client.experiments.get_details(TestAIOpenScaleClient.experiment_uid)['resources'][0]['entity']['training_statuses'][0]['training_guid']
        print("train_run_uid: " + TestAIOpenScaleClient.train_run_uid)

        meta_data = {
            self.wml_client.repository.ModelMetaNames.NAME: "Keras Boston",
        }

        print("Definition URL: " + TestAIOpenScaleClient.definition_url)
        trained_model_details = self.wml_client.repository.store_model(TestAIOpenScaleClient.train_run_uid, meta_props=meta_data)
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(trained_model_details)

        print("Stored model details: " + str(trained_model_details))
        self.assertIsNotNone(TestAIOpenScaleClient.model_uid)

    def test_11_create_deployment(self):
        TestAIOpenScaleClient.logger.info("Create deployment")

        deployment_details = self.wml_client.deployments.create(artifact_uid=TestAIOpenScaleClient.model_uid, name="Test deployment", asynchronous=False)
        TestAIOpenScaleClient.logger.debug("Deployment details: " + str(deployment_details))
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment_details)
        TestAIOpenScaleClient.scoring_url = self.wml_client.deployments.get_scoring_url(deployment_details)
        self.assertTrue('online' in str(TestAIOpenScaleClient.scoring_url))

    def test_12_subscribe(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_13_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.aios_model_uid)

    def test_13b_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_14_setup_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(evaluation_method='regression', threshold=0.8, min_records=5, training_results_reference=get_cos_training_results_reference(self.bucket_names))

    def test_15_get_quality_monitoring_details(self):
        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        print("Quality monitor details: " + str(details))

    def test_16b_run_learning_iteration(self):
        run_details = TestAIOpenScaleClient.wml_client.learning_system.run(TestAIOpenScaleClient.model_uid, asynchronous=False)
        print(run_details)
        import time
        time.sleep(20)
        self.assertTrue(run_details['entity']['status']['state'] == 'COMPLETED')
        TestAIOpenScaleClient.wml_client.learning_system.list_metrics(TestAIOpenScaleClient.model_uid)

    def test_17_stats_on_quality_monitoring_table(self):

        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_20_disable_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.disable()

    def test_21_get_metrics(self):
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='quality'))
        print(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        self.assertTrue(len(TestAIOpenScaleClient.subscription.quality_monitoring.get_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid)['metrics']) > 0)

    def test_22_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.subscription.uid)
        wait_until_deleted(TestAIOpenScaleClient.ai_client, subscription_uid=TestAIOpenScaleClient.subscription.uid)

    def test_23_clean(self):
        self.wml_client.repository.delete(TestAIOpenScaleClient.model_uid)
        self.wml_client.repository.delete(TestAIOpenScaleClient.definition_uid)

    def test_24_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.subscription.binding_uid)
        wait_until_deleted(TestAIOpenScaleClient.ai_client, binding_uid=TestAIOpenScaleClient.subscription.binding_uid)

    def test_25_delete_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.delete()
        wait_until_deleted(TestAIOpenScaleClient.ai_client, data_mart=True)
        delete_schema(get_postgres_credentials(), get_schema_name())


if __name__ == '__main__':
    unittest.main()
