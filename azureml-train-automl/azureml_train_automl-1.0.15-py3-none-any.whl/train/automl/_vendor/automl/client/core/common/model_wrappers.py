# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to wrap models that don't accept parameters such as 'fraction of the dataset'."""

import warnings
from abc import ABC, abstractmethod

import lightgbm as lgb
import numpy as np
import scipy
import sklearn
import sklearn.decomposition
import sklearn.naive_bayes
import sklearn.pipeline
from scipy.special import inv_boxcox
from scipy.stats import boxcox
from sklearn import preprocessing
from sklearn.base import (BaseEstimator, ClassifierMixin, RegressorMixin,
                          TransformerMixin)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, Normalizer
from automl.client.core.common.exceptions import ConfigException
try:
    import xgboost as xgb
    xgboost_present = True
except ImportError:
    xgboost_present = False


class _AbstractModelWrapper(ABC):
    """Abstract base class for the model wrappers."""

    def __init__(self):
        """Initialize AbstractModelWrapper class."""
        pass

    @abstractmethod
    def get_model(self):
        """
        Abstract method for getting the inner original model object.

        :return: An inner model object.
        """
        raise NotImplementedError


class LightGBMClassifier(ClassifierMixin, _AbstractModelWrapper):
    """
    LightGBM Classifier class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
        for more parameters.
    """

    DEFAULT_MIN_DATA_IN_LEAF = 20

    def __init__(self, random_state=None, n_jobs=1, **kwargs):
        """
        Initialize LightGBM Classifier class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
            for more parameters.
        """
        self.params = kwargs
        self.params['random_state'] = random_state
        self.params['n_jobs'] = n_jobs
        self.model = None
        self._min_data_str = "min_data_in_leaf"
        self._min_child_samples = "min_child_samples"

        if self._min_data_str not in kwargs and \
                self._min_child_samples not in kwargs:
            raise ValueError("min_data_in_leaf not passed")

    def get_model(self):
        """
        Return LightGBM Classifier model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for LightGBM Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: other parameters
            Check http://lightgbm.readthedocs.io/en/latest/Parameters.html
            for more parameters.
        :return: Self after fitting the model.
        """
        N = X.shape[0]
        args = dict(self.params)
        if (self._min_data_str in args):
            if (self.params[self._min_data_str] ==
                    LightGBMClassifier.DEFAULT_MIN_DATA_IN_LEAF):
                args[self._min_child_samples] = self.params[
                    self._min_data_str]
            else:
                args[self._min_child_samples] = int(
                    self.params[self._min_data_str] * N) + 1
            del args[self._min_data_str]
        else:
            args[self._min_child_samples] = int(
                self.params[self._min_child_samples] * N) + 1

        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        self.model = lgb.LGBMClassifier(**args)
        self.model.fit(X, y, **kwargs)
        self.classes_ = np.unique(y)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for LightGBM Classifier model.

        :param deep:
                If True, will return the parameters for this estimator
                and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for the LightGBM classifier model.
        """
        params = {}
        params['random_state'] = self.params['random_state']
        params['n_jobs'] = self.params['n_jobs']
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.params)

        return params

    def predict(self, X):
        """
        Prediction function for LightGBM Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from LightGBM Classifier model.
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for LightGBM Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from LightGBM Classifier model.
        """
        return self.model.predict_proba(X)


class XGBoostClassifier(ClassifierMixin, _AbstractModelWrapper):
    """
    XGBoost Classifier class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check https://xgboost.readthedocs.io/en/latest/parameter.html
        for more parameters.
    """

    def __init__(self, random_state=None, n_jobs=1, **kwargs):
        """
        Initialize XGBoost Classifier class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        """
        self.params = kwargs
        self.params['seed'] = random_state
        self.params['n_jobs'] = n_jobs
        self.model = None
        if not xgboost_present:
            raise ConfigException("xgboost not installed, please install xgboost for including xgboost based models")

    def get_model(self):
        """
        Return XGBoost Classifier model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        self.model = xgb.XGBClassifier(**args)
        self.model.fit(X, y, **kwargs)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for XGBoost Classifier model.

        :param deep: If True, will return the parameters for this estimator and contained subobjects that are
            estimators.
        :type deep: boolean
        :return: Parameters for the XGBoost classifier model.
        """
        params = {}
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.params)

        return params

    def predict(self, X):
        """
        Prediction function for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from XGBoost Classifier model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for XGBoost Classifier model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from XGBoost Classifier model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict_proba(X)


class SparseNormalizer(TransformerMixin, _AbstractModelWrapper):
    """
    Normalizes rows of an input matrix. Supports sparse matrices.

    :param norm:
        Type of normalization to perform - l1’, ‘l2’, or ‘max’,
        optional (‘l2’ by default).
    :type norm: str
    """

    def __init__(self, norm="l2"):
        """
        Initialize function for Sparse Normalizer transformer.

        :param norm:
            Type of normalization to perform - l1’, ‘l2’, or ‘max’,
            optional (‘l2’ by default).
        :type norm: str
        """
        self.norm = norm
        self.norm_str = "norm"
        self.model = Normalizer(norm, copy=True)

    def get_model(self):
        """
        Return Sparse Normalizer model.

        :return: Sparse Normalizer model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Sparse Normalizer model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self.
        """
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Sparse Normalizer model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :return: Parameters for Sparse Normalizer model.
        """
        params = {self.norm_str: self.norm}
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.params)

        return params

    def transform(self, X):
        """
        Transform function for Sparse Normalizer model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Transformed output of Sparse Normalizer.
        """
        return self.model.transform(X)


class SparseScaleZeroOne(
        BaseEstimator, TransformerMixin, _AbstractModelWrapper):
    """Transforms the input data by appending previous rows."""

    def __init__(self):
        """Initialize Sparse Scale Transformer."""
        self.scaler = None
        self.model = None

    def get_model(self):
        """
        Return Sparse Scale model.

        :return: Sparse Scale model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Sparse Scale model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: Returns self after fitting the model.
        """
        self.model = sklearn.preprocessing.MaxAbsScaler()
        self.model.fit(X)
        return self

    def transform(self, X):
        """
        Transform function for Sparse Scale model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Transformed output of MaxAbsScaler.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        X = self.model.transform(X)
        X.data = (X.data + 1) / 2
        return X

    def get_params(self, deep=True):
        """
        Return parameters for Sparse Scale model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for Sparse Scale model.
        """
        params = {}
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.params)

        return params


