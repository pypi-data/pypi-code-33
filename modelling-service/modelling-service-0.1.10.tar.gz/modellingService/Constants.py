"""
Constants and smart defaults for use with modelling-service
"""

"""
(min, max) range of hyperparams for building param grid in bayesian optimization
"""
bounds = dict(
    # Logistic Regression Classifier
    lrc = {
        'regParam': (0.1, 1),
        'elasticNetParam': (0.1, 1),
        'threshold': (0.4, 0.6)
    },

    # Decision Tree Classifier
    dtc = {
        'maxDepth': (1,10),
        'minInstancesPerNode': (1,10),
        'minInfoGain':(0.0,0.5),
        'maxBins':(32,64)
    },

    # Linear Support Vector Classifier
    lsvc = {
        'regParam': (0.1,1.0)
    },

    # Gradient Boosted Tree Classifier
    gbtc = {
        'maxDepth': (1,10),
        'minInstancesPerNode': (1,10),
        'minInfoGain': (0.0,0.5),
        'maxBins': (32,64),
        'stepSize': (0.1,1.0),
        'subsamplingRate': (0.5,1.0)
    },

    # Random Forest Classifier
    rfc = {
        'maxDepth': (1,10),
        'minInstancesPerNode': (1,10),
        'minInfoGain': (0.0,0.5),
        'maxBins': (32,64),
        'numTrees': (10,50),
        'subsamplingRate':(0.5,1.0)
    },

    # Naive Bayes Classifier
    nbc = {
        'smoothing': (0.1,1)
    },

    # K Means Clustering
    kmc = {
        'k': (2, 20),
        'maxIter': (5, 100)
    },

    # Bisecting KMeans Clustering
    bkmc = {
        'k': (4, 40),
        'maxIter': (5, 100),
        'minDivisibleClusterSize': (0.1, 1.0)
    },

    # Gaussian Mixture Clustering
    gmc = {
        'k': (2, 20),
        'maxIter': (5, 100)
    },

    # Linear Regression
    lr = {
        'regParam': (0.1, 1),
        'elasticNetParam': (0.1, 1)
    },

    # Generalized Linear Regression
    glr = {
        'regParam': (0.1, 1)
    },

    # Random Forest Regression
    rfr = {
        'maxDepth': (1,10),
        'minInstancesPerNode': (1,10),
        'minInfoGain': (0.0,0.5),
        'maxBins': (32,64),
        'numTrees': (10,50),
        'subsamplingRate':(0.5,1.0)
    },

    # AFT Survival Regression
    aftsr = {

    },

    # Decision Tree Regression
    dtr = {
        'maxDepth': (1,10),
        'minInstancesPerNode': (1,10),
        'minInfoGain':(0.0,0.5),
        'maxBins':(32,64)
    },

    # Isotonic Regression
    ir = {

    },

    # Gradient Boosted Tree Regression
    gbtr = {
        'maxDepth': (1,10),
        'minInstancesPerNode': (1,10),
        'minInfoGain': (0.0,0.5),
        'maxBins': (32,64),
        'stepSize': (0.1,1.0),
        'subsamplingRate': (0.5,1.0)
    }
)

"""
Smart default hyperparams. Generates param grid by cross product
"""
inits = dict(
    # Logistic Regression Classifier
    lrc = {
        'regParam': [0.1, 0.3],
        'elasticNetParam': [0.1, 0.3],
        'threshold': [0.4, 0.5]
    },

    #Decision Tree Classifier
    dtc = {
        'maxDepth': [1,3],
        'minInstancesPerNode': [1,3],
        'minInfoGain': [0.0,0.1],
        'maxBins': [32,40]
    },

    # Linear Support Vector Classifier
    lsvc = {
        'regParam': [0.1,0.3]
    },

    # Gradient Boosted Tree Classifier
    gbtc = {
        'maxDepth': [1,3],
        'minInstancesPerNode': [1,3],
        'minInfoGain': [0.0,0.1],
        'maxBins': [32,40],
        'stepSize': [0.1,0.5],
        'subsamplingRate': [0.5,1.0]
    },

    # Random Forest Classifier
    rfc = {
        'maxDepth': [1,3],
        'minInstancesPerNode': [1,3],
        'minInfoGain': [0.0,0.1],
        'maxBins': [32,40],
        'numTrees': [20,40],
        'subsamplingRate': [0.5,1.0]
    },

    # Naive Bayes Classifier
    nbc = {
        'smoothing': [0.5,1.0]
    }
)

"""
Dictionary containing the default hyperparams set by Spark
"""
defaults = dict(
    # Logistic Regression Classifier
    lrc = {
        'regParam': [0.0],
        'elasticNetParam': [0.0],
        'threshold': [0.5]
    },

    #Decision Tree Classifier
    dtc = {
        'maxDepth': [5],
        'minInstancesPerNode': [1],
        'minInfoGain': [0.0],
        'maxBins': [32]
    },

    # Linear Support Vector Classifier
    lsvc = {
        'regParam': [0.0]
    },

    # Gradient Boosted Tree Classifier
    gbtc = {
        'maxDepth': [5],
        'minInstancesPerNode': [1],
        'minInfoGain': [0.0],
        'maxBins': [32],
        'stepSize': [0.1],
        'subsamplingRate': [1.0]
    },

    # Random Forest Classifier
    rfc = {
        'maxDepth': [5],
        'minInstancesPerNode': [1],
        'minInfoGain': [0.0],
        'maxBins': [32],
        'numTrees': [20],
        'subsamplingRate': [1.0]
    },

    # Naive Bayes Classifier
    nbc = {
        'smoothing': [1.0]
    },

    # K Means Clustering
    kmc = {
        'k': [2],
        'maxIter': [20]
    },

    # Bisecting KMeans Clustering
    bkmc = {
        'k': [4],
        'maxIter': [20],
        'minDivisibleClusterSize': [1.0]
    },

    # Gaussian Mixture Clustering
    gmc = {
        'k': [2],
        'maxIter': [100]
    },

    # Linear Regression
    lr = {
        'regParam': [0.0],
        'elasticNetParam': [0.0]
    },

    # Generalized Linear Regression
    glr = {
        'regParam': [0.0]
    },

    # Random Forest Regression
    rfr = {
        'maxDepth': [5],
        'minInstancesPerNode': [1],
        'minInfoGain': [0.0],
        'maxBins': [32],
        'numTrees': [20],
        'subsamplingRate': [1.0]
    },

    # AFT Survival Regression
    aftsr = {

    },

    # Decision Tree Regression
    dtr = {
        'maxDepth': [5],
        'maxBins': [32],
        'minInstancesPerNode': [1],
        'minInfoGain': [0.0]
    },

    # Isotonic Regression
    ir = {

    },

    # Gradient Boosted Tree Regression
    gbtr = {
        'maxDepth': [5],
        'maxBins': [32],
        'minInstancesPerNode': [1],
        'minInfoGain': [0.0],
        'subsamplingRate': [1.0]
    }

)

'''
Dictionary to identify category of algorithm
'''
category = dict(
    lrc = "classification",
    dtc = "classification",
    lsvc = "classification",
    gbtc = "classification",
    rfc = "classification",
    nbc = "classification",
    kmc = "clustering",
    bkmc = "clustering",
    gmc = "clustering",
    lr = "regression",
    glr = "regression",
    rfr = "regression",
    # aftsr = "regression",
    dtr = "regression",
    # ir = "regression",
    gbtr = "regression"
)