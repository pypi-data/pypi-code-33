"""numtype contains functions for checking the type of number that is contained within a string.
"""

def str_is_float(numeric_string):
    """Returns true if the string is a float
    
    Arguments:
        string {str} -- String representing a number
    
    Returns:
        bool -- True if the string is a float
    """
    is_float = False
    if numeric_string:
        if numeric_string.replace('.','',1).replace('-','',1).isdigit():
            is_float = True
    return is_float

def str_is_int(numeric_string):
    """Returns true if the string is an integer
    
    Arguments:
        string {str} -- String representing a number
    
    Returns:
        bool -- True if the string is an integer
    """
    is_int = False
    if numeric_string:
        if numeric_string.replace('-','',1).isdigit():
            is_int = True
    return is_int

def str_is_pos_float(numeric_string):
    """Returns true if the string is a positive float
    
    Arguments:
        string {str} -- String representing a number
    
    Returns:
        bool -- True if the string is a positive float
    """
    is_float = False
    if numeric_string:
        if numeric_string.replace('.','',1).isdigit():
            is_float = True
    return is_float

def str_is_pos_int(numeric_string):
    """Returns true if the string is a positive integer
    
    Arguments:
        string {str} -- String representing a number
    
    Returns:
        bool -- True if the string is a positive integer
    """
    is_int = False
    if numeric_string:
        if numeric_string.isdigit():
            is_int = True
    return is_int