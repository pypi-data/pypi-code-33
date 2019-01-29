# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest

from ibm_ai_openscale import APIClient
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *
from models.spark import GoSales


@unittest.skipIf("ICP" in get_env(), "No internal postgres on ICP")
class TestAIOpenScaleClient(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    aios_model_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    subscription = None
    binding_uid = None
    test_uid = str(uuid.uuid4())

    model = GoSales()

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        cls.ai_client = APIClient(cls.aios_credentials)
        cls.wml_credentials = get_wml_credentials()

        prepare_env(cls.ai_client, internal=True)

    def test_01_create_client(self):
        TestAIOpenScaleClient.ai_client = APIClient(self.aios_credentials)

    def test_02_setup_data_mart_with_internal_db(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(internal_db=True)
        dm_details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        self.assertTrue('internal' in str(dm_details))
        print(str(dm_details))

    def test_03_check_if_db_credentials_are_hidden(self):
        dm_details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        print(dm_details)

        self.assertTrue(dm_details['database_configuration'] == {})

    def test_04_data_mart_get_details(self):
        details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        print(details)
        self.assertTrue(len(json.dumps(details)) > 10)

    def test_05_bind_wml_instance_and_get_wml_client(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.add("My WML instance", WatsonMachineLearningInstance(self.wml_credentials))

    def test_06_get_wml_client(self):
        TestAIOpenScaleClient.binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(self.binding_uid)

    def test_07_list_instances(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.list()

    def test_08_get_uids(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()

    def test_09_get_details(self):
        print("Details: {}".format(TestAIOpenScaleClient.ai_client.data_mart.bindings.get_details()))

    def test_10_prepare_deployment(self):
        TestAIOpenScaleClient.model_uid, TestAIOpenScaleClient.deployment_uid = self.model.deploy_to_wml(
            self.wml_client)

        print("Model id: {}".format(self.model_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_11_list_subscriptions(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.list()

    def test_12_subscribe(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = subscription.uid

    def test_13_list_and_get_uids_after_subscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.list()
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.list(name="AIOS Spark GoSales model")
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get_uids()

    def test_14_check_if_deployments_were_added(self):
        sub_details = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get_details()
        self.assertTrue(len(sub_details['subscriptions'][0]['entity']['deployments']) > 0)
        self.assertTrue('uri' not in str(sub_details))

    def test_15_list_models_and_functions(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.list_assets()
        TestAIOpenScaleClient.ai_client.data_mart.bindings.list_assets(is_subscribed=True)

    def test_16_get_asset_uids(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.get_asset_uids()

    def test_17_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.aios_model_uid)
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(source_uid=TestAIOpenScaleClient.model_uid)
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(name=self.model.model_name, choose='random')
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(name=self.model.model_name, choose='first')
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(name=self.model.model_name, choose='last')
        TestAIOpenScaleClient.subscription.get_details()

    def test_18_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_19_get_metrics(self):
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(metric_type='quality'))

    def test_21_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_22_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