class PreprocWrapper(TransformerMixin, _AbstractModelWrapper):
    """Normalizes rows of an input matrix. Supports sparse matrices."""

    def __init__(self, cls, **kwargs):
        """
        Initialize PreprocWrapper class.

        :param cls:
        :param kwargs:
        """
        self.cls = cls
        self.args = kwargs
        self.model = None

    def get_model(self):
        """
        Return wrapper model.

        :return: wrapper model
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for PreprocWrapper.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Ignored.
        :type y: numpy.ndarray
        :return: Returns an instance of self.
        """
        args = dict(self.args)
        self.model = self.cls(**args)
        self.model.fit(X)
        return self

    def get_params(self, deep=True):
        """
        Return parameters for PreprocWrapper.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for PreprocWrapper.
        """
        params = {'cls': self.cls}
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.args)

        return params

    def transform(self, X):
        """
        Transform function for PreprocWrapper.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Transformed output of inner model.
        """
        return self.model.transform(X)

    def inverse_transform(self, X):
        """
        Inverse transform function for PreprocWrapper.

        :param X: New data.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Inverse transformed data.
        """
        return self.model.inverse_transform(X)


class StandardScalerWrapper(PreprocWrapper):
    """Standard Scaler Wrapper around StandardScaler transformation."""

    def __init__(self, **kwargs):
        """Initialize Standard Scaler Wrapper class."""
        super().__init__(sklearn.preprocessing.StandardScaler,
                         **kwargs)


class NBWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """Naive Bayes Wrapper for conditional probabilities using either Bernoulli or Multinomial models."""

    def __init__(self, model, **kwargs):
        """
        Initialize Naive Bayes Wrapper class with either Bernoulli or Multinomial models.

        :param model: The actual model name.
        :type model: str
        """
        assert model in ['Bernoulli', 'Multinomial']
        self.model_name = model
        self.args = kwargs
        self.model = None

    def get_model(self):
        """
        Return Naive Bayes model.

        :return: Naive Bayes model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Naive Bayes model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other arguments.
        """
        if self.model_name == 'Bernoulli':
            base_clf = sklearn.naive_bayes.BernoulliNB(**self.args)
        elif self.model_name == 'Multinomial':
            base_clf = sklearn.naive_bayes.MultinomialNB(**self.args)
        model = base_clf
        is_sparse = scipy.sparse.issparse(X)
        # sparse matrix with negative cells
        if is_sparse and np.any(X < 0).max():
            clf = sklearn.pipeline.Pipeline(
                [('MinMax scaler', SparseScaleZeroOne()),
                 (self.model_name + 'NB', base_clf)])
            model = clf
        # regular matrix with negative cells
        elif not is_sparse and np.any(X < 0):
            clf = sklearn.pipeline.Pipeline(
                [('MinMax scaler',
                  sklearn.preprocessing.MinMaxScaler(
                      feature_range=(0, X.max()))),
                 (self.model_name + 'NB', base_clf)])
            model = clf

        self.model = model
        self.model.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for Naive Bayes model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for Naive Bayes model.
        """
        params = {'model_name': self.model_name}
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.args)

        return params

    def predict(self, X):
        """
        Prediction function for Naive Bayes Wrapper Model.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values from actual Naive Bayes model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Naive Bayes Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction probability values from actual Naive Bayes model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict_proba(X)


