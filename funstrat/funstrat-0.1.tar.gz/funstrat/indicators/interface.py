import pandas as pd
from copy import deepcopy

# TODO: Move dataframe to
class Indicator(object):
    def __init__(self):
        pass

    def set_ta_params(self, **kwargs):
        """ 
            Set TA indicators.
            Allows the user to set things like buy/sell conditions
        """

        raise NotImplementedError

    def _run_ta(self):
        """ Run the technical analysis here """
        raise NotImplementedError
    
    def process(self, dataframe):
        """ Process the TA"""
        raise NotImplementedError
