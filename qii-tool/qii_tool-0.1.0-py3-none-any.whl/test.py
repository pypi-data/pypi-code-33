# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 10:17:09 2019

@author: hxvin
"""

from qii import QII
from predictor import QIIPredictor
from qoi import QuantityOfInterest

from sklearn.linear_model import LogisticRegression
from sklearn import datasets

iris = datasets.load_iris()
X = iris.data[:, 0:2]  # we only take the first two features for visualization
y = iris.target

n_features = X.shape[1]

classifier = LogisticRegression(C=10, penalty='l1',
                                      solver='saga',
                                      multi_class='multinomial',
                                      max_iter=10000)

classifier.fit(X, y)

class LRPredictor(QIIPredictor):
    def __init__(self, predictor):
        super(LRPredictor, self).__init__(predictor)
        
    def predict(self, x):
        return self._predictor.predict(x) 
    
lr_predictor = LRPredictor(classifier)
quantity_of_interest = QuantityOfInterest()
qii = QII(X, n_features, quantity_of_interest)


shapley_vals =  qii.compute(x_0=X[0:1], predictor=lr_predictor, 
                            show_approx=True, evaluated_features=None,
                            data_exhaustive=True, feature_exhaustive=True,
                            method='shapley')
print ('Shapley: \n{0}'.format(shapley_vals))



banzhaf_vals =  qii.compute(x_0=X[0:1], predictor=lr_predictor, 
                            show_approx=True, evaluated_features=None,
                            data_exhaustive=True, feature_exhaustive=True,
                            method='banzhaf')

print ('Banzhaf: \n{0}'.format(banzhaf_vals))
