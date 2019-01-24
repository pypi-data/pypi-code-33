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
from ibm_ai_openscale.supporting_classes import *
from models import SparkBestHeartDrug
from preparation_and_cleaning import *


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
        model_data = SparkBestHeartDrug.get_model_data()

        model_name = "AIOS Spark Best Drug model"
        deployment_name = "AIOS Spark Best Drug deployment"

        training_data_reference = {
            "name": "DRUG feedback",
            "connection": self.db2_credentials,
            "source": {
                "tablename": "DRUG_TRAIN_DATA",
                "type": "dashdb"
            }
        }

        meta_props = {
            self.wml_client.repository.ModelMetaNames.NAME: "{}".format(model_name),
            self.wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: training_data_reference,
            self.wml_client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA: model_data['output_data_schema'].jsonValue(),
            self.wml_client.repository.ModelMetaNames.EVALUATION_METHOD: "multiclass",
            self.wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                {
                    "name": "accuracy",
                    "value": 0.870968,
                    "threshold": 0.8
                }
            ]
        }

        wml_models = self.wml_client.repository.get_details()

        for model in wml_models['models']['resources']:
            if model_name == model['entity']['name']:
                TestAIOpenScaleClient.model_uid = model['metadata']['guid']
                break

        if self.model_uid is None:
            print("Storing model ...")

            published_model_details = self.wml_client.repository.store_model(model=model_data['model'], meta_props=meta_props, training_data=model_data['training_data'], pipeline=model_data['pipeline'])
            TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        wml_deployments = self.wml_client.deployments.get_details()

        for deployment in wml_deployments['resources']:
            if deployment_name == deployment['entity']['name']:
                TestAIOpenScaleClient.deployment_uid = deployment['metadata']['guid']
                break

        if self.deployment_uid is None:
            print("Deploying model...")

            deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name,
                                                            asynchronous=False)
            TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        print("Model id: {}".format(self.model_uid))
        print("Deployment id: {}".format(self.deployment_uid))

    def test_06_subscribe(self):
        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(TestAIOpenScaleClient.model_uid))
        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print("Subscription id: {}".format(TestAIOpenScaleClient.subscription_uid))

    def test_07_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.subscription_uid)

    def test_08_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()

    def test_09_setup_payload_logging(self):
        TestAIOpenScaleClient.subscription.payload_logging.enable()

    def test_10_setup_fairness_monitoring(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.enable(
            features=[
                Feature("AGE", majority=[[20,50],[60,70]], minority=[[51,59]], threshold=0.8)
            ],
            prediction_column='predictedLabel',
            favourable_classes=['drugY'],
            unfavourable_classes=['drugA', 'drugB', 'drugC'],
            min_records=12
        )

    def test_11_score(self):
        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)
        payload_scoring = SparkBestHeartDrug.get_scoring_payload_from_training_data()

        for i in range(0, 30):
            self.wml_client.deployments.score(scoring_endpoint, payload_scoring)

        print('Scoring result: {}'.format(self.wml_client.deployments.score(scoring_endpoint, payload_scoring)))
        print("Waiting for fairness propagation...")
        time.sleep(60)

    def test_12_run(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.run()
        time.sleep(60)

    def test_13_get_fairness_monitoring_details(self):
        print('Fairness monitoring details: {}'.format(TestAIOpenScaleClient.subscription.fairness_monitoring.get_details()))

    def test_14_stats_on_fairness_and_payload_monitoring_tables(self):
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.fairness_monitoring.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.describe_table()

        pandas_df_fairness = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content()
        print(TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content(format='python'))
        print(str(pandas_df_fairness))

        pandas_df_payload = TestAIOpenScaleClient.subscription.payload_logging.get_table_content()
        print(str(pandas_df_payload))
        print(TestAIOpenScaleClient.subscription.payload_logging.get_table_content(format='python'))

        self.assertTrue(pandas_df_fairness.size > 1)
        self.assertTrue(pandas_df_payload.size > 1)

    def test_15_disable_fairness_monitoring(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.disable()

    def test_16_disable_payload_logging(self):
        TestAIOpenScaleClient.subscription.payload_logging.disable()

    def test_17_get_metrics(self):
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type=MetricTypes.FAIRNESS_MONITORING))
        print(TestAIOpenScaleClient.subscription.fairness_monitoring.get_metrics(TestAIOpenScaleClient.deployment_uid))

        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics()['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid)['deployment_metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid, metric_type=MetricTypes.FAIRNESS_MONITORING)['deployment_metrics'][0]['metrics']) > 0)
        self.assertTrue(len(TestAIOpenScaleClient.subscription.fairness_monitoring.get_metrics(TestAIOpenScaleClient.deployment_uid)['metrics']) > 0)

    def test_18_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_19_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