class TruncatedSVDWrapper(
        BaseEstimator, TransformerMixin, _AbstractModelWrapper):
    """
    Wrapper around Truncated SVD so that we only have to pass a fraction of dimensions.

    Read more at http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html

    :param min_components: Min number of desired dimensionality of output data.
    :type min_components: int
    :param max_components: Max number of desired dimensionality of output data.
    :type max_components: int
    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or RandomState
    :param kwargs: Other args taken by sklearn TruncatedSVD.
    """

    def __init__(
            self,
            min_components=2,
            max_components=200,
            random_state=None,
            **kwargs):
        """
        Initialize Truncated SVD Wrapper Model.

        :param min_components:
            Min number of desired dimensionality of output data.
        :type min_components: int
        :param max_components:
            Max number of desired dimensionality of output data.
        :type max_components: int
        :param random_state:
            RandomState instance or None, optional, default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or RandomState
        :param kwargs: Other args taken by sklearn TruncatedSVD.
        :return:
        """
        self._min_components = min_components
        self._max_components = max_components
        self.args = kwargs
        self.args['random_state'] = random_state

        self.n_components_str = "n_components"
        self.model = None

    def get_model(self):
        """
        Return sklearn Truncated SVD Model.

        :return: Truncated SVD Model.
        """
        return self.model

    def fit(self, X, y=None):
        """
        Fit function for Truncated SVD Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Ignored.
        :return: Returns an instance of self.
        :rtype: TruncatedSVDWrapper
        """
        args = dict(self.args)
        args[self.n_components_str] = min(
            self._max_components,
            max(self._min_components,
                int(self.args[self.n_components_str] * X.shape[1])))
        self.model = TruncatedSVD(**args)
        self.model.fit(X)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for Truncated SVD Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for Truncated SVD Wrapper Model.
        """
        params = {}
        params['min_components'] = self._min_components
        params['max_components'] = self._max_components
        params['random_state'] = self.args['random_state']
        if self.model:
            params.update(self.model.get_params(deep=deep))
        else:
            params.update(self.args)

        return self.args

    def transform(self, X):
        """
        Transform function for Truncated SVD Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Transformed data of reduced version of X.
        :rtype: array
        """
        return self.model.transform(X)

    def inverse_transform(self, X):
        """
        Inverse Transform function for Truncated SVD Wrapper Model.

        :param X: New data.
        :type X: numpy.ndarray
        :return: Inverse transformed data. Always a dense array.
        :rtype: array
        """
        return self.model.inverse_transform(X)


class SVCWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around svm.SVC that always sets probability to True.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html.

    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or RandomState
    :param: kwargs: Other args taken by sklearn SVC.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize svm.SVC Wrapper Model.

        :param random_state:
            RandomState instance or None, optional, default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or RandomState
        :param: kwargs: Other args taken by sklearn SVC.
        """
        kwargs["probability"] = True
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = sklearn.svm.SVC(**self.args)

    def get_model(self):
        """
        Return sklearn.svm.SVC Model.

        :return: The svm.SVC Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for svm.SVC Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        """
        self.model.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for svm.SVC Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: parameters for svm.SVC Wrapper Model.
        """
        params = {'random_state': self.args['random_state']}
        params.update(self.model.get_params(deep=deep))

        return params

    def predict(self, X):
        """
        Prediction function for svm.SVC Wrapper Model. Perform classification on samples in X.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values from svm.SVC model.
        :rtype: array
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for svm.SVC Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction probabilities values from svm.SVC model.
        :rtype: array
        """
        return self.model.predict_proba(X)


class NuSVCWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around svm.NuSVC that always sets probability to True.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.svm.NuSVC.html.

    :param random_state: RandomState instance or None, optional, default = None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by np.random.
    :type random_state: int or RandomState
    :param: kwargs: Other args taken by sklearn NuSVC.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize svm.NuSVC Wrapper Model.

        :param random_state: RandomState instance or None, optional,
        default = None
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState instance
            used by np.random.
        :type random_state: int or RandomState
        :param: kwargs: Other args taken by sklearn NuSVC.
        """
        kwargs["probability"] = True
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = sklearn.svm.NuSVC(**self.args)

    def get_model(self):
        """
        Return sklearn svm.NuSVC Model.

        :return: The svm.NuSVC Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for svm.NuSVC Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        """
        self.model.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for svm.NuSVC Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for svm.NuSVC Wrapper Model.
        """
        params = {'random_state': self.args['random_state']}
        params.update(self.model.get_params(deep=deep))
        return params

    def predict(self, X):
        """
        Prediction function for svm.NuSVC Wrapper Model. Perform classification on samples in X.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values from svm.NuSVC model.
        :rtype: array
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for svm.NuSVC Wrapper model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction probabilities values from svm.NuSVC model.
        :rtype: array
        """
        return self.model.predict_proba(X)


class SGDClassifierWrapper(BaseEstimator, ClassifierMixin):
    """
    SGD Classifier Wrapper Class.

    Wrapper around SGD Classifier to support predict probabilities on loss
    functions other than log loss and modified huber loss. This breaks
    partial_fit on loss functions other than log and modified_huber since the
    calibrated model does not support partial_fit.

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html.
    """

    def __init__(self, random_state=None, n_jobs=1, **kwargs):
        """
        Initialize SGD Classifier Wrapper Model.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters.
        """
        self.loss = "loss"
        self.model = None
        self._calibrated = False

        self.args = kwargs
        self.args['random_state'] = random_state
        self.args['n_jobs'] = n_jobs
        loss_arg = kwargs.get(self.loss, None)
        if loss_arg in ["log", "modified_huber"]:
            self.model = sklearn.linear_model.SGDClassifier(**self.args)
        else:
            self.model = CalibratedModel(
                sklearn.linear_model.SGDClassifier(**self.args), random_state)
            self._calibrated = True

    def get_model(self):
        """
        Return SGD Classifier Wrapper Model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for SGD Classifier Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns an instance of inner SGDClassifier model.
        """
        model = self.model.fit(X, y, **kwargs)
        if hasattr(model, "classes_"):
            self.classes_ = model.classes_
        else:
            self.classes_ = np.unique(y)

        return model

    def get_params(self, deep=True):
        """
        Return parameters for SGD Classifier Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for SGD Classifier Wrapper Model.
        """
        params = {}
        params['random_state'] = self.args['random_state']
        params['n_jobs'] = self.args['n_jobs']
        params.update(self.model.get_params(deep=deep))
        return self.args

    def predict(self, X):
        """
        Prediction function for SGD Classifier Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from SGD Classifier Wrapper model.
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for SGD Classifier Wrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return:
            Prediction probability values from SGD Classifier Wrapper model.
        """
        return self.model.predict_proba(X)

    def partial_fit(self, X, y, **kwargs):
        """
        Return partial fit result.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns an instance of inner SGDClassifier model.
        """
        if self._calibrated:
            raise ValueError("Calibrated model used")

        return self.model.partial_fit(X, y, **kwargs)


class EnsembleWrapper(BaseEstimator, ClassifierMixin):
    """Wrapper around multiple pipelines that combine predictions."""

    def __init__(self, models=None, clf=None, weights=None, **kwargs):
        """
        Initialize EnsembleWrapper model.

        :param models: List of models to use in ensembling.
        :type models: list
        :param clf:
        """
        self.models = models
        self.clf = clf
        self.weights = weights

    def fit(self, X, y):
        """
        Fit function for EnsembleWrapper.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return:
        """
        for m in self.models:
            m.fit(X, y)
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Ensemble Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for Ensemble Wrapper Model.
        """
        params = {}
        params['models'] = self.models
        params['clf'] = self.clf

        return params

    @staticmethod
    def get_ensemble_predictions(preds, weights=None):
        """
        Combine an array of probilities from compute_valid_predictions.

        Probabilities are combined into a single array of shape [num_samples, num_classes].
        """
        preds = np.average(preds, axis=2, weights=weights)
        preds /= preds.sum(1)[:, None]

        assert np.all(preds >= 0) and np.all(preds <= 1)
        return preds

    @staticmethod
    def compute_valid_predictions(models, X):
        """Return an array of probabilities of shape [num_samples, num_classes, num_models]."""
        preds0 = None
        for m in models:
            if m is not None:
                preds0 = m.predict_proba(X)
                break
        if preds0 is None:
            raise ValueError('no models found')
        num_classes = preds0.shape[1]
        preds = np.zeros((X.shape[0], num_classes, len(models)))
        for i, m in enumerate(models):
            if m is None:
                continue
            preds[:, :, i] = m.predict_proba(X)
        return preds

    def predict(self, X):
        """
        Prediction function for EnsembleWrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from EnsembleWrapper model.
        """
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for EnsembleWrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return:
            Prediction probability values from EnsembleWrapper model.
        """
        valid_predictions = EnsembleWrapper.compute_valid_predictions(
            self.models, X)
        if self.clf is None:
            return EnsembleWrapper.get_ensemble_predictions(
                valid_predictions, self.weights)
        else:
            # TODO make sure the order is same as during training\
            # ignore the first column due to collinearity
            valid_predictions = valid_predictions[:, 1:, :]
            return self.clf.predict_proba(valid_predictions.reshape(
                valid_predictions.shape[0],
                valid_predictions.shape[1] * valid_predictions.shape[2]))


class LinearSVMWrapper(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Wrapper around linear svm to support predict_proba on sklearn's liblinear wrapper.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param kwargs: Other parameters.
    """

    def __init__(self, random_state=None, **kwargs):
        """
        Initialize Linear SVM Wrapper Model.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used by `np.random`.
        :type random_state: int or RandomState
        :param kwargs: Other parameters.
        """
        self.args = kwargs
        self.args['random_state'] = random_state
        self.model = CalibratedModel(sklearn.svm.LinearSVC(**self.args))

    def get_model(self):
        """
        Return Linear SVM Wrapper Model.

        :return: Linear SVM Wrapper Model.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Linear SVM Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        """
        self.model.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)

    def get_params(self, deep=True):
        """
        Return parameters for Linear SVM Wrapper Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: parameters for Linear SVM Wrapper Model
        """
        params = {'random_state': self.args['random_state']}
        params.update(self.model.get_params(deep=deep))
        return params

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Linear SVM Wrapper model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction probability values from Linear SVM Wrapper model.
        """
        return self.model.predict_proba(X)

    def predict(self, X):
        """
        Prediction function for Linear SVM Wrapper Model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from Linear SVM Wrapper model.
        """
        return self.model.predict(X)


class CalibratedModel(BaseEstimator, ClassifierMixin, _AbstractModelWrapper):
    """
    Trains a calibrated model.

    Takes a base estimator as input and trains a calibrated model.
    :param base_estimator: Base Model on which calibration has to be performed.
    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html.
    """

    def __init__(self, base_estimator, random_state=None):
        """
        Initialize Calibrated Model.

        :param base_estimator: Base Model on which calibration has to be
            performed.
        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        """
        self._train_ratio = 0.8
        self.random_state = random_state
        self.model = CalibratedClassifierCV(
            base_estimator=base_estimator, cv="prefit")

    def get_model(self):
        """
        Return the sklearn Calibrated Model.

        :return: The Calibrated Model.
        :rtype: sklearn.calibration.CalibratedClassifierCV
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for Calibrated Model.

        :param X: Input training data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :return: self: Returns an instance of self.
        :rtype: CalibratedModel
        """
        arrays = [X, y]
        if "sample_weight" in kwargs:
            arrays.append(kwargs["sample_weight"])
        self.args = kwargs
        out_arrays = train_test_split(
            *arrays,
            train_size=self._train_ratio,
            random_state=self.random_state,
            stratify=y)
        X_train, X_valid, y_train, y_valid = out_arrays[:4]

        if "sample_weight" in kwargs:
            sample_weight_train, sample_weight_valid = out_arrays[4:]
        else:
            sample_weight_train = None
            sample_weight_valid = None

        # train model
        self.model.base_estimator.fit(
            X_train, y_train, sample_weight=sample_weight_train)

        # fit calibration model
        try:
            self.model.fit(X_valid, y_valid, sample_weight=sample_weight_valid)
        except ValueError as e:
            y_labels = np.unique(y)
            y_train_labels = np.unique(y_train)
            y_valid_labels = np.unique(y_valid)
            y_train_missing_labels = np.setdiff1d(y_labels, y_train_labels, assume_unique=True)
            y_valid_missing_labels = np.setdiff1d(y_labels, y_valid_labels, assume_unique=True)
            if y_train_missing_labels.shape[0] > 0 or y_valid_missing_labels.shape[0] > 0:
                missing_labels = np.union1d(y_train_missing_labels, y_valid_missing_labels)
                raise ValueError('y did not contain enough samples for the following labels: {}'
                                 .format(missing_labels.tolist())) from e
            else:
                raise

        # retrain base estimator on full dataset
        self.model.base_estimator.fit(X, y, **kwargs)
        if hasattr(self.model, "classes_"):
            self.classes_ = self.model.classes_
        else:
            self.classes_ = np.unique(y)
        return self

    def get_params(self, deep=True):
        """
        Return parameters for Calibrated Model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Calibrated Model.
        """
        params = {'random_state': self.random_state}
        params.update(self.model.get_params(deep=deep))
        return params

    def predict(self, X):
        """
        Prediction function for Calibrated Model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction values from Calibrated model.
        :rtype: array
        """
        return self.model.predict(X)

    def predict_proba(self, X):
        """
        Prediction class probabilities for X for Calibrated model.

        :param X: Input samples.
        :type X: numpy.ndarray
        :return: Prediction proba values from Calibrated model.
        :rtype: array
        """
        return self.model.predict_proba(X)


class LightGBMRegressor(RegressorMixin, _AbstractModelWrapper):
    """
    LightGBM Regressor class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param kwargs: Other parameters.
    """

    DEFAULT_MIN_DATA_IN_LEAF = 20

    def __init__(self, random_state=None, n_jobs=1, **kwargs):
        """
        Initialize LightGBM Regressor class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator;
            If RandomState instance, random_state is the random number
            generator;
            If None, the random number generator is the RandomState
            instance used by `np.random`.
        :type random_state: int or RandomState
        :param kwargs: Other parameters.
        """
        self.params = kwargs
        self.params['random_state'] = random_state
        self.params['n_jobs'] = n_jobs
        self.model = None
        self._min_data_in_leaf = "min_data_in_leaf"
        self._min_child_samples = "min_child_samples"

        if self._min_data_in_leaf not in kwargs and \
                self._min_child_samples not in kwargs:
            raise ValueError("min_data_in_leaf not passed")

    def get_model(self):
        """
        Return LightGBM Regressor model.

        :return:
            Returns the fitted model if fit method has been called.
            Else returns None
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for LightGBM Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Labels for the data.
        :type y: numpy.ndarray
        :param kwargs: Other parameters.
        :return: Returns self after fitting the model.
        """
        verbose_str = "verbose"
        n = X.shape[0]
        params = dict(self.params)
        if (self._min_data_in_leaf in params):
            if (self.params[self._min_data_in_leaf] ==
                    LightGBMRegressor.DEFAULT_MIN_DATA_IN_LEAF):
                params[self._min_child_samples] = self.params[
                    self._min_data_in_leaf]
            else:
                params[self._min_child_samples] = int(
                    self.params[self._min_data_in_leaf] * n) + 1
            del params[self._min_data_in_leaf]
        else:
            params[self._min_child_samples] = int(
                self.params[self._min_child_samples] * n) + 1

        if verbose_str not in params:
            params[verbose_str] = -1

        self.model = lgb.LGBMRegressor(**params)
        self.model.fit(X, y, **kwargs)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for LightGBM Regressor model.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for LightGBM Regressor model.
        """
        params = {}
        params['random_state'] = self.params['random_state']
        params['n_jobs'] = self.params['n_jobs']
        if self.model:
            params.update(self.model.get_params(deep=deep))
        else:
            params.update(self.params)

        return params

    def predict(self, X):
        """
        Prediction function for LightGBM Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from LightGBM Regressor model.
        """
        return self.model.predict(X)


