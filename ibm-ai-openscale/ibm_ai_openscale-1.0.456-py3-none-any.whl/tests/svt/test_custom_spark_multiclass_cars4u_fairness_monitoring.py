# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest
import requests
import time
from preparation_and_cleaning import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.payload_record import PayloadRecord


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

    # Custom deployment configuration
    credentials = {
        "url": "http://169.63.194.147:31520",
        "username": "xxx",
        "password": "yyy",
        "request_headers": {"content-type": "application/json"}
    }

    def score(self, subscription_details):
        payload = {'fields': ['ID','Gender','Status','Children','Age','Customer_Status','Car_Owner','Customer_Service','Business_Area','Satisfaction'],
                   'values': [
                       [3785,'Male','S',1,27,'Inactive','Yes','The car should have been brought to us instead of us trying to find it in the lot.','Product: Information',0],
                       [3786, 'Female', 'M', 2, 52, 'Inactive', 'Yes', 'The car should have been brought to us instead of us trying to find it in the lot.', 'Product: Information', 0]]}

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer xxx'}
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        response = requests.post(scoring_url, json=payload, headers=header)

        return payload, response.json(), 25

    @classmethod
    def setUpClass(cls):
        try:
            requests.get(url="{}/v1/deployments".format(cls.credentials['url']), timeout=10)
        except:
            raise unittest.SkipTest("Custom app is not available.")

        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)

        prepare_env(cls.ai_client)

    def test_01_setup_data_mart(self):
        self.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_02_bind_custom(self):
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("My Custom deployment",CustomMachineLearningInstance(self.credentials))
        print("Binding uid: {}".format(self.binding_uid))
        self.assertIsNotNone(self.binding_uid)

    def test_03_get_binding_details(self):
        binding_details = self.ai_client.data_mart.bindings.get_details()
        print("Binding details: {}".format(binding_details))
        self.assertIsNotNone(binding_details)

    def test_04_get_deployments(self):
        print('Available deployments: {}'.format(self.ai_client.data_mart.bindings.list_assets()))
        self.ai_client.data_mart.bindings.list_assets()
        self.ai_client.data_mart.bindings.get_asset_details()

    def test_05_subscribe_custom(self):
        from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType

        subscription = self.ai_client.data_mart.subscriptions.add(
            CustomMachineLearningAsset(
                source_uid='action',
                binding_uid=self.binding_uid,
                prediction_column='predictedActionLabel',
                probability_column='probability'))

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print("Subscription id: {}".format(self.subscription_uid))
        self.assertIsNotNone(self.subscription_uid)

    def test_06_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

    def test_07_list_deployments(self):
        print("Listing deployments:\n")
        self.subscription.list_deployments()

    def test_10_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        print("Payload logging details:\n{}".format(payload_logging_details))
        self.assertIsNotNone(payload_logging_details)

    def test_11_score_model_and_log_payload(self):
        request, response, response_time = self.score(self.subscription.get_details())

        records_list = []

        for i in range(0, 10):
            records_list.append(PayloadRecord(request=request, response=response, response_time=response_time))

        self.subscription.payload_logging.store(records=records_list)

        print("Waiting 30 seconds for propagation...")
        time.sleep(30)

    def test_12_stats_on_payload_logging_table(self):
        print("Print table schema:")
        self.subscription.payload_logging.print_table_schema()
        print("Show table:")
        self.subscription.payload_logging.show_table()
        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        self.assertIsNotNone(python_table_content)

        if self.scoring_result is not None and 'fields' in self.scoring_result.keys():
            if 'prediction' in self.scoring_result['fields']:
                self.assertIn('prediction', python_table_content['fields'])

            if 'probability' in self.scoring_result['fields']:
                self.assertIn('probability', python_table_content['fields'])

    def test_13_setup_fairness_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Feature

        print('Subscription details after payload logging: ' + str(self.subscription.get_details()))

        with open('assets/training_distribution_cars_4_you.json') as json_file:
            training_data_statistics = json.load(json_file)

        self.assertIsNotNone(training_data_statistics)

        TestAIOpenScaleClient.subscription.fairness_monitoring.enable(
            features=[
                Feature("Age", [[20, 50], [60, 70]], [[51, 59]], 0.8)
            ],
            favourable_classes=["Free Upgrade"],
            unfavourable_classes=["Voucher"],
            min_records=4,
            training_data_statistics=training_data_statistics
        )

    def test_14_get_fairness_monitoring_details(self):
        print(TestAIOpenScaleClient.subscription.fairness_monitoring.get_details())

    def test_15_run(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.run(background_mode=False)

    def test_16_stats_on_fairness_monitoring_table(self):
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.fairness_monitoring.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)
        print(TestAIOpenScaleClient.subscription.payload_logging.get_table_content(format='python'))
        print(TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content(format='python'))

    def test_17_disable_fairness_monitoring(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.disable()

    def test_18_get_metrics(self):
        deployment_metrics = self.ai_client.data_mart.get_deployment_metrics()
        deployment_metrics_deployment_uid = self.ai_client.data_mart.get_deployment_metrics(deployment_uid=self.deployment_uid)
        deployment_metrics_subscription_uid = self.ai_client.data_mart.get_deployment_metrics(subscription_uid=self.subscription.uid)
        deployment_metrics_asset_uid = self.ai_client.data_mart.get_deployment_metrics(asset_uid=self.subscription.source_uid)

        print(deployment_metrics)
        print(deployment_metrics_deployment_uid)
        print(deployment_metrics_subscription_uid)
        print(deployment_metrics_asset_uid)

        self.assertGreater(len(deployment_metrics['deployment_metrics']), 0)
        self.assertGreater(len(deployment_metrics_deployment_uid['deployment_metrics']), 0)
        self.assertGreater(len(deployment_metrics_subscription_uid['deployment_metrics']), 0)
        self.assertGreater(len(deployment_metrics_asset_uid['deployment_metrics']), 0)

        performance_metrics_asset_uid = self.ai_client.data_mart.get_deployment_metrics(metric_type='performance')
        print(performance_metrics_asset_uid)
        self.assertGreater(len(performance_metrics_asset_uid['deployment_metrics'][0]['metrics']), 0)

    def test_19_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_20_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
