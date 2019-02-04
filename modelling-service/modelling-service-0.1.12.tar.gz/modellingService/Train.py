import numpy as np
import uuid
import itertools

from bayes_opt import BayesianOptimization
from modellingService.Utils import generateDirName, getEstimator, getEvaluator, getParamGrid, getValidator, getScorer, \
    reshapeParams, getParamInits, getDefaultParams, getParamBounds, generateReport
from pyspark.ml import Pipeline
import Estimators as e

def train(spark, inputDF, algorithm, metric, hyperparams={}, numFolds=3, seed=None, numInitPoints=5, numIterations=2, acquisitionFunction='poi', gpParams={'alpha': 1e-5}, baseDir='output', workDir='output', outputDir=uuid.uuid4(), idx=1, binary=True, smart=False, optimize=False, pipeline=True, persist=True, s3=False):
    """
    A single point of entry for both single algorithm and bayesian optimization
    :param spark: an existing spark session (unused for now)
    :param inputDF: dataframe containing features and labels
    :param algorithm: the algorithm code
    :param hyperparams: a dictionary of custom param overrides
    :param metric: scoring metric to be used
    :param numFolds: kFold value for cross validation
    :param seed: a seed value to set for deterministic debugging and testing
    :param numInitPoints: number of initial points to explore for bayesian optimization
    :param numIterations: number of iterations to exploit for bayesian optimization
    :param acquisitionFunction: acquisition function to use for bayesian optimization
    :param gpParams: params for tuning bayesian optimization
    :param baseDir: the directory where np will save report.csv 
    :param outputDir: the directory name for the model training job
    :param idx: the index of the model being trained in the current job
    :param binary: is the data multi-class of binary
    :param smart: if you want to explore the set of initial points set by the data scientists
    :param optimize: if you want to run bayesian optimization
    :param pipeline: if you want the pipeline model as an output as well.
    :param persist: if you want to persist model and report output
    :return: A JSON report of the trained model
    """
    _counter = itertools.count()
    _dirName = '{}/{}'.format(outputDir, generateDirName(algorithm, optimize, idx))
    estimator = getEstimator(algorithm)(hyperparams)
    evaluator = getEvaluator(algorithm, metric, binary)

    def getWrapperFunction():
        def optimizer(**params):
            cleanParams = reshapeParams(params, e.reshapers[algorithm])
            print cleanParams
            paramGrid = getParamGrid(estimator, cleanParams)
            validator = getValidator(estimator, evaluator, paramGrid, numFolds=numFolds, seed=seed)
            model = validator.fit(inputDF)
            if pipeline:
                pValidator = Pipeline(stages=[validator])
                pModel = pValidator.fit(inputDF)

            if (persist):
                count = _counter.next()
                model.bestModel.save('{}/{}/{}'.format(baseDir, _dirName, count + 1))
                if pipeline:
                    pModel.save('{}/{}/{}_p_model'.format(baseDir, _dirName, count + 1))

            if (optimize):
                score = model.avgMetrics
                scorer = getScorer(algorithm)
                return scorer(score)
            else:
                return model
        return optimizer

    # ensure the custom params are cleaned first
    customParams = reshapeParams(hyperparams, e.reshapers[algorithm])
    
    # fills in missing params with either smart or default params
    if (smart | optimize):
        smartParams = getParamInits(algorithm, customParams)
    else:
        smartParams = getDefaultParams(algorithm, customParams)

    f = getWrapperFunction()

    if (optimize):
        paramBounds = getParamBounds(algorithm, customParams)
        bo = BayesianOptimization(f, paramBounds, verbose=0)
        bo.explore(smartParams)
        bo.maximize(init_points=numInitPoints, n_iter=numIterations, acq=acquisitionFunction, **gpParams)

        report = generateReport('{}/{}'.format(baseDir, _dirName), workDir, algorithm, smartParams, bo.space.keys, bo.space.X, bo.space.Y, metric=metric, persist=persist, s3=s3)

        return report
    else:
        model = f(**smartParams)
        paramMap = model.getEstimatorParamMaps()[np.argmax(model.avgMetrics)]
        keys = list(map(lambda p: p.name, paramMap))
        X = [list(map(lambda p: paramMap[p], paramMap))]
        Y = [max(model.avgMetrics)]

        report = generateReport('{}/{}'.format(baseDir, _dirName), workDir, algorithm, smartParams, keys, X, Y, metric=metric, persist=persist, s3=s3)

        return report