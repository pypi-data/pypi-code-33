import numpy as np
import itertools
import json
import uuid
import time
import datetime

from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator, ClusteringEvaluator, \
    RegressionEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

import Estimators as e
import Constants as c

from pyspark.sql.types import IntegerType, DoubleType, StringType, StructField
def getInputDF(spark, inputPath, inputFormat):
    """
    Returns DataFrame from input configurations
    :param spark:
    :param inputPath:
    :param inputFormat:
    :return: DataFrame
    """
    df = spark.read.format(inputFormat).load(inputPath)
    return df

def getCsvInputDF(spark, inputPath):
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(inputPath)
    numericColumns = map(lambda f: f.name, filter(lambda p: type(p.dataType) == IntegerType or type(p.dataType) == DoubleType, df.schema.fields))
    stringColumns = map(lambda f: f.name, filter(lambda p: type(p.dataType) == StringType, df.schema.fields))
    assembler = VectorAssembler(inputCols=numericColumns, outputCol="features")
    featureDF = assembler.transform(df)
    return featureDF.select("features")

def reshapeParams(hyperparams, reshaper):
    """
    A utility function that takes a dictionary of transformations for valid hyperparameters
    and filters out invalid params

    Testing the function:
    print reshapeParams({'regParam': 'invalid', 'elasticNetParam': 0.1, 'maxDepth': 0.1}, {'regParam': float, 'elasticNetParam': float, 'threshold': float})
    # Expect: {'elasticNetParam': 0.1}
    :param hyperparams: the dirty dictionary
    :param reshaper: the transformations
    :return: the clean dictionary
    """
    d = {}
    for k, v in hyperparams.items():
        if (reshaper.has_key(k)):
            f = reshaper[k]
            if (isinstance(v, str)):
                if (v.replace('.', '', 1).isdigit()):
                    d[k] = f(v)
                else:
                    continue
            elif (isinstance(v, float)):
                d[k] = f(v)
            elif (isinstance(v, int)):
                d[k] = f(v)
            else:
                continue
        else:
            continue
    return d

def getEstimator(algorithm):
    """
    Returns a wrapper to a valid Estimator and throws an exception if unimplemented
    :param algorithm: the algorithm code
    :return:
    """
    if (e.estimators.has_key(algorithm)):
        return e.estimators[algorithm]
    else:
        raise Exception('{} has not been implemented yet, try one of {}'.format(algorithm, e.estimators.keys()))

def getEvaluator(algorithm, metric, binary=True):
    category = c.category[algorithm]
    if (category == "classification"):
        return getClassificationEvaluator(metric, binary)
    elif (category == "clustering"):
        return getClusteringEvaluator(metric)
    elif (category == "regression"):
        return getRegressionEvaluator(metric)
    else:
        raise Exception('{} does not support evaluation yet'.format(algorithm))

def getClassificationEvaluator(metric='areaUnderROC', binary=True):
    """
    Returns an evaluator for classification algorithms based on Binary or Multiclass data
    :param metric: For binary - areaUnderROC|areaUnderPR, For multiclass - f1|weightedPrecision|weightedRecall|accuracy
    :param binary: Boolean
    :return: Evaluator object
    """
    if (binary):
        return BinaryClassificationEvaluator(metricName=metric)
    else:
        return MulticlassClassificationEvaluator(metricName=metric)

def getClusteringEvaluator(metric='silhouette'):
    """
    Returns an evaluator for clustering algorithms
    :param metric: spark only supports {silhouette} as of v2.3
    :return: Evaluator object
    """
    return ClusteringEvaluator(metricName=metric)

def getRegressionEvaluator(metric='rmse'):
    """
    Returns an evaluator for regression algorithms
    :param metric: One of {rmse|mse|r2|mae}
    :return: Evaluator object
    """
    return RegressionEvaluator(metricName=metric)

def getParamBounds(algorithm, customParams):
    """
    Overrides custom params over init points
    :param algorithm:
    :param customParams: Expects params that have been reshaped
    :return: Bounds of hyperparams
    """
    if (c.bounds.has_key(algorithm)):
        points = c.bounds[algorithm].copy()
        for k, v in points.items():
            if (customParams.has_key(k)):
                points.pop(k)
        return points
    else:
        raise Exception('{} does not have paramBound defined yet'.format(algorithm))

def getParamInits(algorithm, customParams):
    """
    Overrides custom params over init points
    :param algorithm:
    :param customParams: Expects params that have been reshaped
    :return: Set of hyperparams
    """
    if (c.inits.has_key(algorithm)):
        points = c.inits[algorithm].copy()
        for k, v in points.items():
            if (customParams.has_key(k)):
                points[k] = [customParams[k]]
        return points
    else:
        return getDefaultParams(algorithm, customParams)

