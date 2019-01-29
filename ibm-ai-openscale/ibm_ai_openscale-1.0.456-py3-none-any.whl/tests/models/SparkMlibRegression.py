# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os


def get_model_data():
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import RFormula
    from pyspark.ml.regression import LinearRegression
    from pyspark.ml import Pipeline

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

    return {
        'model': lr_model,
        'pipeline': pipeline_lr,
        'training_data': train_data,
        'test_data': test_data,
        'prediction': lr_predictions
    }


def get_scoring_payload():
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
