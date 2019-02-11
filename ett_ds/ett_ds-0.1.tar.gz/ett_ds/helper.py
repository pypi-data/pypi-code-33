#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Emerging Technologies Team Core Library for General Helper Functions

Contains general helper based functions classes such as Enums and Exceptions
"""

import pandas as pd             # DataFrame management
import numpy as np              # Mathematical calcs
import pickle                   # Used for loading models
import sklearn                  # Used for model generation via pickle
from enum import Enum           # Used for custom Enums
from constants import Encoding  # Used to identify character encoding

__author__ = "Kevin Thomas Bradley"
__copyright__ = "Copyright 2019, United Nations OICT PSGD ETT"
__credits__ = ["Kevin Bradley", "Yihan Bao", "Praneeth Nooli"]
__date__ = "07 February 2019"
__version__ = "0.1"
__maintainer__ = "Kevin Thomas Bradley"
__email__ = "bradleyk@un.org"
__status__ = "Development"

# Base Error class
class Error(Exception):
   """ETT Base class for other custom exceptions"""
   pass

# Custom Error Class
class InvalidLabelsToModelsError(Error):
   """The number of labels does not match the number of expected corresponding models"""
   pass

# Wrapper Class 
class Helper:

    ## TODO some form of verification to check filename is not null or empty
    # This function is used to load a CSV file based on the 
    # filename and return this output.
    # @param filename The source file, as an string.
    # @return A DataFrame of the CSV file data.
    # @see OSError
    # @see Exception
    @staticmethod
    def load_csv(filename):
        try:
            return pd.read_csv(filename, encoding = Encoding.LATIN_1.value)
        except OSError as ose:
            print('Handle this by TODO: LOGGING it as an OSError somewhere ' + str(ose)) # TODO use some form of logging
        except Exception as e:
            print('Handle this by TODO: LOGGING it as a general exception somewhere' + str(e)) # TODO use some form of logging
    
    ## TODO some form of verification to check filename is not null or empty
    # This function is used to load a Model based on the 
    # filename and return this object.
    # @param filename The source file, as an string.
    # @return An Object which is the model.
    @staticmethod
    def load_model(filename):
        try:
            with open(filename, 'rb') as model_file:
                return pickle.load(model_file)
        except OSError as ose:
            print('Handle this by TODO: LOGGING it as an OSError somewhere ' + str(ose)) # TODO use some form of logging
        except Exception as e:
            print('Handle this by TODO: LOGGING it as a general exception somewhere' + str(e)) # TODO use some form of logging
        

    ## TODO some form of verification to check filename and delChar is not null or empty
    # This function is used to load data based on the delimiter
    # @param filename String file path
    # @param delChar Character delimiter
    # @returns Tuple of values
    @staticmethod
    def load_data_common_separated(filename, delChar):
        try:
            return pd.read_table(filename, delimiter=delChar)
        except OSError as ose:
            print('Handle this by TODO: LOGGING it as an OSError somewhere ' + str(ose)) # TODO use some form of logging
        except Exception as e:
            print('Handle this by TODO: LOGGING it as a general exception somewhere' + str(e)) # TODO use some form of logging
                               
    ## TODO some form of verification to check parameters is not null or empty
    # This function is used to create an empty DataFrame matching
    # the dimensions of the data expected to populate it
    # @param dataFrame DataFrame initial dataFrame
    # @param num Number of columns
    # @returns DataFrame with the correct dimensions 
    @staticmethod                     
    def provision_data_frame(dataFrame, num):
        provisioned_data = pd.DataFrame(np.zeros((len(dataFrame), num)))
        return provisioned_data

    ## TODO some form of verification to check parameters is not null or empty
    # Method used to create a DataFrame with the column names specified
    # @param dataFrame DataFrame of strings for each part of the path
    # @param colnames Tuple of strings with the column names
    # @returns DataFrame with the columns provisioned
    @staticmethod                   
    def provision_named_data_frame(dataFrame,colnames):
        provisioned_named_data = pd.DataFrame(dataFrame, columns=colnames)
        return provisioned_named_data

    ## TODO some form of verification to check parts size > 1
    # Method used to build a dynamic filepath
    # @param parts Tuple of strings for each part of the path
    # @returns String which is the combined file path
    @staticmethod
    def generate_dynamic_path(parts):
        return '/'.join(parts)


    



