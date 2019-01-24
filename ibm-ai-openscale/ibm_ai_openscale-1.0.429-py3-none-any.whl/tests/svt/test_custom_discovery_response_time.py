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

    custom_deployments = []
    custom_models = []
    custom_deployments_time = 0
    client_deployments = []
    client_deployments_time = 0
    restapi_deployments = []
    restapi_deployments_time = 0

    # in secs
    client_baseline = 2
    rest_api_baseline = 2
    correction = 0

    # Custom deployment configuration
    credentials = {
        "url": "http://169.63.194.147:31520",
        "username": "xxx",
        "password": "yyy",
        "request_headers": {"content-type": "application/json"}
    }

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

        cls.ai_client.data_mart.setup(db_credentials=cls.database_credentials, schema=cls.schema)
        TestAIOpenScaleClient.binding_uid = cls.ai_client.data_mart.bindings.add("My Custom deployment", CustomMachineLearningInstance(cls.credentials))

    def test_01_get_deployments_from_custom_and_calculate_correction(self):
        response = requests.get(url="{}/v1/deployments".format(self.credentials['url']))

        deployments = response.json()
        for deployment in deployments['resources']:
            TestAIOpenScaleClient.custom_deployments.append(deployment['entity']['name'])
            if deployment['entity']['asset']['name'] not in self.custom_models:
                TestAIOpenScaleClient.custom_models.append(deployment['entity']['asset']['name'])

    def test_02_validate_client_response_time(self):
        start_time = time.time()
        asset_details = self.ai_client.data_mart.bindings.get_asset_details()

        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.client_baseline + self.correction, duration))
        self.assertLess(duration, self.client_baseline + self.correction)
        self.assertEqual(len(asset_details), len(self.custom_models))

        endpoints_name_client = []
        for detail in asset_details:
            endpoints_name_client.append(detail['name'])

        for model in self.custom_models:
            self.assertIn(model, endpoints_name_client)

    def test_03_validate_rest_api_response_time(self):
        start_time = time.time()
        response = requests.get(
            self.ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=self.binding_uid),
            headers=self.ai_client._get_headers())
        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.rest_api_baseline + self.correction, duration))
        self.assertLess(duration, self.rest_api_baseline + self.correction)
        self.assertEqual(response.json()['count'], len(self.custom_deployments))

        endpoints_name_rest = []
        for resource in response.json()['resources']:
            endpoints_name_rest.append(resource['entity']['name'])

        for deployment in self.custom_deployments:
            self.assertIn(deployment, endpoints_name_rest)

    @classmethod
    def tearDownClass(cls):
        print("Deleting binding.")
        cls.ai_client.data_mart.bindings.delete(cls.binding_uid)

        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
