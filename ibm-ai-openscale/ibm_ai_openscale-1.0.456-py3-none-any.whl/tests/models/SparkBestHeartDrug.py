# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os
import pandas as pd


def get_model_data():
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import StringIndexer, IndexToString, VectorAssembler
    from pyspark.ml.classification import RandomForestClassifier
    from pyspark.ml import Pipeline
    from pyspark.sql.types import StructType, DoubleType, StringType, ArrayType

    spark = SparkSession.builder.getOrCreate()

    df_data = spark.read \
        .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
        .option('header', 'true') \
        .option("delimiter", ';') \
        .option('inferSchema', 'true') \
        .load("datasets/BestHeartDrug/drug_train_data.csv")

    df_test = spark.read \
        .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
        .option('header', 'true') \
        .option("delimiter", ';') \
        .option('inferSchema', 'true') \
        .load("datasets/drugs/drug_feedback_test.csv")

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


    return {
        'model': model_rf,
        'pipeline': pipeline_rf,
        'training_data': df_data,
        'test_data': df_test,
        'output_data_schema': output_data_schema
    }


def get_scoring_payload():
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


def get_scoring_payload_from_training_data():
    test_data = pd.read_csv("datasets/BestHeartDrug/drug_train_data.csv", header=0, sep=';')
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
