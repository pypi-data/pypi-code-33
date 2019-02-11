# -*- coding: utf-8 -*-
"""
This is the  "neater.py" module and it provides one function called print_lol()
which prints lists that may or may not include neseted lists.

"""

def print_lol(the_list, level):
    """
    This function takes one postional argument called "the list", which
    is any python list(of - possibly - nested lists). Each data item in the
    provided list is(recuraively) printed to the screen on in's own line.
    The second parameter is used to insert tabs when a nested list is
    encountered.
    
    """
    
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end = '')
            print(each_item)

