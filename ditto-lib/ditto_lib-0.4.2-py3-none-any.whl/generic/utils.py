#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Basic utility functions for ditto_lib
#

from math import sqrt

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
        return 100 - ((min(prediction, target) / max(prediction, target)) * 100)

def euclidean(current, comparison):
    '''
    Return the euclidean distance between an input
    feature set when compared to another feature set
    '''
    score = 0
    if len(current) != len(comparison):
        raise ValueError("{} is not the same length as {}".format(current, comparison))
    else:
        for current_item, comparison_item in zip(current, comparison):
            score += (current_item - comparison_item) ** 2
        return sqrt(score)

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