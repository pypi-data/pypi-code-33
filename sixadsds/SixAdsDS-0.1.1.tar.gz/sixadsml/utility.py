"""
Utility functions
"""

import yaml
from sqlalchemy import create_engine

def make_connection(specs):
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                       .format(user=specs['user'],
                               pw=specs['password'],
                               host = specs['host'],
                               db=specs['db']))
    return(engine)

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
    
    return list(l)    