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
import requests
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *
from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType
from ibm_ai_openscale.supporting_classes import PayloadRecord


class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    binding_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    subscription = None
    test_uid = str(uuid.uuid4())
    source_uid = None
    transaction_id = None

    # Azure configuration
    credentials = {
        "client_id": "29f007c5-4c45-4210-8a88-9a40136f0ddd",
        "client_secret": "e4d8b0fa-73f7-4b77-83a7-0b424d92940f",
        "subscription_id": "744bca72-2299-451c-b682-ed6fb75fb671",
        "tenant": "fcf67057-50c9-4ad4-98f3-ffca64add9e9"
    }

    def score(self, subscription_details):
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        data = {
            "Inputs": {
                "input1":
                    [
                        {
                            'GENDER': "F",
                            'AGE': 27,
                            'MARITAL_STATUS': "Single",
                            'PROFESSION': "Professional",
                            'PRODUCT_LINE': "Personal Accessories",
                        }
                    ],
            },
            "GlobalParameters": {
            }
        }

        body = str.encode(json.dumps(data))

        token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
        headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
        headers['Authorization'] = ('Bearer ' + token)

        start_time = time.time()
        response = requests.post(url=scoring_url, data=body, headers=headers)
        response_time = time.time() - start_time
        result = response.json()

        request = {'fields': list(data['Inputs']['input1'][0]),
                   'values': [list(x.values()) for x in data['Inputs']['input1']]}

        response = {'fields': list(result['Results']['output1'][0]),
                    'values': [list(x.values()) for x in result['Results']['output1']]}

        return request, response, response_time

    @classmethod
    def setUpClass(cls):
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

    def test_02_bind_azure(self):
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("Azure ml engine", AzureMachineLearningInstance(self.credentials))

    def test_03_get_binding_details(self):
        print("Binding details: {}".format(self.ai_client.data_mart.bindings.get_details(self.binding_uid)))
        self.ai_client.data_mart.bindings.list()

    def test_04_get_assets(self):
        assets_uids = self.ai_client.data_mart.bindings.get_asset_uids()
        print("Assets uids: {}".format(assets_uids))
        self.assertGreater(len(assets_uids), 1)

        self.ai_client.data_mart.bindings.list_assets()
        asset_details = self.ai_client.data_mart.bindings.get_asset_details()
        print("Assets details: ".format(asset_details))

        for detail in asset_details:
            if 'ProductLineClass.2018.11.2.11.40.22.845' in detail['name']:
                TestAIOpenScaleClient.source_uid = detail['source_uid']

        self.assertIsNotNone(self.source_uid)

    def test_05_subscribe_azure_asset(self):
        subscription = self.ai_client.data_mart.subscriptions.add(
            AzureMachineLearningAsset(source_uid=self.source_uid,
                                      binding_uid=self.binding_uid,
                                      input_data_type=InputDataType.STRUCTURED,
                                      problem_type=ProblemType.MULTICLASS_CLASSIFICATION,
                                      label_column='PRODUCT_LINE',
                                      prediction_column='Scored Labels'))

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print('Subscription details: ' + str(subscription.get_details()))

    def test_06_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.subscription_uid)
        print('Subscription details: ' + str(TestAIOpenScaleClient.subscription.get_details()))

    def test_07_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_08_setup_payload_logging(self):
        TestAIOpenScaleClient.subscription.payload_logging.enable()

    def test_09_get_payload_logging_details(self):
        payload_logging_details = TestAIOpenScaleClient.subscription.payload_logging.get_details()
        print('Payload logging details: ' + str(payload_logging_details))

    def test_10_score_model_and_log_payload(self):
        subscription_details = self.subscription.get_details()

        request, response, response_time = self.score(subscription_details)

        records_list = []

        for i in range(0, 10):
            records_list.append(PayloadRecord(request=request, response=response, response_time=int(response_time)))

        self.subscription.payload_logging.store(records=records_list)

        time.sleep(30)

    def test_11_stats_on_payload_logging_table(self):
        TestAIOpenScaleClient.subscription.payload_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.payload_logging.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.payload_logging.get_table_content()

        payload_table_content = self.subscription.payload_logging.get_table_content(format='python')

        print('XXX' + str(payload_table_content))
        self.assertTrue('Scored Probabilities' in str(payload_table_content))

        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_12_setup_quality_monitoring(self):
        # problem_type should be read from subscription details
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(threshold=0.8,
                                                                     min_records=5)

    def test_13_get_quality_monitoring_details(self):
        print(str(TestAIOpenScaleClient.subscription.quality_monitoring.get_details()))
        TestAIOpenScaleClient.subscription.quality_monitoring.get_details()

    def test_14_send_feedback_data(self):
        feedback_records = []

        fields = ["GENDER", "AGE", "MARITAL_STATUS", "PROFESSION", "PRODUCT_LINE"]

        for i in range(1, 10):
            feedback_records.append(["F", "27", "Single", "Professional", "Personal Accessories"])

        self.subscription.feedback_logging.store(feedback_records, fields=fields)
        time.sleep(10)

    def test_15_stats_on_feedback_logging_table(self):
        pandas_df = TestAIOpenScaleClient.subscription.feedback_logging.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()
        TestAIOpenScaleClient.subscription.feedback_logging.get_table_content()
        feedback_logging = TestAIOpenScaleClient.subscription.feedback_logging.get_table_content(format='python')
        self.assertTrue(len(feedback_logging['values']) > 0)

    def test_16_run_quality_monitor(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        print("Run details: {}".format(run_details))
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
            print("Run details: {}".format(run_details))
            self.assertNotIn('failed', status, msg="Quality run failed.")

        self.assertTrue('completed' in status)

    def test_17_stats_on_quality_monitoring_table(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table(limit=None)
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_18_disable_quality_monitoring(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.disable()

    def test_19_disable_payload_logging(self):
        TestAIOpenScaleClient.subscription.payload_logging.disable()

    def test_20_get_metrics(self):
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(metric_type='quality'))

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
