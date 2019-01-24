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
    azure_get_webervices = []
    azure_get_webervices_time = 0
    client_get_webervices = []
    client_get_webervices_time = 0
    restapi_get_webervices = []
    restapi_get_webervices_time = 0

    # in secs
    client_baseline = 55
    rest_api_baseline = 45
    correction = 0

    # Azure configuration

    azure_token_endpoint_template = "https://login.microsoftonline.com/{}/oauth2/token"
    azure_webservices_list_template = "https://management.azure.com/subscriptions/{}/providers/Microsoft.MachineLearning/webServices?api-version=2016-05-01-preview"
    azure_webservice_details_template = "https://management.azure.com{}?api-version=2016-05-01-preview"
    azure_webservice_api_keys_template = "https://management.azure.com{}/listKeys?api-version=2016-05-01-preview"

    credentials = {
        "client_id": "29f007c5-4c45-4210-8a88-9a40136f0ddd",
        "client_secret": "e4d8b0fa-73f7-4b77-83a7-0b424d92940f",
        "subscription_id": "744bca72-2299-451c-b682-ed6fb75fb671",
        "tenant": "fcf67057-50c9-4ad4-98f3-ffca64add9e9"
    }

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

        cls.ai_client.data_mart.setup(db_credentials=cls.database_credentials, schema=cls.schema)
        TestAIOpenScaleClient.binding_uid = cls.ai_client.data_mart.bindings.add("Azure ml engine", AzureMachineLearningInstance(cls.credentials))

    def test_01_get_webservices_from_azure_and_calculate_correction(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        azure_token_endpoint = self.azure_token_endpoint_template.format(self.credentials['tenant'])
        azure_deployments = []

        start_time = time.time()

        data = {"grant_type": "client_credentials",
                "client_id": "{}".format(self.credentials['client_id']),
                "client_secret": "{}".format(self.credentials['client_secret']),
                "resource": "https://management.azure.com/"}
        response = requests.post(url=azure_token_endpoint, headers=headers, data=data)

        headers = {"Authorization": "Bearer {}".format(response.json()['access_token'])}
        azure_webservices_list = self.azure_webservices_list_template.format(self.credentials['subscription_id'])
        response = requests.get(url=azure_webservices_list, headers=headers)

        for item in response.json()["value"]:
            response = requests.get(url=self.azure_webservice_details_template.format(item['id']), headers=headers)
            deployment = response.json()

            response = requests.get(url=self.azure_webservice_api_keys_template.format(item['id']), headers=headers)
            deployment['api_keys'] = response.json()

            response = requests.get(url="{}?api-version=2016-05-01-preview".format(item['properties']['swaggerLocation']), headers=headers)

            for key in response.json()['paths'].keys():
                if "execute" in key:
                    deployment['scoring_url'] = str(key).replace("&format=swagger", "")

            azure_deployments.append(deployment)

        duration = time.time() - start_time
        duration = int(duration)

        TestAIOpenScaleClient.correction = 0 if (duration - 85) < 0 else duration - 85
        TestAIOpenScaleClient.azure_get_webervices = azure_deployments
        TestAIOpenScaleClient.azure_get_webervices_time = duration

        print("Number of Azure deployments: {}".format(len(self.azure_get_webervices)))
        print("Baseline correction: {}".format(self.correction))

    def test_02_validate_client_response_time(self):
        start_time = time.time()
        asset_details = self.ai_client.data_mart.bindings.get_asset_details()
        duration = time.time() - start_time
        duration = int(duration)

        print(type(asset_details))
        print("Asset details: {}".format(asset_details))

        print("Baseline: {} secs, duration: {} secs".format(self.client_baseline + self.correction, duration))
        self.assertLess(duration, self.client_baseline + self.correction)
        self.assertEqual(len(asset_details), len(self.azure_get_webervices))

        webservices_name_client = []
        for detail in asset_details:
            webservices_name_client.append(detail['name'])

        for webservice in self.azure_get_webervices:
            self.assertIn(webservice['name'], webservices_name_client)

    def test_03_validate_rest_api_response_time(self):
        start_time = time.time()
        response = requests.get(self.ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=self.binding_uid), headers=self.ai_client._get_headers())
        duration = time.time() - start_time
        duration = int(duration)

        print("Baseline: {} secs, duration: {} secs".format(self.rest_api_baseline + self.correction, duration))
        self.assertLess(duration, self.rest_api_baseline + self.correction)
        self.assertEqual(response.json()['count'], len(self.azure_get_webervices))

        webservices_name_rest = []
        for resource in response.json()['resources']:
            webservices_name_rest.append(resource['entity']['name'])

        for webservice in self.azure_get_webervices:
            self.assertIn(webservice['name'], webservices_name_rest)

    @classmethod
    def tearDownClass(cls):
        print("Unbinding.")
        cls.ai_client.data_mart.bindings.delete(cls.binding_uid)

        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
