import time

from assertions import *
from models.xgboost import Agaricus
from preparation_and_cleaning import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *


class TestAIOpenScaleClient(unittest.TestCase):
    ai_client = None
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    scoring_url = None
    labels = None
    wml_client = None
    subscription = None
    binding_uid = None
    aios_model_uid = None
    scoring_result = None
    payload_scoring = None
    published_model_details = None
    source_uid = None

    test_uid = str(uuid.uuid4())

    model = Agaricus()

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
        assert_details(details, schema=self.schema, state='active')

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_prepare_deployment(self):
        TestAIOpenScaleClient.model_uid, TestAIOpenScaleClient.deployment_uid = self.model.deploy_to_wml(self.wml_client)

        print("Model id: {}".format(self.model_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_06_subscribe(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(self.model_uid))
        self.assertIsNotNone(self.subscription)
        TestAIOpenScaleClient.subscription_uid = self.subscription.uid

    def test_07_get_subscription(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

        subscription_details = self.subscription.get_details()
        print("Subscription details:\n{}".format(subscription_details))

    def test_08_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        for configuration in subscription_details['entity']['configurations']:
            if configuration['type'] == 'payload_logging' or configuration['type'] == 'performance_monitoring':
                self.assertEqual(configuration['enabled'], True)
            else:
                self.assertEqual(configuration['enabled'], False)

    def test_09a_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        print("Payload logging details:\n{}".format(payload_logging_details))
        self.assertIsNotNone(payload_logging_details)

        self.assertTrue(payload_logging_details['enabled'])
        self.assertTrue(payload_logging_details['parameters']['dynamic_schema_update'])

    def test_09b_get_performance_monitoring_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        print("Performance monitoring details:\n{}".format(performance_monitoring_details))

        self.assertIsNotNone(performance_monitoring_details)
        self.assertTrue(performance_monitoring_details['enabled'])

    def test_10_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        for i in range(0, 20):
            payload_scoring = self.model.get_scoring_payload()
            scoring_result = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)
            self.assertIsNotNone(scoring_result)

        print("Waiting 60 seconds for propagation.")
        time.sleep(60)

    def test_11_stats_on_payload_logging_table(self):
        print("Print table schema:")
        self.subscription.payload_logging.print_table_schema()
        print("Show table:")
        self.subscription.payload_logging.show_table()

        print("Describe table description:")
        table_description = self.subscription.payload_logging.describe_table()
        print("Table description:\n{}".format(table_description))

        table_content = self.subscription.payload_logging.get_table_content()
        print("Table content:\n{}".format(table_content))

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        print("Python Table content:\n{}".format(python_table_content))

        self.assertGreater(table_content.size, 1)
        self.assertIsNotNone(python_table_content)

        if self.scoring_result is not None and 'fields' in self.scoring_result.keys():
            if 'prediction' in self.scoring_result['fields']:
                self.assertIn('prediction', python_table_content['fields'])

            if 'probability' in self.scoring_result['fields']:
                self.assertIn('probability', python_table_content['fields'])

    def test_12_stats_on_performance_monitoring_table(self):
        print("Printing performance table: ")
        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()
        self.subscription.performance_monitoring.get_table_content()
        performance_metrics = self.subscription.performance_monitoring.get_table_content(format='python')
        print("Performance metrics:\n{}".format(performance_metrics))
        self.assertGreater(len(performance_metrics['values']), 0)

    def test_13_enable_quality_monitoring(self):
        from ibm_ai_openscale.supporting_classes.enums import ProblemType
        self.subscription.quality_monitoring.enable(threshold=0.7, min_records=10, problem_type=ProblemType.BINARY_CLASSIFICATION)
        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        self.assertIn('True', str(details))

    def test_14_feedback_logging(self):

        records = []

        for i in range(0, 20):
            records.append(self.model.get_feedback_payload()['values'])

        TestAIOpenScaleClient.subscription.feedback_logging.store(feedback_data=records)
        time.sleep(60)

        feedback_pd = TestAIOpenScaleClient.subscription.feedback_logging.get_table_content(format='pandas')
        print(feedback_pd)
        self.assertGreater(len(feedback_pd), 1)

    def test_15_stats_on_feedback_logging(self):
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()

    def test_16_run_quality_monitoring(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        self.assertTrue('Prerequisite check' in str(run_details))

        status = run_details['status']
        id = run_details['id']
        start_time = time.time()
        elapsed_time = 0

        while status is not 'completed' and elapsed_time < 60:
            time.sleep(10)
            run_details = TestAIOpenScaleClient.subscription.quality_monitoring.get_run_details(run_uid=id)
            status = run_details['status']
            elapsed_time = time.time() - start_time

        self.assertTrue('completed' in status)

    def test_17_stats_on_quality_monitoring_table(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table(limit=None)
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_18_get_metrics(self):
        performance_metrics_deployment_uid = self.subscription.performance_monitoring.get_metrics(
            deployment_uid=self.deployment_uid)
        print("-> performance_monitoring.get_metrics(deployment_uid={})\n{}".format(self.deployment_uid,
                                                                                    performance_metrics_deployment_uid))
        self.assertGreater(len(performance_metrics_deployment_uid['metrics']), 0)

        last_metric = performance_metrics_deployment_uid['metrics'][0]
        for metric in performance_metrics_deployment_uid['metrics']:
            if datetime.strptime(metric['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.strptime(
                    last_metric['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ") > timedelta(0):
                last_metric = metric

        performance_metrics_deployments = self.subscription.performance_monitoring.get_deployment_metrics()
        print("-> performance_monitoring.get_deployment_metrics()\n{}".format(performance_metrics_deployments))

        current_deployment_metric = None
        for deployment in performance_metrics_deployments['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment

        self.assertIsNotNone(current_deployment_metric,
                             msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        performance_metrics_asset_uid = self.ai_client.data_mart.get_deployment_metrics(
            asset_uid=self.subscription.source_uid, metric_type='performance')
        print("-> get_deployment_metrics(asset_uid={}, metric_type='performance')\n{}".format(
            self.subscription.source_uid, performance_metrics_asset_uid))

        current_deployment_metric = None
        for deployment in performance_metrics_asset_uid['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment

        self.assertIsNotNone(current_deployment_metric,
                             msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        deployment_metrics = self.ai_client.data_mart.get_deployment_metrics()
        print("-> data_mart.get_deployment_metrics()\n{}".format(deployment_metrics))

        current_deployment_metric = None
        for deployment in deployment_metrics['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment

        self.assertIsNotNone(current_deployment_metric,
                             msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        deployment_metrics_deployment_uid = self.ai_client.data_mart.get_deployment_metrics(
            deployment_uid=self.deployment_uid)
        print("-> get_deployment_metrics(deployment_uid={})\n{}".format(self.deployment_uid,
                                                                        deployment_metrics_deployment_uid))
        current_deployment_metric = None
        for deployment in deployment_metrics_deployment_uid['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment
        self.assertGreater(len(deployment_metrics_deployment_uid['deployment_metrics']), 0)
        self.assertIsNotNone(current_deployment_metric,
                             msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        deployment_metrics_subscription_uid = self.ai_client.data_mart.get_deployment_metrics(
            subscription_uid=self.subscription.uid)
        print("-> get_deployment_metrics(subscription_uid={})\n{}".format(self.subscription.uid,
                                                                          deployment_metrics_subscription_uid))
        current_deployment_metric = None
        for deployment in deployment_metrics_subscription_uid['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment
        self.assertGreater(len(deployment_metrics_subscription_uid['deployment_metrics']), 0)
        self.assertIsNotNone(current_deployment_metric,
                             msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

        deployment_metrics_asset_uid = self.ai_client.data_mart.get_deployment_metrics(
            asset_uid=self.subscription.source_uid)
        print("-> get_deployment_metrics(asset_uid={})\n{}".format(self.subscription.source_uid,
                                                                   deployment_metrics_asset_uid))
        current_deployment_metric = None
        for deployment in deployment_metrics_asset_uid['deployment_metrics']:
            if deployment['deployment']['deployment_id'] == self.deployment_uid:
                current_deployment_metric = deployment
        self.assertGreater(len(deployment_metrics_asset_uid['deployment_metrics']), 0)
        self.assertIsNotNone(current_deployment_metric,
                             msg="List of performance deployment metrics does not contain used deployment.")
        self.assertGreater(len(current_deployment_metric['metrics']), 0)
        self.assertEqual(last_metric['value'], current_deployment_metric['metrics'][0]['value'])
        self.assertEqual(current_deployment_metric['metrics'][0]['metric_type'], "performance")

    def test_19_disable_payload_logging_and_performance_monitoring(self):
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()

        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        for configuration in subscription_details['entity']['configurations']:
            if configuration['type'] == 'payload_logging' or configuration['type'] == 'performance_monitoring':
                self.assertFalse(configuration['enabled'])

    def test_20_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_21_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
