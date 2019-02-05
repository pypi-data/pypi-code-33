# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from .AbstractModel import AbstractModel, AbstractFeedbackModel

import os
import pandas as pd
from pyspark import SparkContext, SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, DoubleType, StringType, ArrayType
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, IndexToString, VectorAssembler, RFormula
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import OneHotEncoder, StringIndexer, IndexToString, VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline, Model


class GoSales(AbstractModel):

    model_name = "AIOS Spark GoSales xcxcw"
    deployment_name = "AIOS Spark GoSales xcxc"

    file_path = "datasets/GoSales/GoSales_Tx_NaiveBayes.csv"

    def __init__(self):
        spark = SparkSession.builder.getOrCreate()

        df_data = spark.read \
            .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
            .option('header', 'true') \
            .option('inferSchema', 'true') \
            .load(self.file_path)

        splitted_data = df_data.randomSplit([0.8, 0.18, 0.02], 24)
        train_data = splitted_data[0]
        test_data = splitted_data[1]
        predict_data = splitted_data[2]

        stringIndexer_label = StringIndexer(inputCol="PRODUCT_LINE", outputCol="label").fit(df_data)
        stringIndexer_prof = StringIndexer(inputCol="PROFESSION", outputCol="PROFESSION_IX")
        stringIndexer_gend = StringIndexer(inputCol="GENDER", outputCol="GENDER_IX")
        stringIndexer_mar = StringIndexer(inputCol="MARITAL_STATUS", outputCol="MARITAL_STATUS_IX")

        vectorAssembler_features = VectorAssembler(inputCols=["GENDER_IX", "AGE", "MARITAL_STATUS_IX", "PROFESSION_IX"],
                                                   outputCol="features")
        rf = RandomForestClassifier(labelCol="label", featuresCol="features")
        labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel",
                                       labels=stringIndexer_label.labels)
        pipeline_rf = Pipeline(stages=[stringIndexer_label, stringIndexer_prof, stringIndexer_gend, stringIndexer_mar,
                                       vectorAssembler_features, rf, labelConverter])
        model_rf = pipeline_rf.fit(train_data)

        self.model = model_rf
        self.pipeline = pipeline_rf
        self.training_data = train_data
        self.test_data = test_data
        self.prediction = predict_data
        self.labels = stringIndexer_label.labels

    def publish_to_wml(self, wml_client):
        return wml_client.repository.store_model(model=self.model, meta_props=self.get_model_props(wml_client), training_data=self.training_data, pipeline=self.pipeline)

    def get_model_props(self, wml_client):
        return {
            wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            wml_client.repository.ModelMetaNames.NAME: self.model_name
        }

    def get_name(self):
        return "spark_gosales_model"

    def get_scoring_payload(self):
        return {
           "fields": [
              "GENDER",
              "AGE",
              "MARITAL_STATUS",
              "PROFESSION"
           ],
           "values": [
              [
                 "M",
                 23,
                 "Single",
                 "Student"
              ],
              [
                 "M",
                 55,
                 "Single",
                 "Executive"
              ]
           ]
        }


