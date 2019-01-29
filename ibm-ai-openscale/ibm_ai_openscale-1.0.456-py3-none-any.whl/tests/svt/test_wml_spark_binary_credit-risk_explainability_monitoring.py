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
import pandas as pd
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType
from preparation_and_cleaning import *
from deployments.wml.spark import GermanCreditRisk
from ibm_ai_openscale.utils.training_stats import TrainingStats


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
    transaction_id = None

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

    def test_05_prepare_model(self):
        TestAIOpenScaleClient.deployment.publish_to_wml(self.wml_client, delete_existing=True)
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

    def test_09_score(self):

        TestAIOpenScaleClient.transaction_id = str(uuid.uuid4()).replace("-", "")
        print("Transaction id: {}".format(TestAIOpenScaleClient.transaction_id))

        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = self.deployment.get_scoring_payload()

        for i in range(0, 10):
            scorings = self.wml_client.deployments.score(scoring_endpoint, payload_scoring, transaction_id=TestAIOpenScaleClient.transaction_id)
            print("Score: {}".format(scorings))
            self.assertIsNotNone(scorings)

        print("Waiting 20 seconds for payload propagation...")
        time.sleep(20)

    def test_10_stats_on_payload_logging_table(self):

        TestAIOpenScaleClient.subscription.payload_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.payload_logging.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.payload_logging.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_11_setup_explainability(self):
        # training_distribution_german_risk.json

        data_df = pd.read_csv(
            "./datasets/German_credit_risk/credit_risk_training.csv",
            dtype={'LoanDuration': int, 'LoanAmount': int, 'InstallmentPercent': int, 'CurrentResidenceDuration': int,
                   'Age': int, 'ExistingCreditsCount': int, 'Dependents': int}
        )

        TestAIOpenScaleClient.subscription.explainability.enable(
            training_data_statistics=TrainingStats(
                data_df,
                {
                    "model_type": ProblemType.BINARY_CLASSIFICATION,
                    "class_label": 'Risk',
                    "feature_columns": ['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose', 'LoanAmount',
                                        'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent', 'Sex',
                                        'OthersOnLoan', 'CurrentResidenceDuration', 'OwnsProperty', 'Age',
                                        'InstallmentPlans', 'Housing', 'ExistingCreditsCount', 'Job', 'Dependents',
                                        'Telephone', 'ForeignWorker'],
                    "categorical_columns": ['CheckingStatus', 'CreditHistory', 'LoanPurpose', 'ExistingSavings',
                                            'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty',
                                            'InstallmentPlans', 'Housing', 'Job', 'Telephone', 'ForeignWorker']
                }
            ).get_training_statistics()
        )

    def test_12_get_details(self):
        details = TestAIOpenScaleClient.subscription.explainability.get_details()
        print("Explainability details: {}".format(details))

    def test_13_score(self):

        TestAIOpenScaleClient.transaction_id = str(uuid.uuid4()).replace("-", "")
        print("Transaction id: {}".format(TestAIOpenScaleClient.transaction_id))

        deployment_details = self.wml_client.deployments.get_details(TestAIOpenScaleClient.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        payload_scoring = self.deployment.get_scoring_payload()

        scorings = self.wml_client.deployments.score(scoring_endpoint, payload_scoring, transaction_id=TestAIOpenScaleClient.transaction_id)
        print("Score: {}".format(scorings))
        self.assertIsNotNone(scorings)

        print("Waiting 20 seconds for payload propagation...")
        time.sleep(20)

    def test_14_run_explainability(self):
        explainability_run = TestAIOpenScaleClient.subscription.explainability.run(
            transaction_id="{}-1".format(TestAIOpenScaleClient.transaction_id),
            background_mode=False
        )
        print("Run: {}".format(explainability_run))
        TestAIOpenScaleClient.status = explainability_run['entity']['status']
        print("Status: {}".format(TestAIOpenScaleClient.status))
        self.assertTrue(TestAIOpenScaleClient.status == "finished")

    def test_15_print_explainability_table_schema(self):
        TestAIOpenScaleClient.subscription.explainability.print_table_schema()

    def test_16_stats_on_explainability_table(self):
        TestAIOpenScaleClient.subscription.explainability.show_table()
        TestAIOpenScaleClient.subscription.explainability.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.explainability.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_17_disable_explainability(self):
        TestAIOpenScaleClient.subscription.explainability.disable()

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
