"""This module is a custom module designed for general use in the Omnis project.
"""


def reverse_dict(input_dict):
    """This function returns a dictionary with input_dict's key, value is reversed.
    
    Arguments:
        input_dict {dict} -- Dictionary to reverse.
    
    Returns:
        [dict] -- Reversed dictionary.
    """
    reversed_dict = {}
    key_list = list(input_dict.keys())
    for index, val in enumerate( list(input_dict.values()) ):
        reversed_dict[val] = key_list[index]
    return reversed_dict
