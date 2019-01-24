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
from models.function import Multiply


class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    function_uid = None
    subscription_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    binding_uid = None

    subscription = None
    test_uid = str(uuid.uuid4())

    model = Multiply()

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
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_prepare_deployment(self):
        TestAIOpenScaleClient.function_uid, TestAIOpenScaleClient.deployment_uid = self.model.deploy_to_wml(
            self.wml_client)

        print("Function id: {}".format(self.function_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_06_subscribe(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.function_uid, prediction_column='multiplication'))

    def test_07_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_09_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        for configuration in subscription_details['entity']['configurations']:
            if configuration['type'] == 'payload_logging' or configuration['type'] == 'performance_monitoring':
                self.assertEqual(configuration['enabled'], True)
            else:
                self.assertEqual(configuration['enabled'], False)

    def test_11_score(self):
        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = {"fields": ["x", "y"],
                           "values": [[2, 3], [3.1, 2.2]]}

        for i in range(0, 10):
            scorings = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)
            self.assertIsNotNone(scorings)
            print("Score result: {}".format(scorings))

        time.sleep(20)

    def test_12_stats_on_payload_logging_table(self):
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

        self.assertTrue(table_content.size > 1)
        self.assertIsNotNone(python_table_content)

    def test_13_stats_on_performance_monitoring_table(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.performance_monitoring.show_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content()
        performance_monitoring = TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content(format='python')
        self.assertTrue(len(performance_monitoring['values']) > 0)

    def test_14_setup_quality_monitoring(self):
        from ibm_ai_openscale.supporting_classes import ProblemType
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.8, min_records=5, problem_type=ProblemType.MULTICLASS_CLASSIFICATION)

    def test_15_get_quality_monitoring_details(self):
        print(str(TestAIOpenScaleClient.subscription.quality_monitoring.get_details()))
        TestAIOpenScaleClient.subscription.quality_monitoring.get_details()

    def test_16_send_feedback_data(self):
        feedback_records = []
        fields = ['x', 'y', 'label']

        for i in range(1, 10):
            feedback_records.append([3, 5, 15])

        self.subscription.feedback_logging.store(feedback_records, fields=fields)
        time.sleep(20)

    def test_17_stats_on_feedback_logging_table(self):
        pandas_df = TestAIOpenScaleClient.subscription.feedback_logging.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()
        TestAIOpenScaleClient.subscription.feedback_logging.get_table_content()
        feedback_logging = TestAIOpenScaleClient.subscription.feedback_logging.get_table_content(format='python')
        self.assertTrue(len(feedback_logging['values']) > 0)

    def test_18_run_quality_monitor(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        import time
        self.assertTrue('Prerequisite check' in str(run_details))

        status = run_details['status']
        id = run_details['id']
        start_time = time.time()
        elapsed_time = 0

        while status != 'completed' and elapsed_time < 60:
            time.sleep(10)
            run_details = TestAIOpenScaleClient.subscription.quality_monitoring.get_run_details(run_uid=id)
            status = run_details['status']
            elapsed_time = time.time() - start_time
            print("Details: {}".format(run_details))
            self.assertNotIn('failed', run_details)

        self.assertTrue('completed' in status)

    def test_19_stats_on_quality_monitoring_table(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table(limit=None)
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_20_disable_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.disable()

    def test_21_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.subscription.uid)

    def test_22_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
