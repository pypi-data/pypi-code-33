import pandas as pd
from .base import BaseBlock




class IndicatorBlock(BaseBlock):
    def __init__(self):
        pass
        # if not isinstance(dataframe, pd.DataFrame):
        #     raise TypeError("Should add dataframe")
        # self.df = dataframe

    def set_ta_params(self, **kwargs):
        """ 
            Set TA indicators.
            Allows the user to set things like buy/sell conditions
        """

        raise NotImplementedError

    def _run_ta(self):
        """ Run the technical analysis here """
        raise NotImplementedError
    
    def process(self):
        """ Process the TA and return the solution. """
        raise NotImplementedError
    

class MachineLearningBlock(BaseBlock):
    def __init__(self):
        """ 
            ML Block:
            ---
            Processing block here is used to do machine learning with the indicators.
            Calls outside interface to process data. It would get an appended pandas dataframe or (dask) to train a block.
            Prior to training the model, we will check to see if we have the necessary data to predict input and output
        """
    
    def _check_dataset(self, dataset_bag):
        """ Gets a dask bag to check for dataset information. Can use to turn into a dataframe after converting"""
        raise NotImplementedError
    
    def process(self):
        raise NotImplementedError