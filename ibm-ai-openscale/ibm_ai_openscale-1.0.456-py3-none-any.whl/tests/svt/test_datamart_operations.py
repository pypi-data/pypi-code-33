# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import unittest

from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from preparation_and_cleaning import *
from models.spark import GoSales


class TestAIOpenScaleClient(unittest.TestCase):
    binding_uid = None
    deployment_uid = None
    model_uid = None
    aios_model_uid = None
    scoring_url = None
    labels = None
    ai_client = None
    wml_client = None
    subscription = None
    test_uid = str(uuid.uuid4())

    model = GoSales()

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

    def test_02_delete_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.delete()
        delete_schema(self.database_credentials, self.schema)
        create_schema(self.database_credentials, self.schema)

    def test_03_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_04_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))
        self.assertIsNotNone(self.binding_uid)

    def test_05_unbind(self):
        TestAIOpenScaleClient.ai_client.data_mart.bindings.delete(TestAIOpenScaleClient.binding_uid)
        TestAIOpenScaleClient.binding_uid = None

    def test_06_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML second instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML second instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))
        self.assertIsNotNone(self.binding_uid)

    def test_07_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        print("Binding id: {}".format(binding_uid))
        self.assertEqual(binding_uid, TestAIOpenScaleClient.binding_uid)

        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)
        self.assertIsNotNone(TestAIOpenScaleClient.wml_client)

    def test_08_prepare_deployment(self):
        TestAIOpenScaleClient.model_uid, TestAIOpenScaleClient.deployment_uid = self.model.deploy_to_wml(self.wml_client)

        print("Model id: {}".format(self.model_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_09_subscribe(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = TestAIOpenScaleClient.subscription.uid

    def test_10_unsubscribe(self):
        TestAIOpenScaleClient.ai_client.data_mart.subscriptions.delete(TestAIOpenScaleClient.aios_model_uid)

    def test_11_subscribe(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.aios_model_uid = TestAIOpenScaleClient.subscription.uid

    def test_12_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_13_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_14_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
