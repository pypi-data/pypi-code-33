# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Various constants used throughout AutoML."""


# TODO deprecate this class since Miro has its own source of truth
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
    XGBoostClassifier = 'XGBoostClassifier'

    ElasticNet = 'ElasticNet'
    GradientBoostingRegressor = 'GradientBoostingRegressor'
    DecisionTreeRegressor = 'DecisionTreeRegressor'
    KNearestNeighborsRegressor = 'KNeighborsRegressor'
    LassoLars = 'LassoLars'
    SGDRegressor = 'SGDRegressor'
    RandomForestRegressor = 'RandomForestRegressor'
    ExtraTreesRegressor = 'ExtraTreesRegressor'
    XGBoostRegressor = 'XGBoostRegressor'

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


MODEL_PATH = "outputs/model.pkl"
MODEL_PATH_TRAIN = "outputs/model_train.pkl"
ENSEMBLE_PIPELINE_ID = "__AutoML_Ensemble__"
MAX_ITERATIONS = 1000
MAX_SAMPLES_BLACKLIST = 5000
MAX_SAMPLES_BLACKLIST_ALGOS = [SupportedAlgorithms.KNearestNeighborsClassifier,
                               SupportedAlgorithms.KNearestNeighborsRegressor,
                               SupportedAlgorithms.SupportVectorMachine,
                               SupportedAlgorithms._KNN,
                               SupportedAlgorithms._KNNRegressor,
                               SupportedAlgorithms._SVM]

"""Names of algorithms that do not support sample weights."""
Sample_Weights_Unsupported = {
    SupportedAlgorithms.ElasticNet,
    SupportedAlgorithms.KNearestNeighborsClassifier,
    SupportedAlgorithms.KNearestNeighborsRegressor,
    SupportedAlgorithms.LassoLars,
    SupportedAlgorithms._KNN,
}


class CustomerFacingSupportedModelNames:
    """Customer Facing Names for all algorithms supported by AutoML."""

    class ClassificationModelNames:
        """Classification model names."""

        LogisticRegression = 'LogisticRegression'
        SGDClassifier = 'SGD'
        MultinomialNB = 'MultinomialNaiveBayes'
        BernoulliNB = 'BernoulliNaiveBayes'
        SupportVectorMachine = 'SVM'
        LinearSupportVectorMachine = 'LinearSVM'
        KNearestNeighborsClassifier = 'KNN'
        DecisionTree = 'DecisionTree'
        RandomForest = 'RandomForest'
        ExtraTrees = 'ExtremeRandomTrees'
        LightGBMClassifier = 'LightGBM'
        GradientBoosting = 'GradientBoosting'
        TensorFlowDNNClassifier = 'TensorFlowDNN'
        TensorFlowLinearClassifier = 'TensorFlowLinearClassifier'
        XGBoostClassifier = 'XGBoost'

    class RegressionModelNames:
        """Regression Model Names."""

        ElasticNet = 'ElasticNet'
        GradientBoostingRegressor = 'GradientBoosting'
        DecisionTreeRegressor = 'DecisionTree'
        KNearestNeighborsRegressor = 'KNN'
        LassoLars = 'LassoLars'
        SGDRegressor = 'SGD'
        RandomForestRegressor = 'RandomForest'
        ExtraTreesRegressor = 'ExtremeRandomTrees'
        LightGBMRegressor = 'LightGBM'
        TensorFlowLinearRegressor = 'TensorFlowLinearRegressor'
        TensorFlowDNNRegressor = 'TensorFlowDNN'
        XGBoostRegressor = 'XGBoostRegressor'


