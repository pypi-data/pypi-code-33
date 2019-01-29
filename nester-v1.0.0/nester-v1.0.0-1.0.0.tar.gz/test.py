# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 23:23:06 2019

@author: alexie666
"""
"""Thisfunction can print any nested list on the screen with each data on the line"""

def print_list(the_list, indent=False, level = 0):
    for nested_list in the_list:
        if isinstance(nested_list, list):
            print_list(nested_list, indent, level+1)
        else:
            if indent:
                for indent in range(level):
                    print("\t", end='')    
            print(nested_list)
            
                
                
            
            