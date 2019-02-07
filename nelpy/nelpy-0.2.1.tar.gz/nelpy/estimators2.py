import numpy as np
import logging
import copy

from sklearn.base import BaseEstimator
from sklearn.utils.validation import check_is_fitted

from .preprocessing import DataWindow
from . import core

class BayesianDecoderTemp(BaseEstimator):
    """
    Bayesian decoder wrapper class.

    mode = ['hist', 'glm-poisson', 'glm-binomial', 'glm', 'gvm', 'bars', 'gp']

    (gvm = generalized von mises; see http://kordinglab.com/spykes/getting-started.html)

    QQQ. Do we always bin first? does GLM and BARS use spike times, or binned
         spike counts? I think GLM uses binned spike counts with Poisson
         regression; not sure about BARS.

    QQQ. What other methods should be supported? BAKS? What is state of the art?

    QQQ. What if we want to know the fring rate over time? What does the input y
         look like then? How about trial averaged? How about a tuning curve?

    AAA. At the end of the day, this class should estimate a ratemap, and we
         need some way to set the domain of that ratemap, if desired, but it
         should not have to assume anything else. Values in y might be repeated,
         but if not, then we estimate the (single-trial) firing rate over time
         or whatever the associated y represents.

    See https://arxiv.org/pdf/1602.07389.pdf for more GLM intuition? and http://www.stat.columbia.edu/~liam/teaching/neurostat-fall18/glm-notes.pdf

    [2] https://www.biorxiv.org/content/biorxiv/early/2017/02/24/111450.full.pdf?%3Fcollection=
    http://kordinglab.com/spykes/getting-started.html
    https://xcorr.net/2011/10/03/using-the-binomial-glm-instead-of-the-poisson-for-spike-data/

    [1] http://www.stat.cmu.edu/~kass/papers/bars.pdf
    https://gist.github.com/AustinRochford/d640a240af12f6869a7b9b592485ca15
    https://discourse.pymc.io/t/bayesian-adaptive-regression-splines-and-mcmc-some-questions/756/5

    """

    def __init__(self, mode='hist', w=None):
        self._mode = self._check_mode(mode)
        self._w = self._check_window(w)
        pass

    @property
    def mode(self):
        return self._mode

    @property
    def w(self):
        return self._w

    @staticmethod
    def _check_mode(mode):
        mode = str(mode).strip().lower()
        valid_modes = ['hist']
        if mode in valid_modes:
            return mode
        raise NotImplementedError("mode '{}' is not supported yet!".format(str(mode)))

    @staticmethod
    def _check_window(w):
        if w is None:
            w = DataWindow(sum=True, bin_width=1)
        elif not isinstance(w, DataWindow):
            raise TypeError('w must be a nelpy DataWindow() type!')
        else:
            w = copy.copy(w)
        if w._sum is False:
            logging.warning('BayesianDecoder requires DataWindow (w) to have sum=True; changing to True')
            w._sum = True
        if w.bin_width is None:
            w.bin_width = 1
        return w

    def _check_X_y(self, X, y, *, method='fit', unit_ids=None):

        unit_ids = self._check_unit_ids_from_X(X, method=method, unit_ids=unit_ids)
        if isinstance(X, core.BinnedEventArray):
            if method == 'fit':
                self._w.bin_width = X.ds
                logging.info('Updating DataWindow.bin_width from training data.')
            else:
                if self._w.bin_width != X.ds:
                    raise ValueError('BayesianDecoder was fit with a bin_width of {}, but is being used to predict data with a bin_width of {}'.format(self.w.bin_width, X.ds))

            X, T = self.w.transform(X)

            if isinstance(y, core.RegularlySampledAnalogSignalArray):
                y = y(T).T

        if isinstance(y, core.RegularlySampledAnalogSignalArray):
            raise TypeError('y can only be a RegularlySampledAnalogSignalArray if X is a BinnedEventArray.')

        assert len(X) == len(y), "X and y must have the same number of samples!"

        return X, y

    def _ratemap_permute_unit_order(self, unit_ids):
        """Permute the unit ordering.

        If no order is specified, and an ordering exists from fit(), then the
        data in X will automatically be permuted to match that registered during
        fit().

        Parameters
        ----------
        unit_ids : array-like, shape (n_units,)
        """
        unit_ids = self._check_unit_ids(unit_ids)
        if len(unit_ids) != len(self._unit_ids):
            raise ValueError("To re-order (permute) units, 'unit_ids' must have the same length as self._unit_ids.")
        raise NotImplementedError("Ratemap re-ordering has not yet been implemented.")

    def _check_unit_ids(self, unit_ids):
        for unit_id in unit_ids:
            # NOTE: the check below allows for predict() to pass on only
            # a subset of the units that were used during fit! So we
            # could fit on 100 units, and then predict on only 10 of
            # them, if we wanted.
            if unit_id not in self._unit_ids:
                raise ValueError('unit_id {} was not present during fit(); aborting...'.format(unit_id))

    def _check_unit_ids_from_X(self, X, *, method='fit', unit_ids=None):
        if isinstance(X, core.BinnedEventArray):
            if unit_ids is not None:
                logging.warning("X is a nelpy BinnedEventArray; kwarg 'unit_ids' will be ignored")
            unit_ids = X.series_ids
            n_units = X.n_series
        else:
            n_units = X.shape[-1]
            if unit_ids is None:
                unit_ids = np.arange(n_units)

        if len(unit_ids) != n_units:
            raise ValueError("'X' has {} units, but 'unit_ids' has shape ({},).".format(n_units, len(unit_ids)))
        if method == 'fit':
            self._unit_ids = unit_ids
        else:
            self._check_unit_ids(unit_ids)
        return unit_ids

    def fit(self, X, y, *, lengths=None, unit_ids=None, sample_weight=None):
        """Fit Gaussian Naive Bayes according to X, y

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features.
                OR
            nelpy.core.BinnedEventArray / BinnedSpikeTrainArray
                The number of spikes in each time bin for each neuron/unit.
        y : array-like, shape (n_samples, n_output_dims)
            Target values.
                OR
            nelpy.core.RegularlySampledAnalogSignalArray
                containing the target values corresponding to X.
            NOTE: If X is an array-like, then y must be an array-like.
        lengths : array-like, shape (n_epochs,), optional (default=None)
            Lengths (in samples) of contiguous segments in (X, y).
            .. versionadded:: x.xx
                BayesianDecoder does not yet support *lengths*.
        unit_ids : array-like, shape (n_units,), optionsl (default=None)
            Persistent unit IDs that are used to associate units after
            permutation. Unit IDs are inherited from nelpy.core.BinnedEventArray
            objects, or initialized to np.arange(n_units).
        sample_weight : array-like, shape (n_samples,), optional (default=None)
            Weights applied to individual samples (1. for unweighted).
            .. versionadded:: x.xx
               BayesianDecoder does not yet support fitting with *sample_weight*.
        Returns
        -------
        self : object
        """

        # self._check_unit_ids(X, unit_ids, method='fit')
        ratemap = RateMap()
        X, y = self._check_X_y(X, y, method='fit')

        self.ratemap_ = None
        # return self._partial_fit(X, y, np.unique(y), _refit=True,
        #                          sample_weight=sample_weight)

    def predict(self, X, *, lengths=None, unit_ids=None):
        check_is_fitted(self, 'ratemap_')
        unit_ids = self._check_unit_ids_from_X(X, unit_ids=unit_ids)
        raise NotImplementedError
        ratemap = self._get_temp_ratemap(unit_ids)
        return self._predict_from_ratemap(X, ratemap)

    def predict_proba(self, X, *, lengths=None, unit_ids=None):
        check_is_fitted(self, 'ratemap_')
        unit_ids = self._check_unit_ids_from_X(X, unit_ids=unit_ids)
        raise NotImplementedError
        ratemap = self._get_temp_ratemap(unit_ids)
        return self._predict_proba_from_ratemap(X, ratemap)

    def score(self, X, y, *, lengths=None, unit_ids=None):
        check_is_fitted(self, 'ratemap_')
        # X = self._permute_unit_order(X)
        X, y = self._check_X_y(X, y, method='score', unit_ids=unit_ids)
        unit_ids = self._check_unit_ids_from_X(X, unit_ids=unit_ids)
        raise NotImplementedError
        ratemap = self._get_temp_ratemap(unit_ids)
        return self._score_from_ratemap(X, ratemap)

    def score_samples(self, X, y, *, lengths=None, unit_ids=None):
        # X = self._permute_unit_order(X)
        check_is_fitted(self, 'ratemap_')
        raise NotImplementedError


