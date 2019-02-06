# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from pyspark.ml import Pipeline
from pyspark.ml.feature import RFormula
from pyspark.ml.regression import LinearRegression
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, DoubleType, ArrayType

from assertions import *
from datasets_classes import TelcoCustomerChurnDataset
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes import *
from models.spark import CustomerSatisfaction
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
    transaction_id = None
    scoring_records = 10
    feedback_records = 10

    test_uid = str(uuid.uuid4())

    model = CustomerSatisfaction()

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

    def test_02_data_mart_get_details(self):
        details = TestAIOpenScaleClient.ai_client.data_mart.get_details()
        assert_datamart_details(details, schema=self.schema)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))

        print("Binding details:\n{}".format(self.ai_client.data_mart.bindings.get_details(self.binding_uid)))

    def test_04_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_05_prepare_deployment(self):
        model_name = "AIOS Spark Telco Model"
        deployment_name = "AIOS Spark Telco Deployment"

        file_path = os.path.join(os.getcwd(), 'datasets', 'SparkMlibRegression', 'WA_FnUseC_TelcoCustomerChurn.csv')

        spark = SparkSession.builder.getOrCreate()

        df_data = spark.read \
            .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
            .option('header', 'true') \
            .option('inferSchema', 'true') \
            .option('nanValue', ' ') \
            .option('nullValue', ' ') \
            .load(file_path)

        df_complete = df_data.dropna()
        df_complete.drop('Churn')

        (train_data, test_data) = df_complete.randomSplit([0.8, 0.2], 24)

        features = RFormula(
            formula="~ gender + SeniorCitizen +  Partner + Dependents + tenure + PhoneService + MultipleLines + "
                    "InternetService + OnlineSecurity + OnlineBackup + DeviceProtection + TechSupport + StreamingTV + "
                    "StreamingMovies + Contract + PaperlessBilling + PaymentMethod + MonthlyCharges - 1")

        lr = LinearRegression(labelCol='TotalCharges')
        pipeline_lr = Pipeline(stages=[features, lr])
        lr_model = pipeline_lr.fit(train_data)
        lr_predictions = lr_model.transform(test_data)

        output_data_schema = StructType(list(filter(lambda f: f.name != "TotalCharges", df_data.schema.fields))). \
            add("prediction", DoubleType(), True, {'modeling_role': 'prediction'}). \
            add("probability", ArrayType(DoubleType()), True, {'modeling_role': 'probability'})

        model = lr_model
        pipeline = pipeline_lr
        training_data = train_data
        test_data = test_data
        prediction = lr_predictions
        output_data_schema = output_data_schema.jsonValue()

        model_meta_props = {
            self.wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            self.wml_client.repository.ModelMetaNames.NAME: model_name,
            self.wml_client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA: output_data_schema
        }

        print("Publishing a new model...")
        published_model_details = self.wml_client.repository.store_model(model=model, meta_props=model_meta_props, training_data=training_data, pipeline=pipeline)

        print("Published model details:\n{}".format(published_model_details))
        TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

        print("Deploying model: {}, deployment name: {}".format(model_name, deployment_name))
        deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
        TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        print("Deployment details:\n{}".format(deployment_details))

    def test_06_subscribe(self):
        from ibm_ai_openscale.supporting_classes.enums import ProblemType
        from ibm_ai_openscale.supporting_classes.enums import InputDataType

        if "ICP" in get_env():
            training_data_reference = DB2Reference(credentials=self.database_credentials, schema_name="TRAININGDATA", table_name="CUSTOMER_SATISFACTION")
        else:
            cos_resource = get_cos_resource()
            bucket_names = prepare_cos(cos_resource)
            TelcoCustomerChurnDataset.upload_to_cos(cos_resource, bucket_names['data'])
            training_data_reference = BluemixCloudObjectStorageReference(
                    get_cos_credentials(),
                    bucket_names['data'] + '/WA_FnUseC_TelcoCustomerChurn.csv',
                    first_line_header=True
                )

        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.add(
            WatsonMachineLearningAsset(
                training_data_reference=training_data_reference,
                source_uid=self.model_uid,
                binding_uid=self.binding_uid,
                problem_type=ProblemType.REGRESSION,
                input_data_type=InputDataType.STRUCTURED,
                feature_columns=["gender", "SeniorCitizen", "PaymentMethod", "MonthlyCharges"],
                categorical_columns=["gender", "SeniorCitizen", "PaymentMethod"]
            )
        )
        self.assertIsNotNone(self.subscription)
        TestAIOpenScaleClient.subscription_uid = self.subscription.uid

    def test_07_get_subscription(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

        subscription_details = self.subscription.get_details()
        print("Subscription details:\n{}".format(subscription_details))

    def test_08_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details, payload=True, performance=True)

    def test_09_get_payload_logging_details(self):
        payload_logging_details = self.subscription.payload_logging.get_details()
        assert_payload_logging_configuration(payload_logging_details=payload_logging_details)

    def test_10_get_performance_monitoring_details(self):
        performance_monitoring_details = self.subscription.performance_monitoring.get_details()
        assert_performance_monitoring_configuration(performance_monitoring_details=performance_monitoring_details)

    def test_11_score(self):
        deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
        scoring_endpoint = self.wml_client.deployments.get_scoring_url(deployment_details)

        scoring_payload = {
            "fields": ["customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure", "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
                       "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod", "MonthlyCharges" ],
            "values": [
                [
                    "9237-HQITU",
                    "Female",
                    0,
                    "No",
                    "No",
                    20,
                    "Yes",
                    "No",
                    "Fiber optic",
                    "No",
                    "No",
                    "No",
                    "No",
                    "No",
                    "No",
                    "Month-to-month",
                    "Yes",
                    "Electronic check",
                    70.7
                ],
                [
                    "3638-WEABW",
                    "Female",
                    0,
                    "Yes",
                    "No",
                    58,
                    "Yes",
                    "Yes",
                    "DSL",
                    "No",
                    "Yes",
                    "No",
                    "Yes",
                    "No",
                    "No",
                    "Two year",
                    "Yes",
                    "Credit card (automatic)",
                    59.900
                ],
                [
                    "8665-UTDHZ",
                    "Male",
                    0,
                    "Yes",
                    "Yes",
                    1,
                    "No",
                    "No phone service",
                    "DSL",
                    "No",
                    "Yes",
                    "No",
                    "No",
                    "No",
                    "No",
                    "Month-to-month",
                    "No",
                    "Electronic check",
                    30.200
                ],
                [
                    "8773-HHUOZ",
                    "Female",
                    0,
                    "No",
                    "Yes",
                    17,
                    "Yes",
                    "No",
                    "DSL",
                    "No",
                    "No",
                    "No",
                    "No",
                    "Yes",
                    "Yes",
                    "Month-to-month",
                    "Yes",
                    "Mailed check",
                    64.700
                ]
            ]
        }
        print("Scoring payload:\n{}".format(scoring_payload))

        TestAIOpenScaleClient.scoring_records = 20
        for i in range(0, int(self.scoring_records / 4)):
            scoring_result = self.wml_client.deployments.score(scoring_endpoint, scoring_payload)
            self.assertIsNotNone(scoring_result)

        print("Scoring result:\n{}".format(scoring_result))

        print("Waiting 30 seconds for propagation...")
        time.sleep(30)

    def test_12_stats_on_payload_logging_table(self):
        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()
        self.subscription.payload_logging.describe_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content, scoring_records=self.scoring_records)

        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        assert_payload_logging_python_table_content(python_table_content=python_table_content, fields=['prediction', 'probability'])

    def test_13_stats_on_performance_monitoring_table(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        self.subscription.performance_monitoring.print_table_schema()
        self.subscription.performance_monitoring.show_table()
        self.subscription.performance_monitoring.describe_table()

        performance_table_pandas = self.subscription.performance_monitoring.get_table_content()
        assert_performance_monitoring_pandas_table_content(pandas_table_content=performance_table_pandas)

        performance_table_python = self.subscription.performance_monitoring.get_table_content(format='python')
        assert_performance_monitoring_python_table_content(python_table_content=performance_table_python)

    def test_14_enable_quality_monitoring(self):
        self.subscription.quality_monitoring.enable(threshold=0.7, min_records=10)

        details = TestAIOpenScaleClient.subscription.quality_monitoring.get_details()
        assert_quality_monitoring_configuration(quality_monitoring_details=details)

    def test_15_feedback_logging(self):

        feedback_payload = [
            "9237-HQITU",
            "Female",
            0,
            "No",
            "No",
            20,
            "Yes",
            "No",
            "Fiber optic",
            "No",
            "No",
            "No",
            "No",
            "No",
            "No",
            "Month-to-month",
            "Yes",
            "Electronic check",
            70.7,
            "",
            1100
        ]
        print("Feedback payload:\n{}".format(feedback_payload))

        TestAIOpenScaleClient.feedback_records = 20
        records = []
        for i in range(0, self.feedback_records):
            records.append(feedback_payload)

        self.subscription.feedback_logging.store(feedback_data=records)

        print("Waiting 20 seconds for records.")
        time.sleep(20)

    def test_16_stats_on_feedback_logging(self):
        self.subscription.feedback_logging.show_table()
        self.subscription.feedback_logging.print_table_schema()
        self.subscription.feedback_logging.describe_table()

        feedback_pd = self.subscription.feedback_logging.get_table_content(format='pandas')
        assert_feedback_pandas_table_content(pandas_table_content=feedback_pd, feedback_records=self.feedback_records)

    def test_17_run_quality_monitoring(self):
        run_details = TestAIOpenScaleClient.subscription.quality_monitoring.run()
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
            print("Status: {}\nRun details: {}".format(status, run_details))
            self.assertNotEqual('failed', status)

        self.assertEqual('completed', status)

    def test_18_stats_on_quality_monitoring_table(self):
        self.subscription.quality_monitoring.print_table_schema()
        self.subscription.quality_monitoring.show_table()
        self.subscription.quality_monitoring.show_table(limit=None)
        self.subscription.quality_monitoring.describe_table()

        quality_monitoring_table = self.subscription.quality_monitoring.get_table_content()
        assert_quality_monitoring_pandas_table_content(pandas_table_content=quality_monitoring_table)

        quality_metrics = self.subscription.quality_monitoring.get_table_content(format='python')
        assert_quality_monitoring_python_table_content(python_table_content=quality_metrics)

    def test_19_get_transaction_id(self):
        python_table_content = self.subscription.payload_logging.get_table_content(format='python')
        no_payloads = len(python_table_content['values'])

        # select random record from payload table
        import random
        random_record = random.randint(0, no_payloads - 1)
        TestAIOpenScaleClient.transaction_id = python_table_content['values'][random_record][0]

        print("Selected trainsaction id: {}".format(self.transaction_id))

    def test_20_setup_explainability(self):
        TestAIOpenScaleClient.subscription.explainability.enable()

    def test_21_get_explainability_details(self):
        details = TestAIOpenScaleClient.subscription.explainability.get_details()
        assert_explainability_configuration(explainability_details=details)

    def test_22_run_explainability(self):
        explainability_run_detais = TestAIOpenScaleClient.subscription.explainability.run(
            transaction_id=self.transaction_id,
            background_mode=False
        )
        assert_explainability_run(explainability_run_details=explainability_run_detais)

    def test_23_stats_on_explainability_table(self):
        TestAIOpenScaleClient.subscription.explainability.print_table_schema()
        TestAIOpenScaleClient.subscription.explainability.show_table()
        TestAIOpenScaleClient.subscription.explainability.describe_table()

        pandas_df = TestAIOpenScaleClient.subscription.explainability.get_table_content()
        assert_explainability_pandas_table_content(pandas_table_content=pandas_df)

        python_table_content = TestAIOpenScaleClient.subscription.explainability.get_table_content(format='python')
        assert_explainability_python_table_content(python_table_content=python_table_content)

    def test_24_get_metrics(self):
        performance_metrics_deployment_uid = self.subscription.performance_monitoring.get_metrics(deployment_uid=self.deployment_uid)
        assert_performance_metrics(metrics=performance_metrics_deployment_uid)

        performance_metrics_deployments = self.subscription.performance_monitoring.get_deployment_metrics()
        assert_deployment_metrics(metrics=performance_metrics_deployments)

        deployment_metrics_performance = self.ai_client.data_mart.get_deployment_metrics(asset_uid=self.subscription.source_uid, metric_type='performance')
        assert_deployment_metrics(metrics=deployment_metrics_performance)

        deployment_metrics = self.ai_client.data_mart.get_deployment_metrics()
        assert_deployment_metrics(metrics=deployment_metrics)

        deployment_metrics_deployment_uid = self.ai_client.data_mart.get_deployment_metrics(deployment_uid=self.deployment_uid)
        assert_deployment_metrics(metrics=deployment_metrics_deployment_uid)

        deployment_metrics_subscription_uid = self.ai_client.data_mart.get_deployment_metrics(subscription_uid=self.subscription.uid)
        assert_deployment_metrics(metrics=deployment_metrics_subscription_uid)

        deployment_metrics_asset_uid = self.ai_client.data_mart.get_deployment_metrics(asset_uid=self.subscription.source_uid)
        assert_deployment_metrics(metrics=deployment_metrics_asset_uid)

    def test_25_disable_monitors(self):
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()
        self.subscription.quality_monitoring.disable()
        self.subscription.explainability.disable()

        subscription_details = self.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details)

    def test_26_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_27_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()

        for deployment in cls.wml_client.deployments.get_details()['resources']:
            if 'published_model' in deployment['entity'] and cls.model_uid == deployment['entity']['published_model']['guid']:
                print("Deleting deployment: {}".format(deployment['metadata']['guid']))
                cls.wml_client.deployments.delete(deployment['metadata']['guid'])
        cls.wml_client.repository.delete(cls.model_uid)
        print("Deleting model: {}".format(cls.model_uid))


if __name__ == '__main__':
    unittest.main()
