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
from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType
from preparation_and_cleaning import *
from deployments.wml.spark import GermanCreditRisk


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
    fairness_enabled = False

    test_uid = str(uuid.uuid4())

    deployment = GermanCreditRisk()

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()
        cls.db2_credentials = get_db2_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)
            cls.wml_credentials = get_wml_credentials()

        if 'postgres' in cls.database_credentials['uri']:
            upload_german_risk_training_data_to_postgres(cls.database_credentials)

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
        TestAIOpenScaleClient.ai_client.data_mart.bindings.list_asset_deployments()

    def test_05_prepare_model(self):
        TestAIOpenScaleClient.deployment.publish_to_wml(self.wml_client)
        TestAIOpenScaleClient.model_uid = TestAIOpenScaleClient.deployment.asset_uid
        TestAIOpenScaleClient.deployment_uid = TestAIOpenScaleClient.deployment.deployment_uid

    def test_06_subscribe(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(
            TestAIOpenScaleClient.model_uid,
            problem_type=ProblemType.BINARY_CLASSIFICATION,
            input_data_type=InputDataType.STRUCTURED,
            label_column='Risk',
            prediction_column='predictedLabel',
            probability_column='probability'
        ))

        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_07_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.aios_model_uid)

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()
        TestAIOpenScaleClient.ai_client.data_mart.bindings.list_asset_deployments()

    def test_09_get_payload_logging_details(self):
        payload_logging_details = TestAIOpenScaleClient.subscription.payload_logging.get_details()
        print(str(payload_logging_details))

    def test_10_score(self):
        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = self.deployment.get_scoring_payload()

        for i in range(0, 10):
            scorings = self.wml_client.deployments.score(scoring_endpoint, payload_scoring)
            print("Score: {}".format(scorings))
            self.assertIsNotNone(scorings)

        print("Waiting 20 seconds for payload propagation...")
        time.sleep(20)

    def test_11_stats_on_payload_logging_table(self):
        TestAIOpenScaleClient.subscription.payload_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.payload_logging.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.payload_logging.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_12_setup_fairness_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Feature

        with open('assets/training_distribution_german_risk.json') as json_file:
            training_data_statistics = json.load(json_file)

        try:
            TestAIOpenScaleClient.subscription.fairness_monitoring.enable(
                features=[
                    Feature("Sex", majority=['male'], minority=['female'], threshold=0.95),
                    Feature("Age", majority=[[26,75]], minority=[[18,25]], threshold=0.95)
                ],
                favourable_classes=['No Risk'],
                unfavourable_classes=['Risk'],
                min_records=4,
                training_data_statistics=training_data_statistics
            )
            TestAIOpenScaleClient.fairness_enabled = True
        except Exception as ex:
            print("Unable to set up fairness monitoring.")
            self.fail("Unable to set up fairness monitoring.")

    def test_13_get_fairness_monitoring_details(self):
        print(TestAIOpenScaleClient.subscription.fairness_monitoring.get_details())

    def test_14_run(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.run(background_mode=True)

        print("Waiting 2 minutes for bias calculation.")
        time.sleep(120)

    def test_15_stats_on_fairness_table(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.fairness_monitoring.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_16_get_metrics(self):
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='fairness'))
        print(TestAIOpenScaleClient.subscription.fairness_monitoring.get_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))

        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics()['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type='fairness')['deployment_metrics'][0]['metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.subscription.fairness_monitoring.get_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid)['metrics']) > 0)

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
