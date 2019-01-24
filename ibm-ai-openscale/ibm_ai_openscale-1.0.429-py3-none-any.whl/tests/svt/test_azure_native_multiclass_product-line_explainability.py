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
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *
from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType


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

        return request, response, int(response_time)

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
        print('Binding details: :' + str(TestAIOpenScaleClient.ai_client.data_mart.bindings.get_details(TestAIOpenScaleClient.binding_uid)))
        TestAIOpenScaleClient.ai_client.data_mart.bindings.list()

    def test_04_get_assets(self):
        assets_uids = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_asset_uids()
        self.assertGreater(len(assets_uids), 1)
        print('Assets uids: ' + str(assets_uids))

        TestAIOpenScaleClient.ai_client.data_mart.bindings.list_assets()
        asset_details = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_asset_details()
        print('Assets details: ' + str(asset_details))

        for detail in asset_details:
            if 'ProductLineClass.2018.11.2.11.40.22.845' in detail['name']:
                TestAIOpenScaleClient.source_uid = detail['source_uid']

        self.assertIsNotNone(TestAIOpenScaleClient.source_uid)

    def test_05_subscribe_azure_asset(self):
        with open('assets/training_distribution_product_line.json') as json_file:
            training_data_statistics = json.load(json_file)

        self.assertIsNotNone(training_data_statistics)

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            AzureMachineLearningAsset(source_uid=TestAIOpenScaleClient.source_uid,
                                      binding_uid=TestAIOpenScaleClient.binding_uid,
                                      input_data_type=InputDataType.STRUCTURED,
                                      problem_type=ProblemType.MULTICLASS_CLASSIFICATION,
                                      label_column='PRODUCT_LINE',
                                      prediction_column='Scored Labels',
                                      feature_columns=['GENDER', 'AGE', 'MARITAL_STATUS', 'PROFESSION'],
                                      categorical_columns=['GENDER', 'MARITAL_STATUS', 'PROFESSION'],
                                      training_data_statistics=training_data_statistics
                                      ))

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
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        request, response, response_time = self.score(subscription_details)

        records_list = [PayloadRecord(request=request, response=response, response_time=int(response_time)),
                        PayloadRecord(request=request, response=response, response_time=int(response_time))]

        TestAIOpenScaleClient.subscription.payload_logging.store(records=records_list)
        time.sleep(20)

    def test_11_stats_on_payload_logging_table(self):
        payload_table_content = TestAIOpenScaleClient.subscription.payload_logging.get_table_content(format='python')
        self.assertTrue('Scored Probabilities' in str(payload_table_content))

        TestAIOpenScaleClient.subscription.payload_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.payload_logging.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.payload_logging.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_12_setup_explainability(self):
        TestAIOpenScaleClient.subscription.explainability.enable()

    def test_13_get_details(self):
        details = TestAIOpenScaleClient.subscription.explainability.get_details()
        print("Explainability details: {}".format(details))

    def test_14_score(self):
        TestAIOpenScaleClient.transaction_id = str(uuid.uuid4()).replace("-", "")
        TestAIOpenScaleClient.transaction_id_2 = str(uuid.uuid4()).replace("-", "")

        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        request, response, response_time = self.score(subscription_details)

        TestAIOpenScaleClient.subscription.payload_logging.store(
            records=[PayloadRecord(
                scoring_id=TestAIOpenScaleClient.transaction_id,
                request=request,
                response=response,
                response_time=response_time
            )]
        )
        time.sleep(30)

    def test_15_run_explainability(self):
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.status = TestAIOpenScaleClient.subscription.explainability.run(
            transaction_id="{}-1".format(TestAIOpenScaleClient.transaction_id),
            background_mode=False
        )['entity']['status']
        print("Status: {}".format(TestAIOpenScaleClient.status))
        self.assertTrue(TestAIOpenScaleClient.status == "finished")

    def test_16_print_explainability_table_schema(self):
        TestAIOpenScaleClient.subscription.explainability.print_table_schema()

    def test_17_stats_on_explainability_table(self):
        TestAIOpenScaleClient.subscription.explainability.show_table()
        TestAIOpenScaleClient.subscription.explainability.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.explainability.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_18_disable_explainability(self):
        TestAIOpenScaleClient.subscription.explainability.disable()

    def test_19_get_metrics(self):
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
