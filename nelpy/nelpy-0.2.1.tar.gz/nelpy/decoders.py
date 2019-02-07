from sklearn.base import BaseEstimator

class BayesianDecoder(BaseEstimator):
    """
    Gaussian Naive Bayes (GaussianNB)
    Can perform online updates to model parameters via `partial_fit` method.
    For details on algorithm used to update feature means and variance online,
    see Stanford CS tech report STAN-CS-79-773 by Chan, Golub, and LeVeque:
        http://i.stanford.edu/pub/cstr/reports/cs/tr/79/773/CS-TR-79-773.pdf
    Read more in the :ref:`User Guide <gaussian_naive_bayes>`.
    Parameters
    ----------
    priors : array-like, shape (n_classes,)
        Prior probabilities of the classes. If specified the priors are not
        adjusted according to the data.
    var_smoothing : float, optional (default=1e-9)
        Portion of the largest variance of all features that is added to
        variances for calculation stability.
    Attributes
    ----------
    class_prior_ : array, shape (n_classes,)
        probability of each class.
    class_count_ : array, shape (n_classes,)
        number of training samples observed in each class.
    theta_ : array, shape (n_classes, n_features)
        mean of each feature per class
    sigma_ : array, shape (n_classes, n_features)
        variance of each feature per class
    epsilon_ : float
        absolute additive value to variances
    Examples
    --------
    >>> import numpy as np
    >>> X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
    >>> Y = np.array([1, 1, 1, 2, 2, 2])
    >>> from sklearn.naive_bayes import GaussianNB
    >>> clf = GaussianNB()
    >>> clf.fit(X, Y)
    GaussianNB(priors=None, var_smoothing=1e-09)
    >>> print(clf.predict([[-0.8, -1]]))
    [1]
    >>> clf_pf = GaussianNB()
    >>> clf_pf.partial_fit(X, Y, np.unique(Y))
    GaussianNB(priors=None, var_smoothing=1e-09)
    >>> print(clf_pf.predict([[-0.8, -1]]))
    [1]
    """

    def __init__(self, priors=None, var_smoothing=1e-9):
        self.priors = priors
        self.var_smoothing = var_smoothing

    def fit(self, X, y, sample_weight=None):
        """Fit Gaussian Naive Bayes according to X, y
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features.
        y : array-like, shape (n_samples,)
            Target values.
        sample_weight : array-like, shape (n_samples,), optional (default=None)
            Weights applied to individual samples (1. for unweighted).
            .. versionadded:: 0.17
               Gaussian Naive Bayes supports fitting with *sample_weight*.
        Returns
        -------
        self : object
        """
        X, y = check_X_y(X, y)
        return self._partial_fit(X, y, np.unique(y), _refit=True,
                                 sample_weight=sample_weight)