class XGBoostRegressor(RegressorMixin, _AbstractModelWrapper):
    """
    XGBoost Regressor class.

    :param random_state:
        RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.
    :type random_state: int or RandomState
    :param n_jobs: Number of parallel threads.
    :type n_jobs: int
    :param kwargs: Other parameters
        Check https://xgboost.readthedocs.io/en/latest/parameter.html
        for more parameters.
    """

    def __init__(self, random_state=None, n_jobs=1, **kwargs):
        """
        Initialize XGBoost Regressor class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        """
        self.params = kwargs
        self.params['seed'] = random_state
        self.params['n_jobs'] = n_jobs
        self.model = None
        if not xgboost_present:
            raise ConfigException("xgboost not installed, please install xgboost for including xgboost based models")

    def get_model(self):
        """
        Return XGBoost Regressor model.

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.model

    def fit(self, X, y, **kwargs):
        """
        Fit function for XGBoost Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param kwargs: other parameters
            Check https://xgboost.readthedocs.io/en/latest/parameter.html
            for more parameters.
        :return: Self after fitting the model.
        """
        args = dict(self.params)
        verbose_str = "verbose"
        if verbose_str not in args:
            args[verbose_str] = -10

        self.model = xgb.XGBRegressor(**args)
        self.model.fit(X, y, **kwargs)

        return self

    def get_params(self, deep=True):
        """
        Return parameters for XGBoost Regressor model.

        :param deep:
            If True, will return the parameters for this estimator and contained subobjects that are estimators.
        :type deep: boolean
        :return: Parameters for the XGBoost classifier model.
        """
        params = {}
        if self.model:
            params.update(self.model.get_params(deep))
        else:
            params.update(self.params)

        return params

    def predict(self, X):
        """
        Prediction function for XGBoost Regressor model.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Prediction values from XGBoost Regressor model.
        """
        if self.model is None:
            raise sklearn.exceptions.NotFittedError()
        return self.model.predict(X)


class PipelineWithYTransformations(sklearn.pipeline.Pipeline):
    """
    Pipeline transformer class.

    Pipeline and y_transformer are assumed to be already initialized.

    But fit could change this to allow for passing the parameters of the
    pipeline and y_transformer.

    :param pipeline: sklearn.pipeline.Pipeline object.
    :type pipeline: sklearn.pipeline.Pipeline
    :param y_trans_name: Name of y transformer.
    :type y_trans_name: string
    :param y_trans_obj: Object that computes a transformation on y values.
    :return: Object of class PipelineWithYTransformations.
    """

    def __init__(self, pipeline, y_trans_name, y_trans_obj):
        """
        Pipeline and y_transformer are assumed to be already initialized.

        But fit could change this to allow for passing the parameters of the
        pipeline and y_transformer.

        :param pipeline: sklearn.pipeline.Pipeline object.
        :type pipeline: sklearn.pipeline.Pipeline
        :param y_trans_name: Name of y transformer.
        :type y_trans_name: string
        :param y_trans_obj: Object that computes a transformation on y values.
        :return: Object of class PipelineWithYTransformations.
        """
        self.pipeline = pipeline
        self.y_transformer_name = y_trans_name
        self.y_transformer = y_trans_obj
        self.steps = pipeline.__dict__.get("steps")

    def __str__(self):
        """
        Return transformer details into string.

        return: string representation of pipeline transform.
        """
        return "%s\nY_transformer(['%s', %s])" % (self.pipeline.__str__(),
                                                  self.y_transformer_name,
                                                  self.y_transformer.__str__())

    def fit(self, X, y, y_min=None):
        """
        Fit function for pipeline transform.

        Perform the fit_transform of y_transformer, then fit into the sklearn.pipeline.Pipeline.

        :param X: Input training data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: numpy.ndarray
        :return: self: Returns an instance of PipelineWithYTransformations.
        """
        self.pipeline.fit(X, self.y_transformer.fit_transform(y, y_min=y_min))
        return self

    def fit_predict(self, X, y, y_min=None):
        """
        Fit predict function for pipeline transform.

        :param X: Input data.
        :type X: numpy.ndarray or scipy.spmatrix
        :param y: Input target values.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: numpy.ndarray
        :return: Prediction values after performing fit.
        """
        return self.fit(X, y, y_min).predict(X)

    def get_params(self, deep=True):
        """
        Return parameters for Pipeline Transformer.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Parameters for Pipeline Transformer.
        """
        return {
            "Pipeline": self.pipeline.get_params(deep),
            "y_transformer": self.y_transformer.get_params(deep),
            "y_transformer_name": self.y_transformer_name
        }

    def predict(self, X):
        """
        Prediction function for Pipeline Transformer.

        Perform the prediction of sklearn.pipeline.Pipeline, then do the inverse transform from y_transformer.

        :param X: Input samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values from Pipeline Transformer.
        :rtype: array
        """
        return self.y_transformer.inverse_transform(self.pipeline.predict(X))


class QuantileTransformerWrapper(BaseEstimator, TransformerMixin):
    """
    Quantile transformer wrapper class.

    Transform features using quantiles information.

    :param n_quantiles:
        Number of quantiles to be computed. It corresponds to the number
        of landmarks used to discretize the cumulative density function.
    :type n_quantiles: int
    :param output_distribution:
        Marginal distribution for the transformed data.
        The choices are 'uniform' (default) or 'normal'.
    :type output_distribution: string

    Read more at:
    http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.QuantileTransformer.html.
    """

    def __init__(self, n_quantiles=1000, output_distribution="uniform"):
        """
        Initialize function for Quantile transformer.

        :param n_quantiles:
            Number of quantiles to be computed. It corresponds to the number
            of landmarks used to discretize the cumulative density function.
        :type n_quantiles: int
        :param output_distribution:
            Marginal distribution for the transformed data.
            The choices are 'uniform' (default) or 'normal'.
        :type output_distribution: string
        """
        self.transformer = preprocessing.QuantileTransformer(
            n_quantiles=n_quantiles,
            output_distribution=output_distribution)

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Quantile transform.
        """
        return self.transformer.__str__()

    def fit(self, y):
        """
        Fit function for Quantile transform.

        :param y: The data used to scale along the features axis.
        :type y: numpy.ndarray or scipy.spmatrix
        :return: Object of QuantileTransformerWrapper.
        :rtype: QuantileTransformerWrapper
        """
        self.transformer.fit(y.reshape(-1, 1))
        return self

    def get_params(self, deep=True):
        """
        Return parameters of Quantile transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: bool
        :return: Dictionary of Quantile transform parameters.
        """
        return {
            "transformer": self.transformer.get_params(deep=deep)
        }

    def transform(self, y):
        """
        Transform function for Quantile transform.

        :param y: The data used to scale along the features axis.
        :type y: numpy.ndarray or scipy.spmatrix
        :return: The projected data of Quantile transform.
        :rtype: numpy.ndarray or scipy.spmatrix
        """
        return self.transformer.transform(y.reshape(-1, 1)).reshape(-1)

    def inverse_transform(self, y):
        """
        Inverse transform function for Quantile transform. Back-projection to the original space.

        :param y: The data used to scale along the features axis.
        :type y: numpy.ndarray or scipy.spmatrix
        :return: The projected data of Quantile inverse transform.
        :rtype: numpy.ndarray or scipy.spmatrix
        """
        return self.transformer.inverse_transform(y.reshape(-1, 1)).reshape(-1)


