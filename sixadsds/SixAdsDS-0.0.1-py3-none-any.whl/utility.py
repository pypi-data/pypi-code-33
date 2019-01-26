"""
Utility functions
"""

import yaml
import pymysql

def make_connection(specs):
    connection = pymysql.connect(host = specs['host'], 
                             user = specs['user'], 
                             password = specs['password'],
                             db = specs['db'])
    return(connection)

def exec_file(file, add_params = None):
    """
    Executes a file 
    """
    if add_params is not None:
        exec(open(file).read(), add_params)
    else:
        exec(open(file).read())

def read_yaml(file):
    """
    A function to read a yaml file as a dictionary
    """
    with open(file, 'r') as f:
        d = yaml.load(f)
    
    return d    
        
def chunks_of_n(l, n):
    """
    Split an item into chunks of size n
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]