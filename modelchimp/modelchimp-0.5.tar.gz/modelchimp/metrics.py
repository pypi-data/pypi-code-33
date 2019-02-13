"""
Evaluation Metrics accepted by ModelChimp
"""

# Classification
ACCURACY = 1
AVERAGE_PRECISION = 2
F1 = 3
F1_MICRO = 4
F1_MACRO = 5
F1_WEIGHTED = 6
F1_SAMPLES = 7
NEG_LOG_LOSS = 8
PRECISION = 9
RECALL = 10
ROC_AUC = 11
HAMMING_LOSS = 12
COHEN_KAPPA_SCORE = 13
HINGE_LOSS = 14
MATTHEWS_CORRCOEF = 15
JACCARD_SIMILARITY_SCORE = 16
LOG_LOSS = 17
# Clustering
ADJUSTED_MUTUAL_INFO_SCORE = 18
ADJUSTED_RAND_SCORE = 19
COMPLETENESS_SCORE = 20
FOWLKES_MALLOWS_SCORE = 21
HOMOGENEITY_SCORE = 22
MUTUAL_INFO_SCORE = 23
NORMALIZED_MUTUAL_INFO_SCORE = 24
V_MEASURE_SCORE = 25
# Regression
EXPLAINED_VARIANCE = 26
MEAN_ABSOLUTE_ERROR = 27
MEAN_SQUARED_ERROR = 28
MEAN_SQUARED_LOG_ERROR = 29
MEDIAN_ABSOLUTE_ERROR = 30
R2 = 31

def is_valid_metric(metric):
    return 1 <= metric <= 31

def get_metric_name(metric):
    METRIC_CHOICES = {
            ACCURACY: 'accuracy',
            AVERAGE_PRECISION: 'average precision',
            F1: 'f1',
            F1_MICRO: 'f1 micro',
            F1_MACRO: 'f1 macro',
            F1_WEIGHTED: 'f1 weighted',
            F1_SAMPLES: 'f1 samples',
            NEG_LOG_LOSS: 'neg log loss',
            PRECISION: 'precision',
            RECALL: 'recall',
            ROC_AUC: 'roc auc',
            HAMMING_LOSS: 'hamming loss',
            COHEN_KAPPA_SCORE: 'cohen kappa score',
            HINGE_LOSS: 'hinge loss',
            MATTHEWS_CORRCOEF: 'matthews corrcoef',
            JACCARD_SIMILARITY_SCORE: 'jaccard similarity score',
            LOG_LOSS: 'log loss',
            ADJUSTED_MUTUAL_INFO_SCORE: 'adjusted mutual info score',
            ADJUSTED_RAND_SCORE: 'adjusted rand score',
            COMPLETENESS_SCORE: 'completeness score',
            FOWLKES_MALLOWS_SCORE: 'fowlkes mallows score',
            HOMOGENEITY_SCORE: 'homogeneity score',
            MUTUAL_INFO_SCORE: 'mutual info score',
            NORMALIZED_MUTUAL_INFO_SCORE: 'normalized mutual info score',
            V_MEASURE_SCORE: 'v measure score',
            EXPLAINED_VARIANCE: 'explained variance',
            MEAN_ABSOLUTE_ERROR: 'mean absolute error',
            MEAN_SQUARED_ERROR: 'mean squared error',
            MEAN_SQUARED_LOG_ERROR: 'mean squared log error',
            MEDIAN_ABSOLUTE_ERROR: 'median absolute error',
            R2: 'r2'
        }

    return METRIC_CHOICES[metric]
