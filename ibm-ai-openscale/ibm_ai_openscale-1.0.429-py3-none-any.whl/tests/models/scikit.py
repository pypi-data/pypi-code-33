# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os
from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn import preprocessing
from sklearn import decomposition
from sklearn import svm
from .AbstractModel import AbstractModel


class Digit(AbstractModel):

    model_name = "AIOS Spark Digits Model"
    deployment_name = "AIOS Spark Digits Deployment"

    def __init__(self):
        self.model_data = datasets.load_digits()
        scaler = preprocessing.StandardScaler()
        clf = svm.SVC(kernel='rbf')
        self.pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
        self.model = self.pipeline.fit(self.model_data.data, self.model_data.target)
        self.predicted = self.model.predict(self.model_data.data[1: 10])

    def publish_to_wml(self, wml_client):
        return wml_client.repository.store_model(model=self.model, meta_props=self.get_model_props(wml_client), training_data=self.model_data.data, training_target=self.model_data.target)

    def get_model_props(self, wml_client):
        return {
            wml_client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
            wml_client.repository.ModelMetaNames.NAME: self.model_name,
            wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: {},
            wml_client.repository.ModelMetaNames.EVALUATION_METHOD: "multiclass",
            wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                {
                    "name": "accuracy",
                    "value": 0.64,
                    "threshold": 0.8
                }
            ]
        }

    def get_scoring_payload(self):
        return {
           "values": [
              [
                 0.0,
                 0.0,
                 5.0,
                 16.0,
                 16.0,
                 3.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 9.0,
                 16.0,
                 7.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 12.0,
                 15.0,
                 2.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 1.0,
                 15.0,
                 16.0,
                 15.0,
                 4.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 9.0,
                 13.0,
                 16.0,
                 9.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 14.0,
                 12.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 5.0,
                 12.0,
                 16.0,
                 8.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 3.0,
                 15.0,
                 15.0,
                 1.0,
                 0.0,
                 0.0
              ],
              [
                 0.0,
                 0.0,
                 6.0,
                 16.0,
                 12.0,
                 1.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 5.0,
                 16.0,
                 13.0,
                 10.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 5.0,
                 5.0,
                 15.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 8.0,
                 15.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 13.0,
                 13.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 0.0,
                 6.0,
                 16.0,
                 9.0,
                 4.0,
                 1.0,
                 0.0,
                 0.0,
                 3.0,
                 16.0,
                 16.0,
                 16.0,
                 16.0,
                 10.0,
                 0.0,
                 0.0,
                 5.0,
                 16.0,
                 11.0,
                 9.0,
                 6.0,
                 2.0
              ]
           ]
        }


def create_scikit_learn_model_data(model_name='digits'):
    from sklearn import datasets
    from sklearn.pipeline import Pipeline
    from sklearn import preprocessing
    from sklearn import decomposition
    from sklearn import svm

    global model_data
    global model

    if model_name == 'digits':
        model_data = datasets.load_digits()
        scaler = preprocessing.StandardScaler()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
        model = pipeline.fit(model_data.data, model_data.target)
        predicted = model.predict(model_data.data[1: 10])
    if model_name == 'iris':
        model_data = datasets.load_iris()
        pca = decomposition.PCA()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('pca', pca), ('svc', clf)])
        model = pipeline.fit(model_data.data, model_data.target)
        predicted = model.predict(model_data.data[1: 10])

    return {
        'model': model,
        'pipeline': pipeline,
        'training_data': model_data.data,
        'training_target': model_data.target,
        'prediction': predicted
    }


def get_digits_model_data():
    return _get_model_data('digits')


def get_iris_model_data():
    return _get_model_data('iris')


def _get_model_data(model_name='digits'):
    from sklearn import datasets
    from sklearn.pipeline import Pipeline
    from sklearn import preprocessing
    from sklearn import decomposition
    from sklearn import svm

    global model_data
    global model

    if model_name == 'digits':
        model_data = datasets.load_digits()
        scaler = preprocessing.StandardScaler()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
        model = pipeline.fit(model_data.data, model_data.target)
        predicted = model.predict(model_data.data[1: 10])
    if model_name == 'iris':
        model_data = datasets.load_iris()
        pca = decomposition.PCA()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('pca', pca), ('svc', clf)])
        model = pipeline.fit(model_data.data, model_data.target)
        predicted = model.predict(model_data.data[1: 10])

    return {
        'model': model,
        'pipeline': pipeline,
        'training_data': model_data.data,
        'training_target': model_data.target,
        'prediction': predicted
    }


def get_digits_scoring_payload():
    return {"values": [
        [
            0.0,
            0.0,
            5.0,
            16.0,
            16.0,
            3.0,
            0.0,
            0.0,
            0.0,
            0.0,
            9.0,
            16.0,
            7.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            12.0,
            15.0,
            2.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            15.0,
            16.0,
            15.0,
            4.0,
            0.0,
            0.0,
            0.0,
            0.0,
            9.0,
            13.0,
            16.0,
            9.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            14.0,
            12.0,
            0.0,
            0.0,
            0.0,
            0.0,
            5.0,
            12.0,
            16.0,
            8.0,
            0.0,
            0.0,
            0.0,
            0.0,
            3.0,
            15.0,
            15.0,
            1.0,
            0.0,
            0.0
        ],
        [
            0.0,
            0.0,
            6.0,
            16.0,
            12.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            5.0,
            16.0,
            13.0,
            10.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            5.0,
            5.0,
            15.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            8.0,
            15.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            13.0,
            13.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            6.0,
            16.0,
            9.0,
            4.0,
            1.0,
            0.0,
            0.0,
            3.0,
            16.0,
            16.0,
            16.0,
            16.0,
            10.0,
            0.0,
            0.0,
            5.0,
            16.0,
            11.0,
            9.0,
            6.0,
            2.0
        ]
    ]
    }
