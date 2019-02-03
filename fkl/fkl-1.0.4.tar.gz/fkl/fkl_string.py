# -*- coding: utf-8 -*-
"""
This is a submodule of fk_lib.
The moudle contains several functions to process string.
"""
import re
import json

def FKLEditDist(str1,str2):
    """
    Args:
        str1: Just a string.
        str2: Just another string.
    Returns:
        Return a integer that represent hamming distance of st1 and str2.
    Raises:
        None
    """
    len_str1 = len(str1) + 1  
    len_str2 = len(str2) + 1  
    matrix = [0 for n in range(len_str1 * len_str2)]  
    for i in range(len_str1):  
        matrix[i] = i  
    for j in range(0, len(matrix), len_str1):  
        if j % len_str1 == 0:
            matrix[j] = j // len_str1  
    for i in range(1, len_str1):  
        for j in range(1, len_str2):  
            if str1[i-1] == str2[j-1]:  
                cost = 0  
            else:  
                cost = 1  
            matrix[j*len_str1+i]=min(matrix[(j-1)*len_str1+i]+1,matrix[j*len_str1+(i-1)]+1,
                                     matrix[(j-1)*len_str1+(i-1)] + cost)  
    return matrix[-1]   
def FKLSplit(string,key):
    """
    Args:
        string: To be split string.
        key: A string that represent key of split.
    Returns:
        Return a list that contains several period string but not contains escape
        and newline character.
    Raises:
        Exception: The args string and key must be str.
    """
    if(type(string)!=str or type(key)!=str):
        raise Exception("FKLSplit Error: The args string and key must be str.")
    period_str=string.split(key)
    period_str=list(map(lambda s:s.strip(),period_str))
    return period_str
def FKLReplaceSubStr(string,replace_str,regex_pattern):
    """
    Args:
        string: To be split string.
        replace_str: A string of to be replaced.
        regex_pattern: A string of regex pattern.
    Returns:
        Return a replaced string.
    Raises:
        None
    """
    new_string=re.sub(regex_pattern,replace_str,string)
    return new_string
def FKLEncodeJsonStr(arg):
    return json.dumps(arg)
def FKLdecodeJsonStr(json_str):
    return json.loads(json_str)
