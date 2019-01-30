"""Testing machine learning experiments
"""


import sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from ex4ml.objects.dataobject import DataObject
from ex4ml.ml import ml


def test_run_sl():

    data = load_iris()

    my_do = DataObject([DataObject(None, views={"feats": datum[0]}, targets={"species": datum[1]}) for datum in zip(data["data"], data["target"])])

    estimators = [
        {
            "name": "KNN",
            "estimator": KNeighborsClassifier(),
            "parameters": {'n_neighbors': [2, 5], 'weights':["uniform", "distance"]}
        },
        {
            "name": "SVM",
            "estimator": SVC(random_state=1),
            "parameters": {'kernel': ('linear', 'rbf'), 'C': [1, 10]}
        }
    ]

    latex, results = ml.run_sl(my_do, estimators, scoring="accuracy", target="species", view="feats")


def test_run_mv_sl():

    data = load_iris()

    my_do = DataObject([DataObject(None, views={"feats": datum[0], "less": datum[0][:2]}, targets={"species": datum[1]}) for datum in zip(data["data"], data["target"])])

    estimators = [
        {
            "name": "KNN",
            "estimator": KNeighborsClassifier(),
            "parameters": {'n_neighbors': [2, 5], 'weights':["uniform", "distance"]}
        },
        {
            "name": "SVM",
            "estimator": SVC(random_state=1),
            "parameters": {'kernel': ('linear', 'rbf'), 'C': [1, 10]}
        }
    ]

    latex, results = ml.run_mv_sl(my_do, estimators, scoring="accuracy", target="species", views=["feats", "less"])