class ModelClassNames:
    """Class names for models."""

    class ClassificationModelClassNames:
        """Classification model names."""

        LogisticRegression = 'LogisticRegression'
        SGDClassifier = 'SGDClassifierWrapper'
        MultinomialNB = 'NBWrapper'
        BernoulliNB = 'NBWrapper'  # BernoulliNB use NBWrapper as classname
        SupportVectorMachine = 'SVCWrapper'
        LinearSupportVectorMachine = 'LinearSVMWrapper'
        KNearestNeighborsClassifier = 'KNeighborsClassifier'
        DecisionTree = 'DecisionTreeClassifier'
        RandomForest = 'RandomForestClassifier'
        ExtraTrees = 'ExtraTreesClassifier'
        LightGBMClassifier = 'LightGBMClassifier'
        GradientBoosting = 'GradientBoostingClassifier'
        TensorFlowDNNClassifier = 'TFDNNClassifierWrapper'
        TensorFlowLinearClassifier = 'TFLinearClassifierWrapper'
        XGBoostClassifier = 'XGBoostClassifier'

    class RegressionModelClassNames:
        """Regression Model Names."""

        ElasticNet = 'ElasticNet'
        GradientBoostingRegressor = 'GradientBoostingRegressor'
        DecisionTreeRegressor = 'DecisionTreeRegressor'
        KNearestNeighborsRegressor = 'KNeighborsRegressor'
        LassoLars = 'LassoLars'
        SGDRegressor = 'SGDRegressor'
        RandomForestRegressor = 'RandomForestRegressor'
        ExtraTreesRegressor = 'ExtraTreesRegressor'
        LightGBMRegressor = 'LightGBMRegressor'
        TensorFlowLinearRegressor = 'TFLinearRegressorWrapper'
        TensorFlowDNNRegressor = 'TFDNNRegressorWrapper'
        XGBoostRegressor = 'XGBoostRegressor'


class LegacyModelNames:
    """Names for all legacy model names supported by AutoML."""

    class ClassificationLegacyModelNames:
        """Names for all classification legacy model names."""

        LogisticRegression = 'logistic regression'
        SGDClassifier = 'SGD classifier'
        MultinomialNB = 'MultinomialNB'
        BernoulliNB = 'BernoulliNB'
        SupportVectorMachine = 'SVM'
        LinearSupportVectorMachine = 'LinearSVM'
        KNearestNeighborsClassifier = 'kNN'
        DecisionTree = 'DT'
        RandomForest = 'RF'
        ExtraTrees = 'extra trees'
        LightGBMClassifier = 'lgbm_classifier'
        GradientBoosting = 'gradient boosting'
        TensorFlowDNNClassifier = 'TF DNNClassifier'
        TensorFlowLinearClassifier = 'TF LinearClassifier'
        XGBoostClassifier = 'xgboost classifier'

    class RegressionLegacyModelNames:
        """Names for all regression legacy model names."""

        ElasticNet = 'Elastic net'
        GradientBoostingRegressor = 'Gradient boosting regressor'
        DecisionTreeRegressor = 'DT regressor'
        KNearestNeighborsRegressor = 'kNN regressor'
        LassoLars = 'Lasso lars'
        SGDRegressor = 'SGD regressor'
        RandomForestRegressor = 'RF regressor'
        ExtraTreesRegressor = 'extra trees regressor'
        LightGBMRegressor = 'lightGBM regressor'
        TensorFlowLinearRegressor = 'TF LinearRegressor'
        TensorFlowDNNRegressor = 'TF DNNRegressor'
        XGBoostRegressor = 'xgboost regressor'


class ModelName:
    """Model names with customer, legacy and class names."""

    def __init__(self, customer_model_name, legacy_model_name, model_class_name):
        """Init ModelName."""
        self.customer_model_name = customer_model_name
        self.legacy_model_name = legacy_model_name
        self.model_class_name = model_class_name


