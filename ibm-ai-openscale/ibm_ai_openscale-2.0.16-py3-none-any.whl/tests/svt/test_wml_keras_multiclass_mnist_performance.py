# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest
import time
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *


class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    binding_uid = None
    subscription = None
    scoring_result = None
    test_uid = str(uuid.uuid4())

    model_path = os.path.join(os.getcwd(), 'artifacts', 'core_ml', 'keras', 'mnistCNN.h5.tgz')

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)
            cls.wml_credentials = get_wml_credentials()

        prepare_env(cls.ai_client)

    def test_01_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_02_data_mart_get_details(self):
        details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        print(details)
        self.assertTrue(len(json.dumps(details)) > 10)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud",WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(
            binding_uid)

    def test_05_prepare_deployment(self):
        model_name = "AIOS Keras mnist model"
        deployment_name = "AIOS Keras mnist deployment"

        wml_models = self.wml_client.repository.get_details()

        for model in wml_models['models']['resources']:
            if model_name == model['entity']['name']:
                TestAIOpenScaleClient.model_uid = model['metadata']['guid']
                break

        if self.model_uid is None:
            print("Storing model ...")

            model_props = {
                self.wml_client.repository.ModelMetaNames.NAME: "{}".format(model_name),
                self.wml_client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                self.wml_client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                self.wml_client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                self.wml_client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5",
                self.wml_client.repository.ModelMetaNames.FRAMEWORK_LIBRARIES: [{'name': 'keras', 'version': '2.1.3'}],
            }

            published_model_details = self.wml_client.repository.store_model(model=self.model_path,meta_props=model_props)
            TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        wml_deployments = self.wml_client.deployments.get_details()

        for deployment in wml_deployments['resources']:
            if deployment_name == deployment['entity']['name']:
                TestAIOpenScaleClient.deployment_uid = deployment['metadata']['guid']
                break

        if self.deployment_uid is None:
            print("Deploying model...")

            deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
            TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        print("Model id: {}".format(self.model_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_06_subscribe(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_07_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(
            self.model_uid)
        print(str(TestAIOpenScaleClient.subscription.get_details()))

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_09_check_if_payload_logging_and_performance_enabled(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        for configuration in subscription_details['entity']['configurations']:
            if configuration['type'] == 'performance_monitoring' or configuration['type'] == 'payload_logging':
                self.assertEqual(configuration['enabled'], True)

    def test_10_get_payload_logging_details(self):
        TestAIOpenScaleClient.subscription.payload_logging.get_details()

    def test_11_get_performance_monitor_details(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.get_details()

    def test_12_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        from keras.datasets import mnist
        import numpy as np

        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        image_1 = np.expand_dims(x_test[0], axis=2)
        image_2 = np.expand_dims(x_test[1], axis=2)

        scoring_payload = {'values': [image_1.tolist(), image_2.tolist()]}

        for i in range(0, 20):
            scores = self.wml_client.deployments.score(scoring_url=scoring_endpoint, payload=scoring_payload)
            self.assertIsNotNone(scores)

        print("Waiting 30 seconds for performance calculation...")
        time.sleep(60)

    def test_13_stats_on_payload_logging_table(self):
        print("Print table schema:")
        self.subscription.payload_logging.print_table_schema()
        print("Show table:")
        self.subscription.payload_logging.show_table()

        print("Describe table description:")
        table_description = self.subscription.payload_logging.describe_table()
        print("Table description:\n{}".format(table_description))

        table_content = self.subscription.payload_logging.get_table_content()
        print("Table content:\n{}".format(table_content))
        print(type(table_content))

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        print("Python Table content:\n{}".format(python_table_content))
        self.assertGreater(table_content.size, 1)

        self.assertIsNotNone(python_table_content)

    def test_14_stats_on_performance_monitoring_table(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        TestAIOpenScaleClient.subscription.performance_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.performance_monitoring.show_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content()
        performance_metrics = TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content(format='python')
        self.assertTrue(len(performance_metrics['values']) > 0)

    def test_15_disable_payload_logging_and_performance_monitoring(self):
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()

        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        for configuration in subscription_details['entity']['configurations']:
            if configuration['type'] == 'payload_logging' or configuration['type'] == 'performance_monitoring':
                self.assertFalse(configuration['enabled'])

    def test_16_get_metrics(self):
        performance_metrics_deployment_uid = self.subscription.performance_monitoring.get_metrics(deployment_uid=self.deployment_uid)
        print("-> performance_monitoring.get_metrics(deployment_uid={})\n{}".format(self.deployment_uid, performance_metrics_deployment_uid))
        self.assertGreater(len(performance_metrics_deployment_uid['metrics']), 0)

        last_metric = performance_metrics_deployment_uid['metrics'][0]
        for metric in performance_metrics_deployment_uid['metrics']:
            if datetime.strptime(metric['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.strptime(last_metric['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ") > timedelta(0):
                last_metric = metric

        performance_metrics_deployments = self.subscription.performance_monitoring.get_deployment_metrics()
        print("-> performance_monitoring.get_deployment_metrics()\n{}".format(performance_metrics_deployments))

        current_deployment_metric = None
        for deployment in performance_metrics_deployments['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment

        self.assertIsNotNone(current_deployment_metric, msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        performance_metrics_asset_uid = self.ai_client.data_mart.get_deployment_metrics(asset_uid=self.subscription.source_uid, metric_type='performance')
        print("-> get_deployment_metrics(asset_uid={}, metric_type='performance')\n{}".format(self.subscription.source_uid, performance_metrics_asset_uid))

        current_deployment_metric = None
        for deployment in performance_metrics_asset_uid['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment

        self.assertIsNotNone(current_deployment_metric, msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        deployment_metrics = self.ai_client.data_mart.get_deployment_metrics()
        print("-> data_mart.get_deployment_metrics()\n{}".format(deployment_metrics))

        current_deployment_metric = None
        for deployment in deployment_metrics['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment

        self.assertIsNotNone(current_deployment_metric, msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        deployment_metrics_deployment_uid = self.ai_client.data_mart.get_deployment_metrics(deployment_uid=self.deployment_uid)
        print("-> get_deployment_metrics(deployment_uid={})\n{}".format(self.deployment_uid, deployment_metrics_deployment_uid))
        current_deployment_metric = None
        for deployment in deployment_metrics_deployment_uid['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment
        self.assertGreater(len(deployment_metrics_deployment_uid['deployment_metrics']), 0)
        self.assertIsNotNone(current_deployment_metric, msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        deployment_metrics_subscription_uid = self.ai_client.data_mart.get_deployment_metrics(subscription_uid=self.subscription.uid)
        print("-> get_deployment_metrics(subscription_uid={})\n{}".format(self.subscription.uid, deployment_metrics_subscription_uid))
        current_deployment_metric = None
        for deployment in deployment_metrics_subscription_uid['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment
        self.assertGreater(len(deployment_metrics_subscription_uid['deployment_metrics']), 0)
        self.assertIsNotNone(current_deployment_metric, msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        deployment_metrics_asset_uid = self.ai_client.data_mart.get_deployment_metrics(asset_uid=self.subscription.source_uid)
        print("-> get_deployment_metrics(asset_uid={})\n{}".format(self.subscription.source_uid, deployment_metrics_asset_uid))
        current_deployment_metric = None
        for deployment in deployment_metrics_asset_uid['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment
        self.assertGreater(len(deployment_metrics_asset_uid['deployment_metrics']), 0)
        self.assertIsNotNone(current_deployment_metric, msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

    def test_17_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_18_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
