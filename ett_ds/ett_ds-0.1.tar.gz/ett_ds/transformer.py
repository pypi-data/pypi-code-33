#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Emerging Technologies Team Core Library for Transformation Functions

Contains methods that are used to transform data in some way
"""

import nltk
from textblob import Word
nltk.data.path.append("/Users/kevin/Desktop/unisdr/nltk_data")

__author__ = "Kevin Thomas Bradley"
__copyright__ = "Copyright 2019, United Nations OICT PSGD ETT"
__credits__ = ["Kevin Bradley", "Yihan Bao", "Praneeth Nooli"]
__date__ = "07 February 2019"
__version__ = "0.1"
__maintainer__ = "Kevin Thomas Bradley"
__email__ = "bradleyk@un.org"
__status__ = "Development"

# Wrapper Class
class Transformer:
    
    ## TODO some form of verification to check parameters are not null or empty
    # This function simply concatinates columns 
    # @param colnames Tuple of column names as Strings
    # @param data DataFrame of the original data to subset and concat
    # @returns concat_cols DataFrame of concatinated columns imto a single column
    @staticmethod
    def concatinate_data_columns(colnames, data):
        concat_cols = data[colnames].apply(lambda x: ''.join(x), axis=1)
        return concat_cols

    ## TODO some form of verification to check text is not empty?
    # This function simply transforms text to lowercase
    # @param text String input text
    # @returns String lowercased text
    @staticmethod
    def lowercase(text):
        text = text.apply(lambda x: " ".join(x.lower() for x in x.split()))  
        return text

    ## TODO some form of verification to check text is not empty?
    # This function simply transforms text morphologically by removing inflectional endings
    # for instance cats > cat
    # @param text String input text
    # @returns String rooted text
    @staticmethod
    def lemmatization(text):
        text = text.apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
        return text

    ## TODO some form of verification that the model of this type can 'transform' data
    # This function simply calls the transform method of the model object
    # Method using these calculated parameters apply the transformation to a particular dataset
    # @param model Object representing a model
    # @param dataFrame DataFrame to be used to transform
    # @returns concat_cols DataFrame of concatinated columns imto a single column   
    # @see sklearn.transform()
    @staticmethod
    def perform_model_transformation(model, dataFrame):
        return model.transform(dataFrame)
        