def getDefaultParams(algorithm, customParams):
    """
    Fetches default params
    :param algorithm: 
    :param customParams: 
    :return: 
    """
    if (c.defaults.has_key(algorithm)):
        defaults = c.defaults[algorithm].copy()
        for k, v in defaults.items():
            if (customParams.has_key(k)):
                defaults[k] = [customParams[k]]
        return defaults
    else:
        raise Exception('{} does not have defaults defined yet'.format(algorithm))

def getScorer(algorithm):
    """
    Fetches the scorer function for the algorithm
    :param algorithm: 
    :return: 
    """
    if (e.scorers.has_key(algorithm)):
        return e.scorers[algorithm]
    else:
        raise Exception('{} does not have scorer defined yet'.format(algorithm))

def getParamGrid(estimator, params):
    """
    Generates a grid of hyperparams based on param bounds
    :param estimator: estimator for extracting the hyperparams
    :param params: the bounds for each hyperparam
    :return: ParamGrid object
    """
    paramGrid = ParamGridBuilder()
    for p in params:
        if (type(params[p]) == list):
            paramGrid = paramGrid.addGrid(getattr(estimator, p), params[p])
        else:
            paramGrid = paramGrid.addGrid(getattr(estimator, p), [params[p]])
    return paramGrid.build()

def getValidator(estimator, evaluator, paramGrid, numFolds=3, seed=42):
    """
    Creates a CrossValidator object
    :param estimator:
    :param evaluator:
    :param paramGrid:
    :param numFolds:
    :param seed:
    :return: Returns a CrossValidator object
    """
    validator = CrossValidator(estimator=estimator, evaluator=evaluator, estimatorParamMaps=paramGrid, numFolds=numFolds, seed=seed)
    return validator

def getSignificantDigits(values):
    """
    Utility to fix precision of float values
    :param values: 
    :return: 
    """
    return list(map(lambda v: float('{0:.4f}'.format(float(v))), values))

def generateModelReport(point, keys, modelDir):
    """
    Generates a dict for each model
    :param point: an ndarray containing hyperparam values and other metadata
    :param keys: headers to map the values to
    :param modelDir: output metadata
    :return: 
    """
    points = map(lambda v: v.item(), np.nditer(point))
    hyperparams = {}
    metrics = {}
    output = {'model_id': points[0], 'model_dir': modelDir, 'model_target': points[1]}
    for (k, v) in zip(keys, points)[-1:]:
        metrics[k] = v
    for (k, v) in zip(keys, points)[2:-1]:
        hyperparams[k] = v
    report = {'_id': points[0], 'output': output, 'hyperparams': hyperparams, 'metrics': metrics}
    return report

def generateReport(outputDir, workDir, algorithm, customParams, headers, params, values, metric='areaUnderROC', persist=True, s3=False):
    """
    Generates a JSON for each model run
    :param outputDir: directory to save the report
    :param algorithm: string code of the algorithm
    :param customParams: customParams taken here to fill in when optimized only on certain params
    :param headers: the params used for training model
    :param params: a matrix of param values across runs
    :param values: a vector of metric values across runs
    :param metric: the scoring metric used
    :param persist: if a csv needs to be written out
    :return: 
    """
    indexes = range(1, len(params) + 1)
    models = list(map(lambda idx: str('{}/{}'.format(outputDir, idx)), indexes))

    smartParams = {}
    for k, v in customParams.items():
        if k not in headers:
            smartParams[k] = v[0]

    points = np.hstack((np.expand_dims(indexes, axis=1), np.expand_dims(models, axis=1), list(map(lambda d: getSignificantDigits(d) + smartParams.values(), params)), np.expand_dims(getSignificantDigits(values), axis=1)))
    header = ','.join(['idx', 'model'] + headers + smartParams.keys() + [metric])

    modelDir = outputDir.split('/')[-1]
    jobName = outputDir.split('/')[-2]

    if (persist):
        if (s3):
            np.savetxt('{}/{}-{}-report.csv'.format(workDir, jobName, modelDir), points, header=header, delimiter=',', fmt='%s', comments='')
        else:
            np.savetxt('{}/report.csv'.format(outputDir), points, header=header, delimiter=',', fmt='%s', comments='')

    models = list(map(lambda p: generateModelReport(p, header.split(','), modelDir), points))
    report = json.dumps({'algorithm': algorithm, 'models': models}, sort_keys=True)

    return report

def generateDirName(algorithm, optimize=False, idx=1):
    """
    Utility function to generate a directory name as <algorithm>-<?optimize>-<idx>-<timestamp>
    :param algorithm: 
    :param optimize: 
    :param idx: 
    :return: 
    """
    tags = [algorithm]
    if (optimize):
        tags.append('optimized')
    now = time.time()
    tags.append(str(idx))
    return '-'.join(tags)


