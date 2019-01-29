import os

from pyspark import SparkContext, SQLContext
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler, IndexToString
from pyspark.sql.types import StructType, DoubleType, StringType, ArrayType

from ..deployment_template import DeploymentTemplate


class GermanCreditRisk(DeploymentTemplate):

    asset_name = "AIOS Spark German Risk model"
    deployment_name = "AIOS Spark German Risk deployment"

    model = None
    auc = None
    pipeline = None
    train_data = None
    test_data = None
    training_data_reference = None
    output_data_schema = None

    def get_scoring_payload(self):
        fields = ["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose", "LoanAmount", "ExistingSavings",
                  "EmploymentDuration", "InstallmentPercent", "Sex", "OthersOnLoan", "CurrentResidenceDuration",
                  "OwnsProperty", "Age", "InstallmentPlans", "Housing", "ExistingCreditsCount", "Job", "Dependents",
                  "Telephone", "ForeignWorker"]
        values = [
            ["no_checking", 13, "credits_paid_to_date", "car_new", 1343, "100_to_500", "1_to_4", 2, "female", "none", 3,
             "savings_insurance", 46, "none", "own", 2, "skilled", 1, "none", "yes"],
            ["no_checking", 24, "prior_payments_delayed", "furniture", 4567, "500_to_1000", "1_to_4", 4, "male", "none",
             4, "savings_insurance", 36, "none", "free", 2, "management_self-employed", 1, "none", "yes"],
            ["0_to_200", 26, "all_credits_paid_back", "car_new", 863, "less_100", "less_1", 2, "female", "co-applicant",
             2, "real_estate", 38, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["0_to_200", 14, "no_credits", "car_new", 2368, "less_100", "1_to_4", 3, "female", "none", 3, "real_estate",
             29, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["0_to_200", 4, "no_credits", "car_new", 250, "less_100", "unemployed", 2, "female", "none", 3,
             "real_estate", 23, "none", "rent", 1, "management_self-employed", 1, "none", "yes"],
            ["no_checking", 17, "credits_paid_to_date", "car_new", 832, "100_to_500", "1_to_4", 2, "male", "none", 2,
             "real_estate", 42, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["no_checking", 33, "outstanding_credit", "appliances", 5696, "unknown", "greater_7", 4, "male",
             "co-applicant", 4, "unknown", 54, "none", "free", 2, "skilled", 1, "yes", "yes"],
            ["0_to_200", 13, "prior_payments_delayed", "retraining", 1375, "100_to_500", "4_to_7", 3, "male", "none", 3,
             "real_estate", 37, "none", "own", 2, "management_self-employed", 1, "none", "yes"]
        ]
        return {"fields": fields, "values": values}

    def _prepare_model(self):
        ctx = SparkContext.getOrCreate()
        sc = SQLContext(ctx)

        spark_df = sc.read.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ",").option("inferSchema", "true").load(os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'credit_risk_training.csv'))
        spark_df.printSchema()

        (train_data, test_data) = spark_df.randomSplit([0.8, 0.2], 24)
        print("Number of records for training: " + str(train_data.count()))
        print("Number of records for evaluation: " + str(test_data.count()))

        self.train_data = train_data
        self.test_data = test_data

        si_CheckingStatus = StringIndexer(inputCol='CheckingStatus', outputCol='CheckingStatus_IX')
        si_CreditHistory = StringIndexer(inputCol='CreditHistory', outputCol='CreditHistory_IX')
        si_LoanPurpose = StringIndexer(inputCol='LoanPurpose', outputCol='LoanPurpose_IX')
        si_ExistingSavings = StringIndexer(inputCol='ExistingSavings', outputCol='ExistingSavings_IX')
        si_EmploymentDuration = StringIndexer(inputCol='EmploymentDuration', outputCol='EmploymentDuration_IX')
        si_Sex = StringIndexer(inputCol='Sex', outputCol='Sex_IX')
        si_OthersOnLoan = StringIndexer(inputCol='OthersOnLoan', outputCol='OthersOnLoan_IX')
        si_OwnsProperty = StringIndexer(inputCol='OwnsProperty', outputCol='OwnsProperty_IX')
        si_InstallmentPlans = StringIndexer(inputCol='InstallmentPlans', outputCol='InstallmentPlans_IX')
        si_Housing = StringIndexer(inputCol='Housing', outputCol='Housing_IX')
        si_Job = StringIndexer(inputCol='Job', outputCol='Job_IX')
        si_Telephone = StringIndexer(inputCol='Telephone', outputCol='Telephone_IX')
        si_ForeignWorker = StringIndexer(inputCol='ForeignWorker', outputCol='ForeignWorker_IX')
        si_Label = StringIndexer(inputCol="Risk", outputCol="label").fit(spark_df)
        label_converter = IndexToString(inputCol="prediction", outputCol="predictedLabel", labels=si_Label.labels)

        va_features = VectorAssembler(
            inputCols=["CheckingStatus_IX", "CreditHistory_IX", "LoanPurpose_IX", "ExistingSavings_IX",
                       "EmploymentDuration_IX", "Sex_IX", "OthersOnLoan_IX", "OwnsProperty_IX", "InstallmentPlans_IX",
                       "Housing_IX", "Job_IX", "Telephone_IX", "ForeignWorker_IX", "LoanDuration", "LoanAmount",
                       "InstallmentPercent", "CurrentResidenceDuration", "LoanDuration", "Age", "ExistingCreditsCount",
                       "Dependents"], outputCol="features")

        classifier = RandomForestClassifier(featuresCol="features")

        self.pipeline = Pipeline(
            stages=[si_CheckingStatus, si_CreditHistory, si_EmploymentDuration, si_ExistingSavings, si_ForeignWorker,
                    si_Housing, si_InstallmentPlans, si_Job, si_LoanPurpose, si_OthersOnLoan,
                    si_OwnsProperty, si_Sex, si_Telephone, si_Label, va_features, classifier, label_converter])

        self.model = self.pipeline.fit(train_data)
        predictions = self.model.transform(test_data)
        evaluator = BinaryClassificationEvaluator(rawPredictionCol="prediction")
        self.auc = evaluator.evaluate(predictions)

        print("Accuracy = %g" % self.auc)

        self.training_data_reference = {
            "name": "Credit Risk feedback",
            "connection": self._get_db2_credentials(),
            "source": {
                "tablename": self._get_db2_table_name(),
                "type": "dashdb"
            }
        }

        train_data_schema = spark_df.schema
        label_field = next(f for f in train_data_schema.fields if f.name == "Risk")
        label_field.metadata['values'] = si_Label.labels
        input_fileds = filter(lambda f: f.name != "Risk", train_data_schema.fields)

        self.output_data_schema = StructType(list(input_fileds)). \
            add("prediction", DoubleType(), True, {'modeling_role': 'prediction'}). \
            add("predictedLabel", StringType(), True,
                {'modeling_role': 'decoded-target', 'values': si_Label.labels}). \
            add("probability", ArrayType(DoubleType()), True, {'modeling_role': 'probability'})

    def _deploy_model_to_wml(self, wml_client):
        if self.model is None:
            self._prepare_model()

        model_props = {
            wml_client.repository.ModelMetaNames.NAME: "{}".format(self.asset_name),
            wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: self.training_data_reference,
            wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                {
                    "name": "AUC",
                    "value": self.auc,
                    "threshold": 0.8
                }
            ]
        }

        return wml_client.repository.store_model(model=self.model, meta_props=model_props, training_data=self.train_data, pipeline=self.pipeline)

    def _get_db2_credentials(self):
        return {
          "hostname": "dashdb-entry-yp-dal09-10.services.dal.bluemix.net",
          "password": "89TsmoAN_Sb_",
          "https_url": "https://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:8443",
          "port": 50000,
          "ssldsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-dal09-10.services.dal.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=dash14647;PWD=89TsmoAN_Sb_;Security=SSL;",
          "host": "dashdb-entry-yp-dal09-10.services.dal.bluemix.net",
          "jdbcurl": "jdbc:db2://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50000/BLUDB",
          "uri": "db2://dash14647:89TsmoAN_Sb_@dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50000/BLUDB",
          "db": "BLUDB",
          "dsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-dal09-10.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=dash14647;PWD=89TsmoAN_Sb_;",
          "username": "dash14647",
          "ssljdbcurl": "jdbc:db2://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50001/BLUDB:sslConnection=true;"
        }

    def _get_db2_table_name(self):
        return "CREDIT_RISK_TRAINING"