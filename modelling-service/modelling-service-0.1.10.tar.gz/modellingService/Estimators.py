import math

from pyspark.ml.classification import LogisticRegression, DecisionTreeClassifier, GBTClassifier, RandomForestClassifier, \
    NaiveBayes, LinearSVC
from pyspark.ml.clustering import KMeans, BisectingKMeans, GaussianMixture
from pyspark.ml.regression import LinearRegression, RandomForestRegressor, AFTSurvivalRegression, DecisionTreeRegressor, GeneralizedLinearRegression, IsotonicRegression, GBTRegressor

import Utils

"""
Each estimator wrapper does the following:
- take a free form dict of hyperparams as input
- filters out invalid params using reshaper
- passes clean params to Spark estimator
"""

def logisticRegressionClassifier(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['lrc'])
    else:
        params = hyperparams
    return LogisticRegression(**params)

def decisionTreeClassifier(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['dtc'])
    else:
        params = hyperparams
    return DecisionTreeClassifier(**params)

def linearSupportVectorClassifier(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['lsvc'])
    else:
        params = hyperparams
    return LinearSVC(**params)

def gradientBoostedTreeClassifier(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['gbtc'])
    else:
        params = hyperparams
    return GBTClassifier(**params)

def randomForestClassifier(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['rfc'])
    else:
        params = hyperparams
    return RandomForestClassifier(**params)

def naiveBayesClassifier(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['nbc'])
    else:
        params = hyperparams
    return NaiveBayes(**params)

def kMeansClustering(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['kmc'])
    else:
        params = hyperparams
    return KMeans(**params)

def bisectingKMeansClustering(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['bkmc'])
    else:
        params = hyperparams
    return BisectingKMeans(**params)

def gaussianMixtureClustering(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['gmc'])
    else:
        params = hyperparams
    return GaussianMixture(**params)

def linearRegression(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['lr'])
    else:
        params = hyperparams
    return LinearRegression(**params)

def generalizedLinearRegression(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['glr'])
    else:
        params = hyperparams
    return GeneralizedLinearRegression(**params)

def randomForestRegression(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['rfr'])
    else:
        params = hyperparams
    return RandomForestRegressor(**params)

def aftSurvivalRegression(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['aftsr'])
    else:
        params = hyperparams
    return AFTSurvivalRegression(**params)

def decisionTreeRegression(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['dtr'])
    else:
        params = hyperparams
    return DecisionTreeRegressor(**params)

def isotonicRegression(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['ir'])
    else:
        params = hyperparams
    return IsotonicRegression(**params)

def gradientBoostedTreeRegression(hyperparams = {}, reshape=True):
    if (reshape):
        params = Utils.reshapeParams(hyperparams, reshapers['gbtr'])
    else:
        params = hyperparams
    return GBTRegressor(**params)

estimators = dict(
    lrc=logisticRegressionClassifier,
    dtc=decisionTreeClassifier,
    lsvc=linearSupportVectorClassifier,
    gbtc=gradientBoostedTreeClassifier,
    rfc=randomForestClassifier,
    nbc=naiveBayesClassifier,
    kmc=kMeansClustering,
    bkmc=bisectingKMeansClustering,
    gmc=gaussianMixtureClustering,
    lr=linearRegression,
    glr=generalizedLinearRegression,
    rfr=randomForestRegression,
    # aftsr=aftSurvivalRegression,
    dtr=decisionTreeRegression,
    # ir=isotonicRegression,
    gbtr=gradientBoostedTreeRegression
)

"""
A reshaper is a map of cast functions to avoid precision errors in hyperparams
"""
reshapers = dict(
    lrc = {
        'regParam': float,
        'elasticNetParam': float,
        'threshold': float
    },
    dtc = {
        'maxDepth': int,
        'minInstancesPerNode': int,
        'maxBins': int,
        'minInfoGain': float
    },
    lsvc = {
        'regParam': float
    },
    gbtc = {
        'maxDepth': int,
        'minInstancesPerNode': int,
        'maxBins': int,
        'minInfoGain': float,
        'stepSize': float,
        'subsamplingRate': float
    },
    rfc = {
        'maxDepth': int,
        'minInstancesPerNode': int,
        'maxBins': int,
        'minInfoGain': float,
        'numTrees': int,
        'subsamplingRate': float
    },
    nbc = {
        'smoothing': float
    },
    kmc = {
        'k': int,
        'maxIter': int
    },
    bkmc = {
        'k': int,
        'maxIter': int,
        'minDivisibleClusterSize': float
    },
    gmc = {
        'k': int,
        'maxIter': int
    },
    lr = {
        'regParam': float,
        'elasticNetParam': float
    },
    glr = {
        'regParam': float
    },
    rfr = {
        'maxDepth': int,
        'minInstancesPerNode': int,
        'maxBins': int,
        'minInfoGain': float,
        'numTrees': int,
        'subsamplingRate': float
    },
    dtr = {
        'maxDepth': int,
        'minInstancesPerNode': int,
        'maxBins': int,
        'minInfoGain': float
    },
    gbtr = {
        'maxDepth': int,
        'minInstancesPerNode': int,
        'maxBins': int,
        'minInfoGain': float,
        'stepSize': float,
        'subsamplingRate': float
    }
)

"""
A scorer determines how to pick the best score for each algorithm
"""
scorers = dict(
    lrc = lambda score: max(score),
    dtc = lambda score: max(score),
    lsvc = lambda score: max(score),
    gbtc = lambda score: max(score),
    rfc = lambda score: max(score),
    nbc = lambda score: max(score),
    kmc = lambda score: max(score),
    bkmc = lambda score: max(score),
    gmc = lambda score: max(score),
    lr = lambda score: -min(score),
    glr = lambda score: max(score),
    rfr = lambda score: max(score),
    # aftsr = lambda score: max(score),
    dtr = lambda score: max(score),
    # ir = lambda score: max(score),
    gbtr = lambda score: max(score)
)