class LogTransformer(BaseEstimator, TransformerMixin):
    """
    Log transformer class.

    :param safe:
        If true, truncate values outside the transformer's
        domain to the nearest point in the domain.
    :type safe: boolean
    :return: Object of class LogTransformer.

    """

    def __init__(self, safe=True):
        """
        Initialize function for Log transformer.

        :param safe:
            If true, truncate values outside the transformer's
            domain to the nearest point in the domain.
        :type safe: boolean
        :return: Object of class LogTransformer.
        """
        self.base = np.e
        self.y_min = None
        self.scaler = None
        self.lower_range = 1e-5
        self.safe = safe

    def __str__(self):
        """
        Return transformer details into string.

        return: string representation of Log transform.
        """
        return "LogTransformer(base=e, y_min=%.5f, scaler=%s, safe=%s)" % \
            (self.y_min if self.y_min is not None else 0,
             self.scaler,
             self.safe)

    def fit(self, y, y_min=None):
        """
        Fit function for Log transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set
        :type y_min: double
        :return: Returns an instance of the LogTransformer model.
        """
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')

        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            self.scaler = preprocessing.StandardScaler(
                copy=False, with_mean=False,
                with_std=False).fit(y.reshape(-1, 1))
        else:
            y_max = np.max(y)
            self.scaler = preprocessing.MinMaxScaler(
                feature_range=(self.lower_range, 1)).fit(
                    np.array([y_max, self.y_min]).reshape(-1, 1))

        return self

    def get_params(self, deep=True):
        """
        Return parameters of Log transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Dictionary of Log transform parameters.
        """
        return {"base": self.base,
                "y_min": self.y_min,
                "scaler": self.scaler,
                "safe": self.safe
                }

    def return_y(self, y):
        """
        Return log value of y.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: The log transform array.
        """
        return np.log(y)

    def transform(self, y):
        """
        Transform function for Log transform to return the log value.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: The log transform array.
        """
        if self.y_min is None:
            raise Exception('Must fit before transforming')
        elif np.min(y) < self.y_min and \
                np.min(self.scaler.transform(
                    y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn("y_min greater than observed minimum in y, "
                              "clipping y to domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                return self.return_y(
                    self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ))
            else:
                raise Exception('y_min greater than observed minimum in y')
        else:
            return self.return_y(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ))

    def inverse_transform(self, y):
        """
        Inverse transform function for Log transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Log transform.
        """
        # this inverse transform has no restrictions, can exponetiate anything
        if self.y_min is None:
            raise Exception('Must fit before transforming')
        else:
            return self.scaler.inverse_transform(
                np.exp(y).reshape(-1, 1)).reshape(-1, )


