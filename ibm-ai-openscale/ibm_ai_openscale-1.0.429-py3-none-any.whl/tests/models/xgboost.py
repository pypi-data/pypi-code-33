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
import random
import xgboost as xgb
import scipy
from scipy import sparse


class Agaricus(AbstractModel):
    model_name = "AIOS Xgboost Agaricus Model"
    deployment_name = "AIOS Xgboost Agaricus Deployment"

    model_path = os.path.join(os.getcwd(), 'artifacts', 'XGboost', 'xgboost_model.tar.gz')

    labels = []
    row = []
    col = []
    dat = []
    i = 0

    with open(os.path.join(os.getcwd(), 'datasets', 'XGboost', 'agaricus.txt.test')) as f:
        for l in f:
            arr = l.split()
            labels.append(int(arr[0]))
            for it in arr[1:]:
                k, v = it.split(':')
                row.append(i)
                col.append(int(k))
                dat.append(float(v))
            i += 1
        csr = scipy.sparse.csr_matrix((dat, (row, col)))

        # inp_matrix = xgb.DMatrix(csr)

    def publish_to_wml(self, wml_client):
        return wml_client.repository.store_model(model=self.model_path, meta_props=self.get_model_props(wml_client))

    def get_model_props(self, wml_client):
        return {
            wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            wml_client.repository.ModelMetaNames.NAME: self.model_name,
            wml_client.repository.ModelMetaNames.FRAMEWORK_NAME: "xgboost",
            wml_client.repository.ModelMetaNames.FRAMEWORK_VERSION: "0.6",
            wml_client.repository.ModelMetaNames.TRAINING_DATA_SCHEMA: self.get_training_data_schema()
        }

    def get_scoring_payload(self):
        random_row = random.randint(0, self.csr.get_shape()[0]-1)

        return {
            'values': self.csr.getrow(random_row).toarray().tolist()
        }

    def get_training_data_schema(self):
        field = lambda x: {"name": "f" + str(x), "type": "float"}
        label = lambda x: {"name": "l" + str(x), "type": "float"}
        fields = [field(i) for i in range(127)]
        labels = [label(i) for i in range(1)]

        return {
            "features": {
                "type": "ndarray",
                "fields": fields
            },
            "labels": {
                "type": "ndarray",
                "fields": labels
            }
        }

    def get_feedback_payload(self):
        random_row = random.randint(0, self.csr.get_shape()[0] - 1)

        payload = self.csr.getrow(random_row).toarray().tolist()[0]
        payload.append(self.labels[random_row])
        return {
            'values': payload
        }
