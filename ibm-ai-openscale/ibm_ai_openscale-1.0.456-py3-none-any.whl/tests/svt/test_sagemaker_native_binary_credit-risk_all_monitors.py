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
import boto3
from preparation_and_cleaning import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes import PayloadRecord


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
    transaction_id = None

    test_uid = str(uuid.uuid4())

    # AWS configuration
    credentials = {
        "access_key_id": "AKIAI3LQITG4RLLSUIHA",
        "secret_access_key": "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",
        "region": "us-east-1"
    }

    def score(self, binding_details, subscription_details):
        access_id = binding_details['entity']['credentials']['access_key_id']
        access_key = binding_details['entity']['credentials']['secret_access_key']
        region = binding_details['entity']['credentials']['region']
        endpoint_name = subscription_details['entity']['deployments'][0]['name']

        runtime = boto3.client('sagemaker-runtime',
                               region_name=region,
                               aws_access_key_id=access_id,
                               aws_secret_access_key=access_key)

        fields = ['CheckingStatus_0_to_200', 'CheckingStatus_greater_200', 'CheckingStatus_less_0', 'CheckingStatus_no_checking', 'CreditHistory_all_credits_paid_back', 'CreditHistory_credits_paid_to_date', 'CreditHistory_no_credits', 'CreditHistory_outstanding_credit', 'CreditHistory_prior_payments_delayed', 'LoanPurpose_appliances', 'LoanPurpose_business', 'LoanPurpose_car_new', 'LoanPurpose_car_used', 'LoanPurpose_education', 'LoanPurpose_furniture', 'LoanPurpose_other', 'LoanPurpose_radio_tv', 'LoanPurpose_repairs', 'LoanPurpose_retraining', 'LoanPurpose_vacation', 'ExistingSavings_100_to_500', 'ExistingSavings_500_to_1000', 'ExistingSavings_greater_1000', 'ExistingSavings_less_100', 'ExistingSavings_unknown', 'EmploymentDuration_1_to_4', 'EmploymentDuration_4_to_7', 'EmploymentDuration_greater_7', 'EmploymentDuration_less_1', 'EmploymentDuration_unemployed', 'Sex_female', 'Sex_male', 'OthersOnLoan_co-applicant', 'OthersOnLoan_guarantor', 'OthersOnLoan_none', 'OwnsProperty_car_other', 'OwnsProperty_real_estate', 'OwnsProperty_savings_insurance', 'OwnsProperty_unknown', 'InstallmentPlans_bank', 'InstallmentPlans_none', 'InstallmentPlans_stores', 'Housing_free', 'Housing_own', 'Housing_rent', 'Job_management_self-employed', 'Job_skilled', 'Job_unemployed', 'Job_unskilled', 'Telephone_none', 'Telephone_yes', 'ForeignWorker_no', 'ForeignWorker_yes', 'LoanDuration', 'LoanAmount', 'InstallmentPercent', 'CurrentResidenceDuration', 'Age', 'ExistingCreditsCount', 'Dependents']
        payload = "0,0,1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,1,0,17,4850,3,3,31,1,1"

        print("Fields size: {}".format(len(fields)))

        start_time = time.time()
        response = runtime.invoke_endpoint(EndpointName=endpoint_name,
                                           ContentType='text/csv',
                                           Body=payload)
        response_time = time.time() - start_time
        result = json.loads(response['Body'].read().decode())

        values = []
        for v in payload.split('\n'):
            values.append([float(s) for s in v.split(',')])

        request = {'fields': fields, 'values': values}
        response = {
            'fields': list(result['predictions'][0]),
            'values': [list(x.values()) for x in result['predictions']]
        }

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

    def test_02_bind_sagemaker(self):
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("SageMaker ml engine", SageMakerMachineLearningInstance(self.credentials))
        print("Binding uid: {}".format(self.binding_uid))

    def test_03_get_binding_details(self):
        binding_details = self.ai_client.data_mart.bindings.get_details(self.binding_uid)
        print("Binding details: {}".format(binding_details))
        self.ai_client.data_mart.bindings.list()

    def test_04_get_assets(self):
        assets_uids = self.ai_client.data_mart.bindings.get_asset_uids()
        self.assertGreater(len(assets_uids), 1)
        print("Assets uids: {}".format(assets_uids))

        self.ai_client.data_mart.bindings.list_assets()
        asset_details = self.ai_client.data_mart.bindings.get_asset_details()
        print("Assets details: {}".format(asset_details))

        asset_name = ""
        for detail in asset_details:
            if 'Credit-risk-linear-learner' in detail['name']:
                asset_name = detail['name']
                TestAIOpenScaleClient.source_uid = detail['source_uid']

        print("asset name: {}".format(asset_name))
        print("asset uid: {}".format(self.source_uid))
        self.assertIsNotNone(TestAIOpenScaleClient.source_uid)

    def test_05_subscribe_sagemaker_asset(self):
        from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(
            SageMakerMachineLearningAsset(
                source_uid=TestAIOpenScaleClient.source_uid,
                binding_uid=TestAIOpenScaleClient.binding_uid,
                input_data_type=InputDataType.STRUCTURED,
                problem_type=ProblemType.BINARY_CLASSIFICATION,
                prediction_column='predicted_label',
                probability_column='score',
                label_column='Risk'))

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print("Subscription uid: ".format(TestAIOpenScaleClient.subscription_uid))

    def test_06_get_subscription_details(self):
        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.subscription_uid)
        details = TestAIOpenScaleClient.subscription.get_details()
        print('Subscription details: ' + str(details))

        self.assertTrue('s3' in str(details))

    def test_07_list_deployments(self):
        TestAIOpenScaleClient.subscription.list_deployments()
        deployment_uids = TestAIOpenScaleClient.subscription.get_deployment_uids()
        self.assertGreater(len(deployment_uids), 0)

    def test_08_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        for configuration in subscription_details['entity']['configurations']:
            if configuration['type'] == 'payload_logging' or configuration['type'] == 'performance_monitoring':
                self.assertEqual(configuration['enabled'], True)
            else:
                self.assertEqual(configuration['enabled'], False)

    def test_09_score_model_and_log_payload(self):
        binding_details = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_details(TestAIOpenScaleClient.binding_uid)
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        request, response, response_time = self.score(binding_details=binding_details, subscription_details=subscription_details)

        records_list = []
        for i in range(0, 15):
            records_list.append(PayloadRecord(request=request, response=response, response_time=int(response_time)))

        TestAIOpenScaleClient.subscription.payload_logging.store(records=records_list)

        time.sleep(20)

    def test_10_stats_on_payload_logging_table(self):
        payload_table_content = TestAIOpenScaleClient.subscription.payload_logging.get_table_content(format='python')
        # self.assertTrue('perimeter_mean' in str(payload_table_content))
        print(payload_table_content)

        TestAIOpenScaleClient.subscription.payload_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.payload_logging.show_table()
        TestAIOpenScaleClient.subscription.payload_logging.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.payload_logging.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_11_stats_on_performance_monitoring_table(self):
        TestAIOpenScaleClient.subscription.performance_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.performance_monitoring.show_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content()
        performance_metrics = TestAIOpenScaleClient.subscription.performance_monitoring.get_table_content(
            format='python')
        self.assertGreater(len(performance_metrics['values']), 0)

    def test_12_setup_quality_monitoring(self):
        from ibm_ai_openscale.supporting_classes.enums import ProblemType
        TestAIOpenScaleClient.subscription.quality_monitoring.enable(problem_type=ProblemType.BINARY_CLASSIFICATION, threshold=0.8, min_records=5)

    def test_13_get_quality_monitoring_details(self):
        print(str(TestAIOpenScaleClient.subscription.quality_monitoring.get_details()))
        TestAIOpenScaleClient.subscription.quality_monitoring.get_details()

    def test_14_send_feedback_data(self):

        feedback_records = []

        fields = ['Risk', 'CheckingStatus_0_to_200', 'CheckingStatus_greater_200', 'CheckingStatus_less_0', 'CheckingStatus_no_checking', 'CreditHistory_all_credits_paid_back', 'CreditHistory_credits_paid_to_date', 'CreditHistory_no_credits', 'CreditHistory_outstanding_credit', 'CreditHistory_prior_payments_delayed', 'LoanPurpose_appliances', 'LoanPurpose_business', 'LoanPurpose_car_new', 'LoanPurpose_car_used', 'LoanPurpose_education', 'LoanPurpose_furniture', 'LoanPurpose_other', 'LoanPurpose_radio_tv', 'LoanPurpose_repairs', 'LoanPurpose_retraining', 'LoanPurpose_vacation', 'ExistingSavings_100_to_500', 'ExistingSavings_500_to_1000', 'ExistingSavings_greater_1000', 'ExistingSavings_less_100', 'ExistingSavings_unknown', 'EmploymentDuration_1_to_4', 'EmploymentDuration_4_to_7', 'EmploymentDuration_greater_7', 'EmploymentDuration_less_1', 'EmploymentDuration_unemployed', 'Sex_female', 'Sex_male', 'OthersOnLoan_co-applicant', 'OthersOnLoan_guarantor', 'OthersOnLoan_none', 'OwnsProperty_car_other', 'OwnsProperty_real_estate', 'OwnsProperty_savings_insurance', 'OwnsProperty_unknown', 'InstallmentPlans_bank', 'InstallmentPlans_none', 'InstallmentPlans_stores', 'Housing_free', 'Housing_own', 'Housing_rent', 'Job_management_self-employed', 'Job_skilled', 'Job_unemployed', 'Job_unskilled', 'Telephone_none', 'Telephone_yes', 'ForeignWorker_no', 'ForeignWorker_yes', 'LoanDuration', 'LoanAmount', 'InstallmentPercent', 'CurrentResidenceDuration', 'Age', 'ExistingCreditsCount', 'Dependents']

        for i in range(1, 10):
            feedback_records.append(
                [0,0,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,1,1,0,0,0,0,1,0,0,1,0,1,0,0,0,0,1,0,1,25,5593,3,4,58,2,2])

        TestAIOpenScaleClient.subscription.feedback_logging.store(feedback_data=feedback_records, fields=fields)

        time.sleep(10)

    def test_15_run_quality_monitor(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
        print("First run details: {}".format(run_details))
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
            self.assertNotIn('failed', status)

        self.assertTrue('completed' in status)

    def test_16_stats_on_quality_monitoring_table(self):
        TestAIOpenScaleClient.subscription.quality_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.show_table(limit=None)
        TestAIOpenScaleClient.subscription.quality_monitoring.describe_table()
        TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content()
        quality_metrics = TestAIOpenScaleClient.subscription.quality_monitoring.get_table_content(format='python')
        self.assertTrue(len(quality_metrics['values']) > 0)

    def test_17_stats_on_feedback_logging_table(self):
        TestAIOpenScaleClient.subscription.feedback_logging.print_table_schema()
        TestAIOpenScaleClient.subscription.feedback_logging.show_table()
        TestAIOpenScaleClient.subscription.feedback_logging.describe_table()
        TestAIOpenScaleClient.subscription.feedback_logging.get_table_content()
        feedback_logging = TestAIOpenScaleClient.subscription.feedback_logging.get_table_content(format='python')
        self.assertTrue(len(feedback_logging['values']) > 0)

    def test_18_score_model_and_log_payload(self):
        binding_details = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_details(TestAIOpenScaleClient.binding_uid)
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        request, response, response_time = self.score(binding_details=binding_details, subscription_details=subscription_details)

        TestAIOpenScaleClient.transaction_id = str(uuid.uuid4()).replace("-", "")
        TestAIOpenScaleClient.transaction_id_2 = str(uuid.uuid4()).replace("-", "")

        records_list = [PayloadRecord(request=request, response=response, response_time=int(response_time), scoring_id=TestAIOpenScaleClient.transaction_id),
                        PayloadRecord(request=request, response=response, response_time=int(response_time), scoring_id=TestAIOpenScaleClient.transaction_id_2)]

        TestAIOpenScaleClient.subscription.payload_logging.store(records=records_list)

        time.sleep(10)

    def test_19_setup_explainability(self):
        with open('assets/training_distribution_german_credit_risk_numerical.json') as json_file:
            training_data_statistics = json.load(json_file)

        self.assertIsNotNone(training_data_statistics)

        TestAIOpenScaleClient.subscription.explainability.enable(
            feature_columns=['CheckingStatus_0_to_200', 'CheckingStatus_greater_200', 'CheckingStatus_less_0', 'CheckingStatus_no_checking', 'CreditHistory_all_credits_paid_back', 'CreditHistory_credits_paid_to_date', 'CreditHistory_no_credits', 'CreditHistory_outstanding_credit', 'CreditHistory_prior_payments_delayed', 'LoanPurpose_appliances', 'LoanPurpose_business', 'LoanPurpose_car_new', 'LoanPurpose_car_used', 'LoanPurpose_education', 'LoanPurpose_furniture', 'LoanPurpose_other', 'LoanPurpose_radio_tv', 'LoanPurpose_repairs', 'LoanPurpose_retraining', 'LoanPurpose_vacation', 'ExistingSavings_100_to_500', 'ExistingSavings_500_to_1000', 'ExistingSavings_greater_1000', 'ExistingSavings_less_100', 'ExistingSavings_unknown', 'EmploymentDuration_1_to_4', 'EmploymentDuration_4_to_7', 'EmploymentDuration_greater_7', 'EmploymentDuration_less_1', 'EmploymentDuration_unemployed', 'Sex_female', 'Sex_male', 'OthersOnLoan_co-applicant', 'OthersOnLoan_guarantor', 'OthersOnLoan_none', 'OwnsProperty_car_other', 'OwnsProperty_real_estate', 'OwnsProperty_savings_insurance', 'OwnsProperty_unknown', 'InstallmentPlans_bank', 'InstallmentPlans_none', 'InstallmentPlans_stores', 'Housing_free', 'Housing_own', 'Housing_rent', 'Job_management_self-employed', 'Job_skilled', 'Job_unemployed', 'Job_unskilled', 'Telephone_none', 'Telephone_yes', 'ForeignWorker_no', 'ForeignWorker_yes', 'LoanDuration', 'LoanAmount', 'InstallmentPercent', 'CurrentResidenceDuration', 'Age', 'ExistingCreditsCount', 'Dependents'],
            categorical_columns=[],
            training_data_statistics=training_data_statistics
        )

    def test_20_get_details(self):
        details = TestAIOpenScaleClient.subscription.explainability.get_details()
        print("Explainability details: {}".format(details))

        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        self.assertTrue('label' in str(subscription_details))

    def test_21_run_explainability(self):
        TestAIOpenScaleClient.status = TestAIOpenScaleClient.subscription.explainability.run(
            transaction_id="{}-1".format(TestAIOpenScaleClient.transaction_id),
            background_mode=False
        )['entity']['status']['state']
        print("Status: {}".format(TestAIOpenScaleClient.status))
        self.assertTrue(TestAIOpenScaleClient.status == "finished")

    def test_22_print_explainability_table_schema(self):
        TestAIOpenScaleClient.subscription.explainability.print_table_schema()

    def test_23_stats_on_explainability_table(self):
        TestAIOpenScaleClient.subscription.explainability.show_table()
        TestAIOpenScaleClient.subscription.explainability.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.explainability.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_24_setup_fairness_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Feature

        try:
            TestAIOpenScaleClient.subscription.fairness_monitoring.enable(
                features=[
                    Feature("Age", majority=[[26,75]], minority=[[18,25]], threshold=0.95)
                ],
                favourable_classes=[0],
                unfavourable_classes=[1],
                min_records=4
            )
            TestAIOpenScaleClient.fairness_enabled = True
        except Exception as ex:
            print("Unable to set up fairness monitoring.")
            self.fail("Unable to set up fairness monitoring.")

    def test_25_get_fairness_monitoring_details(self):
        print(TestAIOpenScaleClient.subscription.fairness_monitoring.get_details())

    def test_26_run(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.run(background_mode=False)

    def test_27_stats_on_fairness_table(self):
        TestAIOpenScaleClient.subscription.fairness_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.fairness_monitoring.show_table()
        TestAIOpenScaleClient.subscription.fairness_monitoring.describe_table()
        pandas_df = TestAIOpenScaleClient.subscription.fairness_monitoring.get_table_content()
        print(str(pandas_df))
        self.assertTrue(pandas_df.size > 1)

    def test_28_disable_all_monitors(self):
        self.subscription.quality_monitoring.disable()
        self.subscription.fairness_monitoring.disable()
        self.subscription.explainability.disable()
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()

        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        print(subscription_details)

        for configuration in subscription_details['entity']['configurations']:
            self.assertFalse(configuration['enabled'])

    def test_30_get_metrics(self):
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics())
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(deployment_uid=TestAIOpenScaleClient.deployment_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(subscription_uid=TestAIOpenScaleClient.subscription.uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(asset_uid=TestAIOpenScaleClient.subscription.source_uid))
        print(TestAIOpenScaleClient.ai_client.data_mart.get_deployment_metrics(metric_type='quality'))

    def test_31_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_32_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
