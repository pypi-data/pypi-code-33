# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from .AbstractModel import AbstractModel
import os


class CustomerSatisfactionPrediction(AbstractModel):
    model_name = "AIOS SPSS Customer Model"
    deployment_name = "AIOS SPSS Customer Deployment"

    model_path = os.path.join(os.getcwd(), 'artifacts', 'SPSSCustomerSatisfaction', 'customer-satisfaction-prediction.str')

    def publish_to_wml(self, wml_client):
        return wml_client.repository.store_model(model=self.model_path, meta_props=self.get_model_props(wml_client))

    def get_model_props(self, wml_client):
        return {
            wml_client.repository.ModelMetaNames.NAME: self.model_name,
            wml_client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
            wml_client.repository.ModelMetaNames.FRAMEWORK_NAME: "spss-modeler",
            wml_client.repository.ModelMetaNames.FRAMEWORK_VERSION: "18.0",
            wml_client.repository.ModelMetaNames.RUNTIME_NAME: "spss-modeler",
            wml_client.repository.ModelMetaNames.RUNTIME_VERSION: "18.0"
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
                "MonthlyCharges",
                "TotalCharges",
                "Churn",
                "SampleWeight"
            ],
            "values": [
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
                    59.9,
                    3505.1,
                    "No",
                    2.768
                ]
            ]
        }