class SupportedModelNames:
    """A list of supported models with all customer name, legacy model name and model class name."""

    SupportedClassificationModelList = [
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            LogisticRegression,
            LegacyModelNames.ClassificationLegacyModelNames.LogisticRegression,
            ModelClassNames.ClassificationModelClassNames.LogisticRegression),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            SGDClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.SGDClassifier,
            ModelClassNames.ClassificationModelClassNames.SGDClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            MultinomialNB,
            LegacyModelNames.ClassificationLegacyModelNames.MultinomialNB,
            ModelClassNames.ClassificationModelClassNames.MultinomialNB),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            BernoulliNB,
            LegacyModelNames.ClassificationLegacyModelNames.BernoulliNB,
            ModelClassNames.ClassificationModelClassNames.BernoulliNB),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            SupportVectorMachine,
            LegacyModelNames.ClassificationLegacyModelNames.
            SupportVectorMachine,
            ModelClassNames.ClassificationModelClassNames.SupportVectorMachine),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            LinearSupportVectorMachine,
            LegacyModelNames.ClassificationLegacyModelNames.
            LinearSupportVectorMachine,
            ModelClassNames.ClassificationModelClassNames.
            LinearSupportVectorMachine),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            KNearestNeighborsClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            KNearestNeighborsClassifier,
            ModelClassNames.ClassificationModelClassNames.
            KNearestNeighborsClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            DecisionTree,
            LegacyModelNames.ClassificationLegacyModelNames.DecisionTree,
            ModelClassNames.ClassificationModelClassNames.DecisionTree),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            RandomForest,
            LegacyModelNames.ClassificationLegacyModelNames.RandomForest,
            ModelClassNames.ClassificationModelClassNames.RandomForest),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            ExtraTrees,
            LegacyModelNames.ClassificationLegacyModelNames.ExtraTrees,
            ModelClassNames.ClassificationModelClassNames.ExtraTrees),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            LightGBMClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.LightGBMClassifier,
            ModelClassNames.ClassificationModelClassNames.LightGBMClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            GradientBoosting,
            LegacyModelNames.ClassificationLegacyModelNames.GradientBoosting,
            ModelClassNames.ClassificationModelClassNames.GradientBoosting),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            TensorFlowDNNClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            TensorFlowDNNClassifier,
            ModelClassNames.ClassificationModelClassNames.
            TensorFlowDNNClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            TensorFlowLinearClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            TensorFlowLinearClassifier,
            ModelClassNames.ClassificationModelClassNames.
            TensorFlowLinearClassifier)]

    SupportedRegressionModelList = [
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.ElasticNet,
            LegacyModelNames.RegressionLegacyModelNames.ElasticNet,
            ModelClassNames.RegressionModelClassNames.ElasticNet),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            GradientBoostingRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            GradientBoostingRegressor,
            ModelClassNames.RegressionModelClassNames.
            GradientBoostingRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            DecisionTreeRegressor,
            LegacyModelNames.RegressionLegacyModelNames.DecisionTreeRegressor,
            ModelClassNames.RegressionModelClassNames.DecisionTreeRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            KNearestNeighborsRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            KNearestNeighborsRegressor,
            ModelClassNames.RegressionModelClassNames.
            KNearestNeighborsRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.LassoLars,
            LegacyModelNames.RegressionLegacyModelNames.LassoLars,
            ModelClassNames.RegressionModelClassNames.LassoLars),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            SGDRegressor,
            LegacyModelNames.RegressionLegacyModelNames.SGDRegressor,
            ModelClassNames.RegressionModelClassNames.SGDRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            RandomForestRegressor,
            LegacyModelNames.RegressionLegacyModelNames.RandomForestRegressor,
            ModelClassNames.RegressionModelClassNames.RandomForestRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            ExtraTreesRegressor,
            LegacyModelNames.RegressionLegacyModelNames.ExtraTreesRegressor,
            ModelClassNames.RegressionModelClassNames.ExtraTreesRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            LightGBMRegressor,
            LegacyModelNames.RegressionLegacyModelNames.LightGBMRegressor,
            ModelClassNames.RegressionModelClassNames.LightGBMRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            TensorFlowLinearRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            TensorFlowLinearRegressor,
            ModelClassNames.RegressionModelClassNames.
            TensorFlowLinearRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            TensorFlowDNNRegressor,
            LegacyModelNames.RegressionLegacyModelNames.TensorFlowDNNRegressor,
            ModelClassNames.RegressionModelClassNames.TensorFlowDNNRegressor)]


