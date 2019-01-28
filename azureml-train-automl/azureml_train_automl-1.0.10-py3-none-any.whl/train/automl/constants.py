# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Various constants used throughout Automated Machine Learning."""

from automl.client.core.common.constants import (
    MODEL_PATH,
    MODEL_PATH_TRAIN,
    ENSEMBLE_PIPELINE_ID,
    Defaults,
    RunState,
    API,
    AcquisitionFunction,
    Status,
    PipelineParameterConstraintCheckStatus,
    OptimizerObjectives,
    Optimizer,
    Tasks as CommonTasks,
    ClientErrors,
    ServerStatus,
    TimeConstraintEnforcement,
    PipelineCost,
    Metric,
    MetricObjective,
    TrainingType,
    NumericalDtype,
    TextOrCategoricalDtype,
    TrainingResultsType,
    get_metric_from_type,
    get_status_from_type,
)


class SupportedAlgorithms:
    """Names for all algorithms supported by AutoML."""

    LogisticRegression = 'LogisticRegression'
    SGDClassifier = 'SGDClassifierWrapper'
    MultinomialNB = 'NBWrapper'
    BernoulliNB = 'NBWrapper'
    SupportVectorMachine = 'SVCWrapper'
    LinearSupportVectorMachine = 'LinearSVMWrapper'
    KNearestNeighborsClassifier = 'KNeighborsClassifier'
    DecisionTree = 'DecisionTreeClassifier'
    RandomForest = 'RandomForestClassifier'
    ExtraTrees = 'ExtraTreesClassifier'
    LightGBMClassifier = 'LightGBMClassifier'
    ElasticNet = 'ElasticNet'
    GradientBoostingRegressor = 'GradientBoostingRegressor'
    DecisionTreeRegressor = 'DecisionTreeRegressor'
    KNearestNeighborsRegressor = 'KNeighborsRegressor'
    LassoLars = 'LassoLars'
    SGDRegressor = 'SGDRegressor'
    RandomForestRegressor = 'RandomForestRegressor'
    ExtraTreesRegressor = 'ExtraTreesRegressor'
    TensorFlowDNNClassifier = 'TensorFlowDNN'
    TensorFlowLinearClassifier = 'TensorFlowLinearClassifier'
    TensorFlowLinearRegressor = 'TensorFlowLinearRegressor'
    TensorFlowDNNRegressor = 'TensorFlowDNN'
    # To be deprecated soon
    _KNN = 'kNN'
    _SVM = 'SVM'
    _KNNRegressor = 'kNN regressor'

    ALL = {
        LogisticRegression,
        SGDClassifier,
        MultinomialNB,
        BernoulliNB,
        SupportVectorMachine,
        LinearSupportVectorMachine,
        KNearestNeighborsClassifier,
        DecisionTree,
        RandomForest,
        ExtraTrees,
        LightGBMClassifier,
        ElasticNet,
        GradientBoostingRegressor,
        DecisionTreeRegressor,
        KNearestNeighborsRegressor,
        LassoLars,
        SGDRegressor,
        RandomForestRegressor,
        ExtraTreesRegressor,
        _KNN,
        _SVM,
        _KNNRegressor}


MODEL_EXPLANATION_TAG = "model_explanation"

MAX_ITERATIONS = 1000
MAX_SAMPLES_BLACKLIST = 5000
MAX_SAMPLES_BLACKLIST_ALGOS = [SupportedAlgorithms.KNearestNeighborsClassifier,
                               SupportedAlgorithms.KNearestNeighborsRegressor,
                               SupportedAlgorithms.SupportVectorMachine,
                               SupportedAlgorithms._KNN,
                               SupportedAlgorithms._KNNRegressor,
                               SupportedAlgorithms._SVM]

ADBCACHEDIRECTORY = "/dbfs/AutoMLRuns/"

Sample_Weights_Unsupported = {
    """Names of algorithms that do not support sample weights."""
    'Elastic net',
    'kNN',
    'Lasso lars',
    SupportedAlgorithms.ElasticNet,
    SupportedAlgorithms.KNearestNeighborsClassifier,
    SupportedAlgorithms.KNearestNeighborsRegressor,
    SupportedAlgorithms.LassoLars
}


TrainingType.FULL_SET.remove(TrainingType.TrainValidateTest)


class ComputeTargets:
    """Names of compute targets supported by AutoML."""

    DSVM = 'VirtualMachine'
    BATCHAI = 'BatchAI'
    AMLCOMPUTE = 'AmlCompute'


class TimeSeries:
    """Parameters used for timeseries."""

    TIME_COLUMN_NAME = 'time_column_name'
    GRAIN_COLUMN_NAMES = 'grain_column_names'
    DROP_COLUMN_NAMES = 'drop_column_names'


class Tasks(CommonTasks):
    """A subclass of Tasks in common.core, extendable to more task types for SDK."""

    CLASSIFICATION = CommonTasks.CLASSIFICATION
    REGRESSION = CommonTasks.REGRESSION
    FORECASTING = 'forecasting'
    ALL = [CommonTasks.CLASSIFICATION, CommonTasks.REGRESSION, FORECASTING]