class PowerTransformer(BaseEstimator, TransformerMixin):
    """
    Power transformer class.

    :param power: Power to raise y values to.
    :type power: double
    :param safe:
        If true, truncate values outside the transformer's domain to
        the nearest point in the domain.
    :type safe: boolean
    """

    def __init__(self, power=1, safe=True):
        """
        Initialize function for Power transformer.

        :param power: Power to raise y values to.
        :type power: double
        :param safe:
            If true, truncate values outside the transformer's domain
            to the nearest point in the domain.
        :type safe: boolean
        """
        # power = 1 is the identity transformation
        self.power = power
        self.y_min = None
        self.accept_negatives = False
        self.lower_range = 1e-5
        self.scaler = None
        self.safe = safe

        # check if the exponent is everywhere defined
        if self.power > 0 and \
                (((self.power % 2 == 1) or (1 / self.power % 2 == 1)) or
                 (self.power % 2 == 0 and self.power > 1)):
            self.accept_negatives = True
            self.y_min = -np.inf
            self.offset = 0
            self.scaler = preprocessing.StandardScaler(
                copy=False, with_mean=False, with_std=False).fit(
                    np.array([1], dtype=float).reshape(-1, 1))

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Power transform.
        """
        return \
            "PowerTransformer(power=%.1f, y_min=%.5f, scaler=%s, safe=%s)" % (
                self.power,
                self.y_min if self.y_min is not None else 0,
                self.scaler,
                self.safe)

    def return_y(self, y, power, invert=False):
        """
        Return some 'power' of 'y'.

        :param y: Input data.
        :type y: numpy.ndarray
        :param power: Power value.
        :type power: double
        :param invert:
            A boolean whether or not to perform the inverse transform.
        :type invert: boolean
        :return: The transformed targets.
        """
        # ignore invert, the power has already been inverted
        # can ignore invert because no offsetting has been done
        if self.accept_negatives:
            if np.any(y < 0):
                mult = np.sign(y)
                y_inter = np.multiply(np.power(np.absolute(y), power), mult)
            else:
                y_inter = np.power(y, power)
        else:
            # these are ensured to only have positives numbers as inputs
            y_inter = np.power(y, power)

        if invert:
            return self.scaler.inverse_transform(
                y_inter.reshape(-1, 1)).reshape(-1, )
        else:
            return y_inter

    def get_params(self, deep=True):
        """
        Return parameters of Power transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Dictionary of Power transform parameters.
        """
        return {
            "power": self.power,
            "scaler": self.scaler,
            "y_min": self.y_min,
            "accept_negatives": self.accept_negatives,
            "safe": self.safe
        }

    def fit(self, y, y_min=None):
        """
        Fit function for Power transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: double
        :return: Returns an instance of the PowerTransformer model.
        """
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')

        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            self.scaler = preprocessing.StandardScaler(
                copy=False, with_mean=False,
                with_std=False).fit(y.reshape(-1, 1))
        else:
            y_max = np.max(y)
            self.scaler = preprocessing.MinMaxScaler(
                feature_range=(self.lower_range, 1)).fit(
                    np.array([y_max, self.y_min]).reshape(-1, 1))
        return self

    def transform(self, y):
        """
        Transform function for Power transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Power transform result.
        """
        if self.y_min is None and not (self.power > 0 and self.power % 2 == 1):
            raise Exception('Must fit before transforming')
        elif np.min(y) < self.y_min and not self.accept_negatives and np.min(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn(
                    "y_min greater than observed minimum in y, clipping y to "
                    "domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                return self.return_y(
                    self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ),
                    self.power, invert=False)
            else:
                raise Exception('y_min greater than observed minimum in y')
        else:
            return self.return_y(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ),
                self.power, invert=False)

    def inverse_transform(self, y):
        """
        Inverse transform function for Power transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Power transform result.
        """
        if self.y_min is None and \
                not (self.power > 0 and self.power % 2 == 1):
            raise Exception('Must fit before transforming')
        elif not self.accept_negatives and np.min(y) <= 0:
            if self.safe:
                warnings.warn(
                    "y_min greater than observed minimum in y, clipping y to "
                    "domain")
                transformed_min = np.min(y[y > 0])
                y_copy = y.copy()
                y_copy[y < transformed_min] = transformed_min
                return self.return_y(y_copy, 1 / self.power, invert=True)
            else:
                raise Exception('y_min greater than observed minimum in y')
        else:
            return self.return_y(y, 1 / self.power, invert=True)


class BoxCoxTransformerScipy(BaseEstimator, TransformerMixin):
    """
    Box Cox transformer class for normalizing non-normal data.

    :param lambda_val:
        Lambda value for Box Cox transform, will be inferred if not set.
    :type lambda_val: double
    :param safe:
        If true, truncate values outside the transformer's domain to
        the nearest point in the domain.
    :type safe: boolean
    """

    def __init__(self, lambda_val=None, safe=True):
        """
        Initialize function for Box Cox transformer.

        :param lambda_val:
            Lambda value for Box Cox transform, will be inferred if not set.
        :type lambda_val: double
        :param safe:
            If true, truncate values outside the transformer's domain
            to the nearest point in the domain.
        :type safe: boolean
        """
        # can also use lambda_val = 0 as equivalent to natural log transformer
        self.lambda_val = lambda_val
        self.lower_range = 1e-5
        self.y_min = None
        self.scaler = None
        self.fitted = False
        self.safe = safe

    def __str__(self):
        """
        Return transformer details into string.

        return: String representation of Box Cox transform.
        """
        return ("BoxCoxTransformer(lambda=%.3f, y_min=%.5f, scaler=%s, "
                "safe=%s)" %
                (self.lambda_val if self.lambda_val is not None else 0,
                 self.y_min if self.y_min is not None else 0,
                 self.scaler,
                 self.safe))

    def fit(self, y, y_min=None):
        """
        Fit function for Box Cox transform.

        :param y: Input training data.
        :type y: numpy.ndarray
        :param y_min: Minimum value of y, will be inferred if not set.
        :type y_min: double
        :return: Returns an instance of the BoxCoxTransformerScipy model.
        """
        self.fitted = True
        if y_min is None:
            self.y_min = np.min(y)
        else:
            if (y_min is not None) and y_min <= np.min(y):
                self.y_min = y_min
            else:
                self.y_min = np.min(y)
                warnings.warn(
                    'Caution: y_min greater than observed minimum in y')
        if self.y_min > self.lower_range:
            self.y_min = self.lower_range
            self.scaler = preprocessing.StandardScaler(
                copy=False,
                with_mean=False,
                with_std=False).fit(y.reshape(-1, 1))
        else:
            y_max = np.max(y)
            self.scaler = preprocessing.MinMaxScaler(
                feature_range=(self.lower_range, 1)).fit(
                    np.array([y_max, self.y_min]).reshape(-1, 1))

        # reset if already fitted
        if self.lambda_val is None or self.fitted:
            y, self.lambda_val = boxcox(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ))
        return self

    def get_params(self, deep=True):
        """
        Return parameters of Box Cox transform as dictionary.

        :param deep:
            If True, will return the parameters for this estimator
            and contained subobjects that are estimators.
        :type deep: boolean
        :return: Dictionary of Box Cox transform parameters.
        """
        return {"lambda": self.lambda_val,
                "y_min": self.y_min,
                "scaler": self.scaler,
                "safe": self.safe
                }

    def transform(self, y):
        """
        Transform function for Box Cox transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Box Cox transform result.
        """
        if self.lambda_val is None:
            raise Exception('Must fit before transforming')
        elif np.min(y) < self.y_min and \
            np.min(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, )) <= 0:
            if self.safe:
                warnings.warn("y_min greater than observed minimum in y, "
                              "clipping y to domain")
                y_copy = y.copy()
                y_copy[y < self.y_min] = self.y_min
                return boxcox(
                    self.scaler.transform(y_copy.reshape(-1, 1)).reshape(-1, ),
                    self.lambda_val)
            else:
                raise Exception('y_min greater than observed minimum in y')
        else:
            return boxcox(
                self.scaler.transform(y.reshape(-1, 1)).reshape(-1, ),
                self.lambda_val)

    def inverse_transform(self, y):
        """
        Inverse transform function for Box Cox transform.

        :param y: Input data.
        :type y: numpy.ndarray
        :return: Inverse Box Cox transform result.
        """
        # inverse box_cox can take any number
        if self.lambda_val is None:
            raise Exception('Must fit before transforming')
        else:
            return self.scaler.inverse_transform(
                inv_boxcox(y, self.lambda_val).reshape(-1, 1)).reshape(-1, )


class PreFittedSoftVotingClassifier(VotingClassifier):
    """
    Pre-fitted Soft Voting Classifier class.

    :param estimators: Models to include in the PreFittedSoftVotingClassifier
    :type estimators: list of (string, estimator) tuples
    :param weights: Weights given to each of the estimators
    :type weights: numpy.ndarray
    :param flatten_transform:
        If True, transform method returns matrix with
        shape (n_samples, n_classifiers * n_classes).
        If False, it returns (n_classifiers, n_samples,
        n_classes).
    :type flatten_transform: boolean
    """

    def __init__(
            self, estimators, weights=None, flatten_transform=None,
            classification_labels=None):
        """
        Initialize function for Pre-fitted Soft Voting Classifier class.

        :param estimators:
            Models to include in the PreFittedSoftVotingClassifier
        :type estimators: list of (string, estimator) tuples
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers * n_classes).
            If False, it returns (n_classifiers, n_samples, n_classes).
        :type flatten_transform: boolean
        """
        super().__init__(estimators=estimators,
                         voting='soft',
                         weights=weights,
                         flatten_transform=flatten_transform)
        self.estimators_ = [est[1] for est in estimators]
        if classification_labels is None:
            self.le_ = LabelEncoder().fit([0])
        else:
            self.le_ = LabelEncoder().fit(classification_labels)


class PreFittedSoftVotingRegressor(PreFittedSoftVotingClassifier):
    """
    Pre-fitted Soft Voting Regressor class.

    :param estimators: Models to include in the PreFittedSoftVotingRegressor
    :type estimators: list of (string, estimator) tuples
    :param weights: Weights given to each of the estimators
    :type weights: numpy.ndarray
    :param flatten_transform:
        If True, transform method returns matrix with
        shape (n_samples, n_classifiers). If False, it
        returns (n_classifiers, n_samples, 1).
    :type flatten_transform: boolean
    """

    _estimator_type = "regressor"

    def __init__(self, estimators, weights=None, flatten_transform=None):
        """
        Initialize function for Pre-fitted Soft Voting Regressor class.

        :param estimators:
            Models to include in the PreFittedSoftVotingRegressor
        :type estimators: list of (string, estimator) tuples
        :param weights: Weights given to each of the estimators
        :type weights: numpy.ndarray
        :param flatten_transform:
            If True, transform method returns matrix with
            shape (n_samples, n_classifiers). If False, it
            returns (n_classifiers, n_samples, 1).
        :type flatten_transform: boolean
        """
        super().__init__(
            estimators, weights, flatten_transform, classification_labels=[0])

    def predict(self, X):
        """
        Predict function for Pre-fitted Soft Voting Regressor class.

        :param X: Input data.
        :type X: numpy.ndarray
        :return: Weighted average of predicted values.
        """
        predicted = self._predict(X)
        return np.average(predicted, axis=1, weights=self.weights)