class ModelNameMappings:
    """Model name mappings."""

    CustomerFacingModelToLegacyModelMapClassification = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.legacy_model_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    CustomerFacingModelToLegacyModelMapRegression = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.legacy_model_name for model in SupportedModelNames.
            SupportedRegressionModelList]))

    CustomerFacingModelToClassNameModelMapClassification = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.model_class_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    CustomerFacingModelToClassNameModelMapRegression = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.model_class_name for model in SupportedModelNames.
            SupportedRegressionModelList]))

    ClassNameToCustomerFacingModelMapClassification = dict(zip(
        [model.model_class_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    ClassNameToCustomerFacingModelMapRegression = dict(zip(
        [model.model_class_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList]))


class Defaults:
    """Default values for pipelines."""

    DEFAULT_PIPELINE_SCORE = float('NaN')  # Jasmine and 016N
    INVALID_PIPELINE_VALIDATION_SCORES = {}
    INVALID_PIPELINE_FITTED = ''
    INVALID_PIPELINE_OBJECT = None


class RunState:
    """Names for the states a run can be in."""

    START_RUN = 'running'
    FAIL_RUN = 'failed'
    CANCEL_RUN = 'canceled'
    COMPLETE_RUN = 'completed'


class API:
    """Names for the AzureML API operations that can be performed."""

    CreateExperiment = 'Create Experiment'
    CreateParentRun = 'Create Parent Run'
    GetNextPipeline = 'Get Pipeline'
    SetParentRunStatus = 'Set Parent Run Status'
    StartRemoteRun = 'Start Remote Run'
    StartRemoteSnapshotRun = 'Start Remote Snapshot Run'
    CancelChildRun = 'Cancel Child Run'
    StartChildRun = 'Start Child Run'
    SetRunProperties = 'Set Run Properties'
    LogMetrics = 'Log Metrics'
    InstantiateRun = 'Get Run'


class AcquisitionFunction:
    """Names for all acquisition functions used to select the next pipeline.

    The default is EI (expected improvement).
    """

    EI = "EI"
    PI = "PI"
    UCB = "UCB"
    THOMPSON = "thompson"

    FULL_SET = {EI, PI, UCB, THOMPSON}


class Status:
    """Names for the possible child run states."""

    NotStarted = 'Not Started'
    Started = 'Started'
    InProgress = 'In Progress'
    Completed = 'Completed'
    Terminated = 'Terminated'

    FULL_SET = {NotStarted, Started, InProgress, Completed, Terminated}

    @classmethod
    def pretty(cls, metric):
        """
        Verbose printing of AutoMLRun statuses.

        :param metric: The metric to print.
        :type metric: azureml.train.automl.constants.Status
        :return: Pretty print of the metric.
        :rtype: str
        """
        return {
            cls.Started: "Started",
            cls.InProgress: "In Progress running one of the child iterations.",
            cls.Completed: "Completed",
            cls.Terminated: "Terminated before finishing execution",
        }[metric]


class PipelineParameterConstraintCheckStatus:
    """Values for whether pipeline is a valid pipeline."""

    VALID = 0
    REMOVE = 1
    REJECTPIPELINE = 2


class OptimizerObjectives:
    """Names for the objectives an algorithm can have relative to a metric.

    Some metrics should be maximized and some should be minimized.
    """

    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    NA = 'NA'

    FULL_SET = {MAXIMIZE, MINIMIZE, NA}


class Optimizer:
    """Names for the categories of pipeline prediction algorithms used.

    - random provides a baseline by selecting a pipeline randomly
    - lvm uses latent variable models to predict probable next pipelines
    given performance on previous pipelines.
    """

    Random = "random"
    LVM = "lvm"

    FULL_SET = {Random, LVM}


class Tasks:
    """Names for the types of machine learning tasks supported by AutoML."""

    CLASSIFICATION = 'classification'
    REGRESSION = 'regression'

    ALL = [CLASSIFICATION, REGRESSION]


class ClientErrors:
    """Names for the client errors that can occur when violating user-specified cost contraints."""

    EXCEEDED_TIME_CPU = "EXCEEDED_TIME_CPU"
    EXCEEDED_TIME = "EXCEEDED_TIME"
    EXCEEDED_MEMORY = "EXCEEDED_MEMORY"
    SUBPROCESS_ERROR = "SUBPROCESS_ERROR"
    GENERIC_ERROR = "GENERIC_ERROR"

    ALL_ERRORS = {
        EXCEEDED_TIME_CPU, EXCEEDED_TIME, EXCEEDED_MEMORY,
        SUBPROCESS_ERROR, GENERIC_ERROR
    }


class ServerStatus:
    """Values that the server status can take."""

    OK = 'ok'
    INCREASE_TIME_THRESHOLD = 'threshold'


class TimeConstraintEnforcement:
    """Enumeration of time contraint enforcement modes."""

    TIME_CONSTRAINT_NONE = 0
    TIME_CONSTRAINT_PER_ITERATION = 1
    TIME_CONSTRAINT_TOTAL = 2


class PipelineCost:
    """Names for the different cost model modes.

    - COST_NONE returns all predicted pipelines
    - COST_FILTER returns only pipelines that were predicted by cost models
        to meet the user-specified cost conditions
    """

    COST_NONE = 0
    COST_FILTER = 1
    COST_SCALE_ACQUISITION = 2
    COST_SCALE_AND_FILTER = 3


class PipelineMaskProfiles:
    """Mask profiles for pipelines."""

    MASK_NONE = 'none'
    MASK_PARTIAL_FIT = 'partial_fit'
    MASK_LGBM_ONLY = 'lgbm'
    MASK_MANY_FEATURES = 'many_features'
    MASK_NO_SVM_KNN = 'no_svm_knn'
    MASK_SPARSE = 'sparse'
    MASK_PRUNE = 'prune'
    MASK_RANGE = 'range_mask'

    ALL_MASKS = [
        MASK_NONE,
        MASK_PARTIAL_FIT, MASK_LGBM_ONLY, MASK_MANY_FEATURES,
        MASK_NO_SVM_KNN, MASK_SPARSE,
        MASK_PRUNE, MASK_RANGE]


class EnsembleMethod:
    """Ensemble methods."""

    ENSEMBLE_AVERAGE = 'average'
    ENSEMBLE_STACK = 'stack'


class TrainingResultsType:
    """Potential results from runners class."""

    # Metrics
    TRAIN_METRICS = 'train'
    VALIDATION_METRICS = 'validation'
    TEST_METRICS = 'test'
    TRAIN_FROM_FULL_METRICS = 'train from full'
    TEST_FROM_FULL_METRICS = 'test from full'
    CV_METRICS = 'CV'
    CV_MEAN_METRICS = 'CV mean'

    # Other useful things
    TRAIN_TIME = 'train time'
    TRAIN_PERCENT = 'train_percent'
    MODELS = 'models'

    # Status:
    TRAIN_VALIDATE_STATUS = 'train validate status'
    TRAIN_FULL_STATUS = 'train full status'
    CV_STATUS = 'CV status'


class Metric:
    """Names for all metrics supported by classification and regression."""

    # Classification
    AUCMacro = 'AUC_macro'
    AUCMicro = 'AUC_micro'
    AUCWeighted = 'AUC_weighted'
    Accuracy = 'accuracy'
    WeightedAccuracy = 'weighted_accuracy'
    BalancedAccuracy = 'balanced_accuracy'
    NormMacroRecall = 'norm_macro_recall'
    LogLoss = 'log_loss'
    F1Micro = 'f1_score_micro'
    F1Macro = 'f1_score_macro'
    F1Weighted = 'f1_score_weighted'
    PrecisionMicro = 'precision_score_micro'
    PrecisionMacro = 'precision_score_macro'
    PrecisionWeighted = 'precision_score_weighted'
    RecallMicro = 'recall_score_micro'
    RecallMacro = 'recall_score_macro'
    RecallWeighted = 'recall_score_weighted'
    AvgPrecisionMicro = 'average_precision_score_micro'
    AvgPrecisionMacro = 'average_precision_score_macro'
    AvgPrecisionWeighted = 'average_precision_score_weighted'
    AccuracyTable = 'accuracy_table'
    ConfusionMatrix = 'confusion_matrix'

    # Regression
    ExplainedVariance = 'explained_variance'
    R2Score = 'r2_score'
    Spearman = 'spearman_correlation'
    MeanAbsError = 'mean_absolute_error'
    MedianAbsError = 'median_absolute_error'
    RMSE = 'root_mean_squared_error'
    RMSLE = 'root_mean_squared_log_error'
    NormMeanAbsError = 'normalized_mean_absolute_error'
    NormMedianAbsError = 'normalized_median_absolute_error'
    NormRMSE = 'normalized_root_mean_squared_error'
    NormRMSLE = 'normalized_root_mean_squared_log_error'
    Residuals = 'residuals'
    PredictedTrue = 'predicted_true'

    SCALAR_CLASSIFICATION_SET = {
        AUCMacro, AUCMicro, AUCWeighted, Accuracy,
        WeightedAccuracy, NormMacroRecall, BalancedAccuracy,
        LogLoss, F1Micro, F1Macro, F1Weighted, PrecisionMicro,
        PrecisionMacro, PrecisionWeighted, RecallMicro, RecallMacro,
        RecallWeighted, AvgPrecisionMicro, AvgPrecisionMacro,
        AvgPrecisionWeighted
    }

    NONSCALAR_CLASSIFICATION_SET = {
        AccuracyTable, ConfusionMatrix
    }

    CLASSIFICATION_SET = (SCALAR_CLASSIFICATION_SET |
                          NONSCALAR_CLASSIFICATION_SET)

    SCALAR_REGRESSION_SET = {
        ExplainedVariance, R2Score, Spearman, MeanAbsError,
        MedianAbsError, RMSE, RMSLE, NormMeanAbsError,
        NormMedianAbsError, NormRMSE, NormRMSLE
    }

    NONSCALAR_REGRESSION_SET = {
        Residuals, PredictedTrue
    }

    REGRESSION_SET = (SCALAR_REGRESSION_SET |
                      NONSCALAR_REGRESSION_SET)

    CLASSIFICATION_PRIMARY_SET = {
        Accuracy, AUCWeighted, NormMacroRecall, AvgPrecisionWeighted,
        PrecisionWeighted
    }

    REGRESSION_PRIMARY_SET = {
        Spearman, NormRMSE, R2Score, NormMeanAbsError
    }

    SAMPLE_WEIGHTS_UNSUPPORTED_SET = {
        WeightedAccuracy, Spearman, MedianAbsError, NormMedianAbsError
    }

    FULL_SET = CLASSIFICATION_SET | REGRESSION_SET
    NONSCALAR_FULL_SET = (NONSCALAR_CLASSIFICATION_SET |
                          NONSCALAR_REGRESSION_SET)
    SCALAR_FULL_SET = (SCALAR_CLASSIFICATION_SET |
                       SCALAR_REGRESSION_SET)

    # TODO: These types will be removed when the artifact-backed
    # metrics are defined with protobuf
    # Do not use these constants except in artifact-backed metrics
    SCHEMA_TYPE_ACCURACY_TABLE = 'accuracy_table'
    SCHEMA_TYPE_CONFUSION_MATRIX = 'confusion_matrix'
    SCHEMA_TYPE_RESIDUALS = 'residuals'
    SCHEMA_TYPE_PREDICTIONS = 'predictions'

    @classmethod
    def pretty(cls, metric):
        """Verbose names for metrics."""
        return {
            cls.AUCMacro: "Macro Area Under The Curve",
            cls.AUCMicro: "Micro Area Under The Curve",
            cls.AUCWeighted: "Weighted Area Under The Curve",
            cls.Accuracy: "Accuracy",
            cls.WeightedAccuracy: "Weighted Accuracy",
            cls.NormMacroRecall: "Normed Macro Recall",
            cls.BalancedAccuracy: "Balanced Accuracy",
            cls.LogLoss: "Log Loss",
            cls.F1Macro: "Macro F1 Score",
            cls.F1Micro: "Micro F1 Score",
            cls.F1Weighted: "Weighted F1 Score",
            cls.PrecisionMacro: "Macro Precision",
            cls.PrecisionMicro: "Micro Precision",
            cls.PrecisionWeighted: "Weighted Precision",
            cls.RecallMacro: "Macro Recall",
            cls.RecallMicro: "Micro Recall",
            cls.RecallWeighted: "Weighted Recall",
            cls.AvgPrecisionMacro: "Macro Average Precision",
            cls.AvgPrecisionMicro: "Micro Average Precision",
            cls.AvgPrecisionWeighted: "Weighted Average Precision",
            cls.ExplainedVariance: "Explained Variance",
            cls.R2Score: "R2 Score",
            cls.Spearman: "Spearman Correlation",
            cls.MeanAbsError: "Mean Absolute Error",
            cls.MedianAbsError: "Median Absolute Error",
            cls.RMSE: "Root Mean Squared Error",
            cls.RMSLE: "Root Mean Squared Log Error",
            cls.NormMeanAbsError: "Normalized Mean Absolute Error",
            cls.NormMedianAbsError: "Normalized Median Absolute Error",
            cls.NormRMSE: "Normalized Root Mean Squared Error",
            cls.NormRMSLE: "Normalized Root Mean Squared Log Error"
        }[metric]

    CLIPS_POS = {
        LogLoss: 10,
        NormMeanAbsError: 10,
        NormMedianAbsError: 10,
        NormRMSE: 10,
        NormRMSLE: 10,
        # current timeout value but there is a long time
        TrainingResultsType.TRAIN_TIME: 10 * 60 * 2
    }

    CLIPS_NEG = {
        # spearman is naturally limitted to this range but necessary for transform_y to work
        # otherwise spearmen is getting clipped to 0 by default
        Spearman: -1,
        ExplainedVariance: -10,
        R2Score: -10
    }


class MetricObjective:
    """Mappings from metrics to their objective.

    Objectives are maximization or minimization (regression and
    classification).
    """

    Classification = {
        Metric.AUCMicro: OptimizerObjectives.MAXIMIZE,
        Metric.AUCMacro: OptimizerObjectives.MAXIMIZE,
        Metric.AUCWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.Accuracy: OptimizerObjectives.MAXIMIZE,
        Metric.WeightedAccuracy: OptimizerObjectives.MAXIMIZE,
        Metric.NormMacroRecall: OptimizerObjectives.MAXIMIZE,
        Metric.BalancedAccuracy: OptimizerObjectives.MAXIMIZE,
        Metric.LogLoss: OptimizerObjectives.MINIMIZE,
        Metric.F1Micro: OptimizerObjectives.MAXIMIZE,
        Metric.F1Macro: OptimizerObjectives.MAXIMIZE,
        Metric.F1Weighted: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionMacro: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionMicro: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.RecallMacro: OptimizerObjectives.MAXIMIZE,
        Metric.RecallMicro: OptimizerObjectives.MAXIMIZE,
        Metric.RecallWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionMacro: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionMicro: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.AccuracyTable: OptimizerObjectives.NA,
        Metric.ConfusionMatrix: OptimizerObjectives.NA
    }

    Regression = {
        Metric.ExplainedVariance: OptimizerObjectives.MAXIMIZE,
        Metric.R2Score: OptimizerObjectives.MAXIMIZE,
        Metric.Spearman: OptimizerObjectives.MAXIMIZE,
        Metric.MeanAbsError: OptimizerObjectives.MINIMIZE,
        Metric.NormMeanAbsError: OptimizerObjectives.MINIMIZE,
        Metric.MedianAbsError: OptimizerObjectives.MINIMIZE,
        Metric.NormMedianAbsError: OptimizerObjectives.MINIMIZE,
        Metric.RMSE: OptimizerObjectives.MINIMIZE,
        Metric.NormRMSE: OptimizerObjectives.MINIMIZE,
        Metric.RMSLE: OptimizerObjectives.MINIMIZE,
        Metric.NormRMSLE: OptimizerObjectives.MINIMIZE,
        Metric.Residuals: OptimizerObjectives.NA,
        Metric.PredictedTrue: OptimizerObjectives.NA
    }


class TrainingType:
    """Names for validation methods.

    Different experiment types will use different validation methods.
    """

    # Yields TRAIN_FROM_FULL_METRICS and TEST_FROM_FULL_METRICS
    TrainFull = 'train_full'
    # Yields VALIDATION_METRICS
    TrainAndValidation = 'train_valid'
    # Yields TRAIN_METRICS, VALIDATION_METRICS, and TEST_METRICS
    TrainValidateTest = 'train_valid_test'
    # Yields CV_METRICS and CV_MEAN_METRICS
    CrossValidation = 'CV'
    MeanCrossValidation = 'MeanCrossValidation'
    FULL_SET = {
        TrainFull,
        TrainAndValidation,
        TrainValidateTest,
        CrossValidation,
        MeanCrossValidation}

    @classmethod
    def pretty(cls, metric):
        """Verbose names for training types."""
        return {
            cls.TrainFull: "Full",
            cls.TrainAndValidation: "Train and Validation",
            cls.CrossValidation: "Cross Validation",
            cls.MeanCrossValidation: "Mean of the Cross Validation",
        }[metric]


class NumericalDtype:
    """Names for supported numerical datatypes.

    Names correspond to the output of pandas.api.types.infer_dtype().
    """

    Integer = 'integer'
    Floating = 'floating'
    MixedIntegerFloat = 'mixed-integer-float'
    MixedInteger = 'mixed-integer'

    FULL_SET = {Integer, Floating, MixedIntegerFloat, MixedInteger}


class TextOrCategoricalDtype:
    """Names for supported categorical datatypes."""

    String = 'string'

    FULL_SET = {String}


class TimeSeries:
    """Parameters used for timeseries."""

    TIME_COLUMN_NAME = 'time_column_name'
    GRAIN_COLUMN_NAMES = 'grain_column_names'
    DROP_COLUMN_NAMES = 'drop_column_names'


class Transformers:
    """Names of transformers used for data processing."""

    X_TRANSFORMER = 'datatransformer'
    Y_TRANSFORMER = 'y_transformer'
    LAG_TRANSFORMER = 'laggingtransformer'
    TIMESERIES_TRANSFORMER = 'timeseriestransformer'
    ALL = [X_TRANSFORMER, Y_TRANSFORMER, LAG_TRANSFORMER, TIMESERIES_TRANSFORMER]


def get_metric_from_type(t):
    """Get valid metrics for a given training type."""
    return {
        TrainingType.TrainFull: TrainingResultsType.TEST_FROM_FULL_METRICS,
        TrainingType.TrainAndValidation: (
            TrainingResultsType.VALIDATION_METRICS),
        TrainingType.TrainValidateTest: (
            TrainingResultsType.VALIDATION_METRICS),
        TrainingType.CrossValidation: TrainingResultsType.CV_MEAN_METRICS
    }[t]


def get_status_from_type(t):
    """Get valid training statuses for a given training type."""
    return {
        TrainingType.TrainFull: TrainingResultsType.TRAIN_FULL_STATUS,
        TrainingType.TrainAndValidation: (
            TrainingResultsType.TRAIN_VALIDATE_STATUS),
        TrainingType.TrainValidateTest: (
            TrainingResultsType.TRAIN_VALIDATE_STATUS),
        TrainingType.CrossValidation: TrainingResultsType.CV_STATUS
    }[t]
