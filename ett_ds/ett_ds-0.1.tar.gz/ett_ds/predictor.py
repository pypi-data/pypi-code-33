#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Emerging Technologies Team Core Library for Predictions

Contains methods that are called to perform certain predictive functions on models
"""

__author__ = "Kevin Thomas Bradley"
__copyright__ = "Copyright 2019, United Nations OICT PSGD ETT"
__credits__ = ["Kevin Bradley", "Yihan Bao", "Praneeth Nooli"]
__date__ = "07 February 2019"
__version__ = "0.1"
__maintainer__ = "Kevin Thomas Bradley"
__email__ = "bradleyk@un.org"
__status__ = "Development"

# Wrapper Class
class Predictor:
    
    ## TODO some form of verification that the model of this type can 'predict'
    # This function calls the predict function on the model
    # @param model Object of type model to perform prediction on
    # @param dataFrame DataFrame of the cleansed and transformed data
    # @returns DataFrame housing 0 OR 1
    @staticmethod
    def perform_model_predictions(model, dataFrame): 
        return model.predict(dataFrame)
 
    ## TODO some form of verification that the model of this type can 'predict' probabilities
    # This function calls the predict probabilities function on the model
    # @param model Object of type model to perform proba prediction on
    # @param dataFrame DataFrame of the cleansed and transformed data
    # @returns DataFrame housing 0.0 > 1.0
    @staticmethod
    def perform_model_prob_predictions(model, dataFrame): 
        return model.predict_proba(dataFrame)

        

