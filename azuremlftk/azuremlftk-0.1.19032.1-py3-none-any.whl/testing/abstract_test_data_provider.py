import abc

class AbstractTestDataProvider(abc.ABC):
    """.. py:class:: AbstractTestDataProvider
    The class AbstractDataProvider creates the interface of data access for ForecastingToolkit
    unit and integrity tests.
    These classes should represent the singletons which read the data once and provide or by request.
    """
    _instances = {}
    
    def __init__(self):
        """Empty Constructor.
        Create placeholders for the data.
        """
        self.validate_ts = None
        self.score_context_validate = None
        self.test_ts = None
        self.train_ts = None
        self.test_fcast = None
        self.score_context_train_predict = None
        self.score_context_train_only = None
        self.score_context_predict_only = None
        self.df_test=None
    
    @classmethod
    def get_instance(cls):
        """.. py:classmethod:: 
        Return the instance of a given TestDataProvider
        Create the class and store it in the dictionary of instances.
        """
        if not cls in AbstractTestDataProvider._instances.keys():
            AbstractTestDataProvider._instances[cls] = cls()
        return AbstractTestDataProvider._instances.get(cls)
    
    @property
    def training_tsdf(self):
        """.. py:method:: training_tsdf()
        Return the training data set in the TimeSeriesDataFrame
        :returns: training data set.
        :rtype: TimeSeriesDataFrame.
        """
        return self.train_ts.copy()
    
    @property
    def testing_mdf(self):
        """.. py:method:: testing_fdf()
        Return the training data set in the pandas.DataFrame
        :returns: training data set.
        :rtype: ForecastDataFrame
        """
        return self._mcast_df.copy()
    
    @property
    def testing_fdf(self):
        """.. py:method:: testing_fdf()
        Return the training data set in the pandas.DataFrame
        :returns: training data set.
        :rtype: ForecastDataFrame
        """
        return self.test_fcast.copy()
        
    @property
    def testing_tsdf(self):
        """.. py:method:: testing_tsdf()
        Return the training data set in the TimeSeriesDataFrame
        :returns: training data set.
        :rtype: TimeSeriesDataFrame.
        """
        return self.test_ts.copy()
    
    @property
    def testing_df(self):
        """.. py:method:: testing_df()
        Return the training data set in the pandas.DataFrame
        :returns: training data set.
        :rtype: pandas.DataFrame.
        """
        return self.df_test.copy()
    
    @property
    def prediction_score_context(self):
        """.. py:method:: prediction_score_context()
        Return the ScoreContext for prediction only.
        :returns: ScoreContext object for prediction.
        :rtype: ScoreContext.
        """
        return self.score_context_predict_only
    
    @property
    def training_score_context(self):
        """.. py:method:: prediction_score_context()
        Return the ScoreContext for training only.
        :returns: ScoreContext object for training.
        :rtype: ScoreContext.
        """
        return self.score_context_train_only
    
    @property
    def train_predict_score_context(self):
        """.. py:method:: predict_score_context()
        Return the ScoreContext for prediction and training.
        :returns: ScoreContext object for prediction and training.
        :rtype: ScoreContext.
        """
        return self.score_context_train_predict
    
    @property
    def validate_score_context(self):
        """.. py:method:: validate_score_context()
        Return the ScoreContext for validation of a model.
        :returns: ScoreContext object for validation.
        :rtype: ScoreContext.
        """
        return self.score_context_validate
    
    @abc.abstractmethod
    def get_pipeline(self):
        """.. py:method:: get_pipeline()
        Return the fitted pipeline for the given example data.
        The pipeline implementation is dependent on the exact data provider.
        :returns: the pipeline.
        :rtype: AzureMLForecastPipeline.
        """
        raise NotImplementedError
    
    def get_empty_fdf(self):
        """.. py:method:: get_empty_fdf()
        Return the empty ForecastDataFrame which is used as a source of metadata to reconstruct the ScoringContext
        from not annotated data frames as TimeSeriesDataFrame and pandas.DataFrame.
        :returns: The empty data frame.
        :rtype: ForecastDataFrame.
        """
        if not self.test_fcast is None:
            return self.test_fcast.iloc[0:1]
        else:
            return None