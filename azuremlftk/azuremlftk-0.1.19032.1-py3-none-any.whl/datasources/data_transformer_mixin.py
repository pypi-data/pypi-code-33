import abc
import pandas as pd
from datetime import datetime
from ftk.base_estimator import AzureMLForecastTransformerBase

class DataTransformerMixin(AzureMLForecastTransformerBase, metaclass=abc.ABCMeta):
    """
    The abstract class which Mix in the data transformation methods.
    The class describe the interface of a transformer which takes the data from the 
    different data sources and converts it to the pandas.DataFrame.
    Data source transforms accept any, or no, input.
    They ignore it and return whatever data their parameters tell them to produce.
      
    :param run_tag: The run tag to be used in the given transformation.
                    *Note* The run_tag used in the constructor is not used! Set run_tag in the transform method.
    :type run_tag: str
     
    """
    TAG_FIELD='RUN_TAG'
    TAG_VAR = 'run_tag'
    TAG_MAX_LENGTH = 255
      
    def __init__(self, run_tag=None):
        """
        Constructor.
        """
        self.run_tag=run_tag
        self._run_tag_set_by_user = not run_tag is None
  
    def fit(self, X, y):
        """
          Does nothing.
      
        """
        pass

    def predict(self, X, **kwargs):
        """
        Does nothing.
          
        """
        pass

    def fit_transform(self, X=None, y=None, **kwargs):
        """
          Returns the data read from the data source in form of pandas.DataFrame
          
          :param X: data frame to be fitted
          :type X: DataFrame
          :param y: fitting parameter (ignored).
          :type y: str
          :returns: the table with data.
          :rtype: pandas.DataFrame
          
        """
        return self.transform(X, **kwargs)

    @abc.abstractmethod
    def transform(self, X=None, **kwargs):
        """
        Returns the data read from the data source in form of pandas.DataFrame
          
        :param X: data frame to be fitted
        :type X: pandas.DataFrame
        :returns: the table with data.
        :rtype: pandas.DataFrame
          
        """
        raise NotImplementedError
  
    @property
    def run_tag(self):
        """
        Get or set run_tag.
        
        :rtype: str
        
        """
        #This method is required for setting of the parameter for pipeline.
        return self._run_tag
    
    @run_tag.setter
    def run_tag(self, val):
        """
        Setter.
        
        """
        DataTransformerMixin.check_run_tag(**{DataTransformerMixin.TAG_VAR:val})
        self._run_tag = val
        self._run_tag_set_by_user = True
    
    def set_tag_from_params(self, **kwargs):
        """
        If kwargs contains the run_tag variable, set ti to the run_tag and define it as user-set.
        If kwargs DOES NOT contain run_tag, but there is already user set run_tag, do nothing.
        If kwargs DOES NOT contain run_tag and there is no user set run_tag, set timestamp as run_tag do not mark it as user set.
        If it is not there, return the pandas timestamp, converted to string,.
        Set the last used run tag value. 
        If the length of a run_tag is more then DataTransformerMixin.TAG_MAX_LENGTH symbols thew ValueError is raised.
        
        :param run_tag: The run tag to be used in the given transformation.
        :param run_tag: str
        :raises: ValueError
        
        """
        if not kwargs.get(DataTransformerMixin.TAG_VAR) is None:
            run_tag = kwargs.get(DataTransformerMixin.TAG_VAR)
            self.run_tag = run_tag
        else:
            if not self._run_tag_set_by_user:
                self.run_tag = str(pd.to_datetime(datetime.now()))
                self._run_tag_set_by_user = False
    
    @staticmethod
    def check_run_tag(**kwargs):
        """
        Riase ValueError if run_tag is longer then DataTransformerMixin.TAG_MAX_LENGTH symbols.
        
        :raises: ValueError
        
        """
        if not kwargs.get(DataTransformerMixin.TAG_VAR) is None and len(kwargs.get(DataTransformerMixin.TAG_VAR))>DataTransformerMixin.TAG_MAX_LENGTH:
            raise ValueError("run_tag can not be longer then {} symbols.".format(DataTransformerMixin.TAG_MAX_LENGTH))