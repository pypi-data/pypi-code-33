#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Emerging Technologies Team Core Library for Data Cleansing Functions

Contains functions that focus on cleaning data
"""

import enchant
import nltk
from nltk.corpus import stopwords
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
class Cleanser:
    
    ## TODO some form of verification to check parameters are not null or empty
    # This function is used to remove certain characters
    # from the DataFrame by using regular expressions
    # @param dataFrame DataFrame to be cleansed
    # @param regex String which represents the regex to find and replace with ''
    # @return DataFrame of the cleansed data
    @staticmethod
    def clean_dataframe_by_regex(dataFrame, regex):
        cleansed_data = dataFrame.str.replace(regex,'')
        return cleansed_data
 
    ## TODO some form of verification to check parameters are not null or empty
    # This function is used to remove non specific ISO words
    # from the DataFrame. For example non American English words
    # @param dataFrame DataFrame to be cleansed
    # @param iso String which represents the ISO code for the language.
    # @return DataFrame of the cleansed data
    # @see enchant.Dict() function used to construct a dictionary based on the iso code
    @staticmethod
    def remove_non_iso_words(dataFrame, iso):
        iso_dict = enchant.Dict(iso)
        dataFrame = dataFrame.apply(lambda x: " ".join(x for x in x.split() if iso_dict.check(x)))
        return dataFrame
    
    ## TODO some form of verification to check parameters are not null or empty
    # This function is used to remove language specific stopwords
    # from the DataFrame. For example the English word 'the'
    # @param dataFrame DataFrame to be cleansed
    # @param language String which represents the language
    # @return DataFrame of the cleansed data
    @staticmethod
    def remove_language_stopwords(dataFrame, language):
        stops = set(stopwords.words(language))
        sw_removed = dataFrame.apply(lambda x: " ".join(x for x in x.split() if x not in stops))
        return sw_removed