class FiringRateEstimator(BaseEstimator):
    """
    FiringRateEstimator
    Estimate the firing rate of a spike train.

    mode = ['hist', 'glm-poisson', 'glm-binomial', 'glm', 'gvm', 'bars', 'gp']

    (gvm = generalized von mises; see http://kordinglab.com/spykes/getting-started.html)

    QQQ. Do we always bin first? does GLM and BARS use spike times, or binned
         spike counts? I think GLM uses binned spike counts with Poisson
         regression; not sure about BARS.

    QQQ. What other methods should be supported? BAKS? What is state of the art?

    QQQ. What if we want to know the fring rate over time? What does the input y
         look like then? How about trial averaged? How about a tuning curve?

    AAA. At the end of the day, this class should estimate a ratemap, and we
         need some way to set the domain of that ratemap, if desired, but it
         should not have to assume anything else. Values in y might be repeated,
         but if not, then we estimate the (single-trial) firing rate over time
         or whatever the associated y represents.

    See https://arxiv.org/pdf/1602.07389.pdf for more GLM intuition? and http://www.stat.columbia.edu/~liam/teaching/neurostat-fall18/glm-notes.pdf

    [2] https://www.biorxiv.org/content/biorxiv/early/2017/02/24/111450.full.pdf?%3Fcollection=
    http://kordinglab.com/spykes/getting-started.html
    https://xcorr.net/2011/10/03/using-the-binomial-glm-instead-of-the-poisson-for-spike-data/

    [1] http://www.stat.cmu.edu/~kass/papers/bars.pdf
    https://gist.github.com/AustinRochford/d640a240af12f6869a7b9b592485ca15
    https://discourse.pymc.io/t/bayesian-adaptive-regression-splines-and-mcmc-some-questions/756/5

    """

    def __init__(self, mode='hist', *args, **kwargs):
        self._mode = mode
        #TODO: check that mode is valid:

        # raise Exception if mode not supported or implemented yet
        pass

    def fit(self, X, y, lengths=None, sample_weight=None):
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

    def predict(self, X, lengths=None):
        raise NotImplementedError

    def predict_proba(self, X, lengths=None):
        raise NotImplementedError

    def score(self, X, y, lengths=None):
        raise NotImplementedError

    def score_samples(self, X, y, lengths=None):
        raise NotImplementedError


