#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Basic utility functions for ditto_lib
#

from scipy import spatial
from sklearn import metrics
from math import sqrt

### UTIL METHODS ###

def rmse(predictions, targets):
    '''
    Return the root mean squared error value given an array of 
    predicted values and an array of target values
    '''
    score = 0
    counter = 0
    for prediction, target in zip(predictions, targets):
        score += sqrt((prediction - target) ** 2)
        counter += 1
    return score / counter

def percent_error(prediction, target):
    '''
    Return the percent error of a predicted value compared
    to a target value 
    '''
    if (prediction == target):
        return 0
    else:
        return ( abs(prediction - target) / max(prediction, target)) * 100

def manhattan_distance(x,y):
    '''
    Return the manhattan distance between an input
    feature set when compared to another feature set
    '''
    if len(x) != len(y):
        raise ValueError("{} is not the same length as {}".format(x, y))
    else:
        return sum(abs(a-b) for a,b in zip(x,y))

def stdev(values):
    '''
    Return the standard deviation for the given
    list of values
    '''
    mean = 0
    result = 0
    for value in values:
        mean += value
    mean /= len(values)
    for value in values:
        result += ( (value - mean) **2)
    return sqrt(result / len(values))

### UTIL FUNCTION DICTS ###

error_dict = {
    'mse' : metrics.mean_squared_error,
    'evs' : metrics.explained_variance_score,
    'msle' : metrics.mean_squared_log_error,
    'r2' : metrics.r2_score
}

similarity_dict = {
    'euc' : spatial.distance.euclidean,
    'man' : manhattan_distance,
    'jac' : spatial.distance.jaccard,
    'cos' : spatial.distance.cosine
}