class CustomerSatisfaction(AbstractModel):
    model_name = "AIOS Spark Telco Modelxxxx"
    deployment_name = "AIOS Spark Telco Deploymentxxxx"

    file_path = os.path.join(os.getcwd(), 'datasets', 'SparkMlibRegression', 'WA_FnUseC_TelcoCustomerChurn.csv')

    def __init__(self):

        spark = SparkSession.builder.getOrCreate()

        df_data = spark.read \
            .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
            .option('header', 'true') \
            .option('inferSchema', 'true') \
            .option('nanValue', ' ') \
            .option('nullValue', ' ') \
            .load(self.file_path)

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

        self.model = lr_model
        self.pipeline = pipeline_lr
        self.training_data = train_data
        self.test_data = test_data
        self.prediction = lr_predictions
        self.output_data_schema = output_data_schema.jsonValue()

    def publish_to_wml(self, wml_client):

        meta_props = self.get_model_props(wml_client)
        return wml_client.repository.store_model(model=self.model, meta_props=meta_props, training_data=self.training_data, pipeline=self.pipeline)

    def get_model_props(self, wml_client):
        return {
            wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            wml_client.repository.ModelMetaNames.NAME: self.model_name,
            wml_client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA: self.output_data_schema
        }

    def get_scoring_payload(self):
        return {
            "fields": [
                "customerID",
                "gender",
                "SeniorCitizen",
                "Partner",
                "Dependents",
                "tenure",
                "PhoneService",
                "MultipleLines",
                "InternetService",
                "OnlineSecurity",
                "OnlineBackup",
                "DeviceProtection",
                "TechSupport",
                "StreamingTV",
                "StreamingMovies",
                "Contract",
                "PaperlessBilling",
                "PaymentMethod",
                "MonthlyCharges"
            ],
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


class BestHeartDrug(AbstractModel):
    model_name = "AIOS Spark BestDrug Model"
    deployment_name = "AIOS Spark BestDrug Deployment"

    training_data_path = "datasets/BestHeartDrug/drug_train_data.csv"
    feedback_data_path = "datasets/drugs/drug_feedback_test.csv"

    def __init__(self):
        spark = SparkSession.builder.getOrCreate()

        df_data = spark.read \
            .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
            .option('header', 'true') \
            .option("delimiter", ';') \
            .option('inferSchema', 'true') \
            .load(self.training_data_path)

        df_test = spark.read \
            .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
            .option('header', 'true') \
            .option("delimiter", ';') \
            .option('inferSchema', 'true') \
            .load(self.feedback_data_path)

        stringIndexer_label = StringIndexer(inputCol="DRUG", outputCol="label").fit(df_data)
        stringIndexer_sex = StringIndexer(inputCol="SEX", outputCol="SEX_IX")
        stringIndexer_bp = StringIndexer(inputCol="BP", outputCol="BP_IX")
        stringIndexer_chol = StringIndexer(inputCol="CHOLESTEROL", outputCol="CHOLESTEROL_IX")

        vectorAssembler_features = VectorAssembler(inputCols=["AGE", "SEX_IX", "BP_IX", "CHOLESTEROL_IX", "NA", "K"],
                                                   outputCol="features")
        rf = RandomForestClassifier(labelCol="label", featuresCol="features")
        labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel",
                                       labels=stringIndexer_label.labels)
        pipeline_rf = Pipeline(stages=[stringIndexer_label, stringIndexer_sex, stringIndexer_bp, stringIndexer_chol,
                                       vectorAssembler_features, rf, labelConverter])
        model_rf = pipeline_rf.fit(df_data)

        train_data_schema = df_data.schema
        label_field = next(f for f in train_data_schema.fields if f.name == "DRUG")
        label_field.metadata['values'] = stringIndexer_label.labels

        input_fileds = filter(lambda f: f.name != "DRUG", train_data_schema.fields)

        output_data_schema = StructType(list(input_fileds)). \
            add("prediction", DoubleType(), True, {'modeling_role': 'prediction'}). \
            add("predictedLabel", StringType(), True,
                {'modeling_role': 'decoded-target', 'values': stringIndexer_label.labels}). \
            add("probability", ArrayType(DoubleType()), True, {'modeling_role': 'probability'})

        self.model = model_rf
        self.pipeline = pipeline_rf
        self.training_data = df_data
        self.test_data = df_test
        self.output_data_schema = output_data_schema

    def publish_to_wml(self, wml_client):
        pass

    def get_model_props(self, wml_client):
        pass

    def get_scoring_payload(self):
        return {
            "fields": [
                "AGE",
                "SEX",
                "BP",
                "CHOLESTEROL",
                "NA",
                "K"
            ],
            "values": [
                [
                    20.0,
                    "F",
                    "HIGH",
                    "HIGH",
                    0.71,
                    0.07
                ],
                [
                    55.0,
                    "M",
                    "LOW",
                    "HIGH",
                    0.71,
                    0.07
                ]
            ]
        }

    def get_scoring_payload_from_training_data(self):
        test_data = pd.read_csv(self.training_data_path, header=0, sep=';')
        sample = test_data.sample()

        return {
            "fields": [
                "AGE",
                "SEX",
                "BP",
                "CHOLESTEROL",
                "NA",
                "K"
            ],
            "values": [
                [
                    sample.iloc[0]['AGE'],
                    sample.iloc[0]['SEX'],
                    sample.iloc[0]['BP'],
                    sample.iloc[0]['CHOLESTEROL'],
                    sample.iloc[0]['NA'],
                    sample.iloc[0]['K']
                ]
            ]
        }


class BestHeartDrugFeedback(AbstractFeedbackModel):

    training_data_path = "datasets/drugs/drug_feedback_data.csv"
    feedback_data_path = "datasets/drugs/drug_feedback_test.csv"

    def publish_to_wml(self, wml_client, db2_credentials):
        ctx = SparkContext.getOrCreate()
        sc = SQLContext(ctx)

        db2_service_credentials = {
            "port": 50000,
            "db": "BLUDB",
            "username": "dash13173",
            "ssljdbcurl": "jdbc:db2://dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net:50001/BLUDB:sslConnection=true;",
            "host": "dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net",
            "https_url": "https://dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net:8443",
            "dsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=dash13173;PWD=UDoy3w_qT9W_;",
            "hostname": "dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net",
            "jdbcurl": "jdbc:db2://dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net:50000/BLUDB",
            "ssldsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=dash13173;PWD=UDoy3w_qT9W_;Security=SSL;",
            "uri": "db2://dash13173:UDoy3w_qT9W_@dashdb-entry-yp-lon02-01.services.eu-gb.bluemix.net:50000/BLUDB",
            "password": "UDoy3w_qT9W_"
        }

        train_data = sc.read.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ";").option("inferSchema", "true").load(self.training_data_path)
        test_data = sc.read.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ";").option("inferSchema", "true").load(self.feedback_data_path)

        stringIndexer_sex = StringIndexer(inputCol='SEX', outputCol='SEX_IX')
        stringIndexer_bp = StringIndexer(inputCol='BP', outputCol='BP_IX')
        stringIndexer_chol = StringIndexer(inputCol='CHOLESTEROL', outputCol='CHOL_IX')
        stringIndexer_label = StringIndexer(inputCol="DRUG", outputCol="label").fit(train_data)

        vectorAssembler_features = VectorAssembler(inputCols=["AGE", "SEX_IX", "BP_IX", "CHOL_IX", "NA", "K"],
                                                   outputCol="features")
        dt = DecisionTreeClassifier(labelCol="label", featuresCol="features")
        labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel",
                                       labels=stringIndexer_label.labels)
        pipeline_dt = Pipeline(stages=[stringIndexer_label, stringIndexer_sex, stringIndexer_bp, stringIndexer_chol,
                                       vectorAssembler_features, dt, labelConverter])

        model = pipeline_dt.fit(train_data)
        predictions = model.transform(test_data)
        evaluatorDT = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction",
                                                        metricName="accuracy")
        accuracy = evaluatorDT.evaluate(predictions)

        train_data_schema = train_data.schema
        label_field = next(f for f in train_data_schema.fields if f.name == "DRUG")
        label_field.metadata['values'] = stringIndexer_label.labels

        input_fileds = filter(lambda f: f.name != "DRUG", train_data_schema.fields)

        output_data_schema = StructType(list(input_fileds)). \
            add("prediction", DoubleType(), True, {'modeling_role': 'prediction'}). \
            add("predictedLabel", StringType(), True,
                {'modeling_role': 'decoded-target', 'values': stringIndexer_label.labels}). \
            add("probability", ArrayType(DoubleType()), True, {'modeling_role': 'probability'})

        model_props = {
            wml_client.repository.ModelMetaNames.NAME: "Best Heart Drug Selection",
            wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: self.get_training_data_reference(db2_credentials=db2_service_credentials),
            wml_client.repository.ModelMetaNames.EVALUATION_METHOD: "multiclass",
            wml_client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA: output_data_schema.jsonValue(),
            wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                {
                    "name": "accuracy",
                    "value": 0.7,
                    "threshold": 0.8
                }
            ]
        }

        return wml_client.repository.store_model(model=model, meta_props=model_props, training_data=train_data, pipeline=pipeline_dt)

    def get_training_data_reference(self, db2_credentials):
        return {
            "name": "DRUG feedback",
            "connection": db2_credentials,
            "source": {
                "tablename": "DRUG_TRAIN_DATA_UPDATED",
                "type": "dashdb"
            }
        }

    def get_feedback_data(self):
        feedback_data = [
                [74.0, 'M', 'HIGH', 'HIGH', 0.715337, 0.074773, 'drugB'],
                [58.0, 'F', 'HIGH', 'NORMAL', 0.868924, 0.061023, 'drugB'],
                [68.0, 'F', 'HIGH', 'NORMAL', 0.77541, 0.0761, 'drugB'],
                [65.0, 'M', 'HIGH', 'NORMAL', 0.635551, 0.056043, 'drugB'],
                [60.0, 'F', 'HIGH', 'HIGH', 0.800607, 0.060181, 'drugB'],
                [70.0, 'M', 'HIGH', 'HIGH', 0.658606, 0.047153, 'drugB'],
                [60.0, 'M', 'HIGH', 'HIGH', 0.805651, 0.057821, 'drugB'],
                [59.0, 'M', 'HIGH', 'HIGH', 0.816356, 0.058583, 'drugB'],
                [60.0, 'F', 'HIGH', 'HIGH', 0.800607, 0.060181, 'drugB'],
                [70.0, 'M', 'HIGH', 'HIGH', 0.658606, 0.047153, 'drugB'],
                [60.0, 'M', 'HIGH', 'HIGH', 0.805651, 0.057821, 'drugB'],
                [59.0, 'M', 'HIGH', 'HIGH', 0.816356, 0.058583, 'drugB']
            ]
        fields = ['AGE', 'SEX', 'BP', 'CHOLESTEROL', 'NA', 'K', 'DRUG']

        return feedback_data, fields

    def get_model_props(self, wml_client, db2_credentials):
        pass

    def get_scoring_payload(self):
        pass
