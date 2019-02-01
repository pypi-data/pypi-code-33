#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np

from numpy.linalg import inv, norm, eig

from scipy.signal import fftconvolve

__all__ = []


def find_cov_multitrial(a, b, ddof=1):
    """
    Estimate the average covariance between two datasets across many trials

    :type a: ndarray
    :param a: a multivariate time series of shape nsignals x nsamples x ntrials

    :type b: ndarray
    :param b: a multivariate time series of shape nsignals x nsamples x ntrials

    :type ddof: None orint
    :param ddof: if None, no normalisation will be performed.  If an integer,
                 covariance will be normalised by (nsamples - ddof)

    :rtype: ndarray
    :return: A covariance matrix between a and b of shape nsignals x nsignals
    """
    nsignals = a.shape[0]
    nsamples = a.shape[1]
    ntrials = a.shape[2]

    # Make sure datasets are demeaned before calculating covariance
    a = a - a.mean(axis=1)[slice(None), np.newaxis]
    b = b - b.mean(axis=1)[slice(None), np.newaxis]

    cov = np.zeros((nsignals, nsignals, ntrials), dtype=np.complex)

    for i in range(ntrials):
        b_h = np.array(np.matrix(b[:, :, i]).H)
        cov[:, :, i] = a[:, :, i].dot(b_h)

    if ddof is not None:
        return cov.mean(axis=2) / (nsamples - ddof)
    else:
        return cov.mean(axis=2)


__all__.append('find_cov_multitrial')


def find_cov(a, b, ddof=1):
    """
    Estimate the covariance between two datasets.

    :type a: ndarray
    :param a: a multivariate time series of shape nsignals x nsamples

    :type b: ndarray
    :param b: a multivariate time series of shape nsignals x nsamples

    :type ddof: int
    :param ddof: if None, no normalisation will be performed.  If an integer,
                 covariance will be normalised by (nsamples - ddof)

    :rtype: ndarray
    :return: A covariance matrix between a and b of shape nsignals x nsignals
    """

    nsamples = float(a.shape[1])

    # Make sure datasets are demeaned before calculating covariance
    a = a - a.mean(axis=1)[slice(None), np.newaxis]
    b = b - b.mean(axis=1)[slice(None), np.newaxis]

    b_h = np.array(np.matrix(b).H)
    cov = a.astype(np.complex).dot(b_h)

    if ddof is not None:
        return cov / (nsamples - ddof)
    else:
        return cov


__all__.append('find_cov')


def mutual_information(A, B, r=None, nbins=21, base=np.log2):
    """
    Calculate the mutual information between two signals.

    :type A: ndarray
    :param A: First signal, of shape [channels x samples]

    :type B: ndarray
    :param B: Second signal, of shape [channels x samples]

    :type r: tuple (float, float)
    :param r: Range of the random variables used for bin calculations.
              If not set, takes the minimum and maximum values from
              the combination of A and B

    :type nbins: int
    :param nbins: Number of bins to compute the frequencies within

    :type base: function
    :param base: Base to use for MI calculation - defaults to np.log2

    :rtype: ndarray
    :return: the mutual information within each signal passed
    """

    if A.ndim != 2 or B.ndim != 2:
        raise ValueError("Require 2D arrays for A and B")

    nsignals = A.shape[0]

    if r is None:
        r = (min(A.min(), B.min()), max(A.max(), B.max()))

    MI = np.zeros((nsignals,))

    for s in range(nsignals):
        PA = np.histogram(A[s, :], range=r,
                          bins=nbins)[0].astype(np.float64)
        PB = np.histogram(B[s, :], range=r,
                          bins=nbins)[0].astype(np.float64)
        PAB = np.histogram2d(A[s, :], B[s, :], range=(r, r),
                             bins=nbins)[0].astype(np.float64)

        # Outer product
        Pmarg = np.dot(np.atleast_2d(PA).T, np.atleast_2d(PB))

        # Scale the PAB and Pmarg matrices
        PAB /= PAB.sum()
        Pmarg /= Pmarg.sum()

        # Handle 0s properly
        idx_x, idx_y = np.nonzero(PAB / Pmarg)

        tmp = base(PAB[idx_x, idx_y] / Pmarg[idx_x, idx_y])
        MI[s] = np.sum(PAB[idx_x, idx_y] * tmp)

    return MI


__all__.append('mutual_information')


def durbin_watson(residuals, step=1):
    """
    Test for autocorrelation in the residuals of a model.

    The result is a value between 0 and 4. A value of 0 indicates a positive
    autocorrelaiton, 2 indicates no correlation and a value of 4 indicates a
    negative autocorrelation.

    If many trials are found the statistic is estimated for each trial
    separately.

    :type residuals: ndarray
    :param residuals: Residuals of shape [channels, samples, ntrials]
                      If only two dimensions, will be treated as
                      [channels, samples]
                      If only one dimension, will be treated as [samples]

    :type step: int
    :param step: step-size to use through residuals when calculating DW.
                 Defaults to 1.

    :rtype: ndarray
    :return: durbin-watson index
    """

    if residuals.ndim == 1:
        residuals = residuals[np.newaxis, slice(None), np.newaxis]
    elif residuals.ndim == 2:
        residuals = residuals[..., np.newaxis]
    elif residuals.ndim != 3:
        raise ValueError("residuals must be 1, 2 or 3D")

    # Calculation needs to be performed in the complex domain
    residuals = residuals.astype(np.complex)
    d_resid = residuals[:, :-step, :] - residuals[:, step:, :]

    # Combine all trials by flattening axes 0 and 1
    d_resid = d_resid.reshape(d_resid.shape[0]*d_resid.shape[1],
                              d_resid.shape[2])

    residuals = residuals.reshape(residuals.shape[0]*residuals.shape[1],
                                  residuals.shape[2])

    num = d_resid.T.dot(d_resid).real
    den = (residuals.T.dot(residuals)).real

    return np.diag(num / den).astype(np.float64)


__all__.append('durbin_watson')


def percent_consistency(data, residuals):
    """
    Estimate how well a model retains the correlational structure of a dataset.

    This uses the percent consistency measure outlined in Ding et al 2000. All
    auto and cross correlations within a multivariate data set are computed and
    compared to the auto and cross correlations of the data as predicted by a
    model (in this case the data - model residuals, as these are easily
    obtained).

    :type data: numpy.ndarray
    :param data: An array containing the observed data, of shape [nsignals x
                 nsamples x ntrials]

    :type data: numpy.ndarray
    :param residuals: An array containing the remaining variance of data after
                      model fitting, of shape [nsignals x nsamples x ntrials]

    :rtype float:
    :return: A value between 0 and 100 indicating the percentage of the
             autocorrelation in the data that is retained in the model.
    """

    if data.shape != residuals.shape:
        raise ValueError("data and residuals must be the same shape")

    if data.ndim == 1:
        data = data[np.newaxis, ..., np.newaxis]
        residuals = residuals[np.newaxis, ..., np.newaxis]
    elif data.ndim == 2:
        data = data[..., np.newaxis]
        residuals = residuals[..., np.newaxis]
    elif residuals.ndim != 3:
        raise ValueError("data and residuals must be 1, 2 or 3D")

    resid = residuals

    # Preallocate arrays for the correlations

    # Real
    R_r = np.zeros((data.shape[0], data.shape[0],
                    data.shape[2], data.shape[1]), dtype=np.complex)
    # Prediction
    R_p = np.zeros((data.shape[0], data.shape[0],
                    data.shape[2], data.shape[1]), dtype=np.complex)

    # Compute auto and cross correlations
    for i in range(data.shape[0]):  # node
        for j in range(data.shape[0]):  # node
            for t in range(data.shape[2]):  # epoch
                # array flipped convolution which is faster for large arrays.
                # This is an fft based method for computing the cross
                # correlation
                R_r[i, j, t, :] = fftconvolve(data[i, :, t],
                                              data[j, ::-1, t],
                                              mode='same')
                R_p[i, j, t, :] = fftconvolve(data[i, :, t]-resid[i, :, t],
                                              data[j, ::-1, t]-resid[j, :, t],
                                              mode='same')

    # Reshape into a vector
    R_r = R_r.reshape(-1)
    R_p = R_p.reshape(-1)

    # Calculate and return PC as defined in Ding et al 2000 - eq 12
    num = norm(R_p - R_r)
    denom = norm(R_r)

    percent_consistency = (1 - (num / denom)) * 100

    return np.float64(percent_consistency)


__all__.append('percent_consistency')


def rsquared_from_residuals(data, residuals, per_signal=False):
    """
    Estimate the variance explained by a model from the original data and the
    model residuals

    If data and residuals are 2D, they will be treated as [channels, nsamples]

    If data and residuals are 1D, they will be treated as [nsamples]

    :type data: ndarray
    :param data: Array containing the original data,
                 of shape [channels, nsamples, ntrials]

    :type residuals: ndarray
    :param residuals: Array containing the model residuals,
                      of shape [channels, nsamples, ntrials]

    :type per_signal: bool
    :param per_signal: Boolean indicating whether the variance explained
                       should be computed separately per channel

    :rtype: float
    :return: Value between 0 and 1 indicating the proportion of variance
             explained by the model.
    """

    if data.shape != residuals.shape:
        raise ValueError("data and residuals must be the same shape")

    if data.ndim == 1:
        data = data[np.newaxis, ..., np.newaxis]
        residuals = residuals[np.newaxis, ..., np.newaxis]
    elif data.ndim == 2:
        data = data[..., np.newaxis]
        residuals = residuals[..., np.newaxis]
    elif residuals.ndim != 3:
        raise ValueError("data and residuals must be 1, 2 or 3D")

    if per_signal:
        dat = (data**2.0).sum(axis=1).sum(axis=1)
        res = (residuals**2.0).sum(axis=1).sum(axis=1)
    else:
        dat = (data**2.0).sum()
        res = (residuals**2.0).sum()

    return np.float64(1 - (res.real / dat.real))


__all__.append('rsquared_from_residuals')


def mahalanobis(X, Y=None, sigma=None):
    """
    Estimate the mahalanobis distance of each point in an array across the
    samples dimension.

    :type X: ndarray
    :param X: Array containing data of points: shape [channels x samples]

    :type Y: ndarray or None
    :param Y: Optional Array containing data of second points: shape
              [channels x samples].  If not provided, the origin will be
              used as the point for comparison.

    :type sigma: ndarray or None
    :param sigma: A precomputed covariance matrix to use in the calculation,
                  of shape [channels x channels].  If not provided, sigma
                  will be calculated from X

    :rtype: ndarray
    :return: The mahalanobis distance for each sample, of shape [samples]
    """

    if Y is not None:
        if Y.shape != X.shape:
            raise ValueError("If Y is provided, must be the same shape as X")

        # Offset the points
        X = X - Y

    # Calculate our covariance matrix if necessary
    if sigma is None:
        sigma = np.cov(X)

    sigma_i = inv(sigma)

    return np.diag(X.T.dot(sigma_i).dot(X))


__all__.append('mahalanobis')


def profile_likelihood(X):
    """
    Find the 'elbow' point in a curve.

    This function uses the automatic dimensionality selection method from Zhu
    et al 2006 to estimate the elbow or inflection point in a given curve.

    Method can be found in Mu Zhu, Ali Ghodsi. Computational Statistics & Data
    Analysis 51 (2006) 918 - 930

    :param X: 1d array containing the curve to be analysed, of shape [samples]
    :type X: ndarray

    :rtype: ndarray
    :return: The log likelihood that each point on the curve separates the
             distributions to the left and right, of shape [samples]
    """

    # Handle 2D arrays with a singleton second dimension
    X = X.squeeze()
    if X.ndim != 1:
        raise ValueError("Only 1D matrices supported by profile_likelihood")

    llh = np.zeros_like(X)

    for i in range(2, X.shape[0]-1):
        left = X[0: i]
        right = X[i:-1]

        # Common scale parameter
        csp = ((i-1)*left.var() + (len(X)-i-1)*right.var()) / (len(X)-2.)

        left_power = (left - left.mean())**2 / 2*csp
        left_side = np.sum(1.0 / np.sqrt(2*np.pi*csp) * np.exp(-left_power))

        right_power = (right - right.mean())**2 / 2*csp
        right_side = np.sum(1.0 / np.sqrt(2*np.pi*csp) * np.exp(-right_power))

        llh[i] = left_side + right_side

    return llh


__all__.append('profile_likelihood')


def stability_index(A):
    """
    Compute the stability index as defined in Lutkepohl 2006 pg 11.

    This is a proxy for the stationarity assumption of MVAR models, if the
    magnitude of the largest principal component of the model parameters is
    less than 1, the model is stable and thus, stationary.

    :type a: numpy.ndarray
    :param a: The MVAR parameter matrix

    :rtype: float
    :return: The stability index
    """

    nsignals = A.shape[0]
    order = A.shape[2]

    # Form companion matrix
    companion = np.eye(nsignals*(order-1), k=nsignals).T
    companion[:nsignals, :] = A[:, :, 1:].reshape((nsignals,
                                                   nsignals*(order-1)),
                                                  order='F')

    # Find eigenvalues
    evals, evecs = eig(companion)

    # Find the largest magnitude
    stability_index = np.abs(evals).max()

    return np.float64(stability_index)


__all__.append('stability_index')


def stability_ratio(A):
    """
    Compute the stability ratio as a measure of stationarity

    A stronger test for stationarity than the stability index. Computes the
    ratio between the largest eigenvalue of the parameters and all the others.
    If the largest parameter is larger than all other parmeters (indicated by a
    value < 1) we have a super-stable system.

    :type a: numpy.ndarray
    :param a: The MVAR parameter matrix

    :rtype float:
    :return: The stability ratio
    """

    nsignals = A.shape[0]
    order = A.shape[2]

    # Form companion matrix
    companion = np.eye(nsignals*(order-1), k=nsignals).T
    companion[:nsignals, :] = A[:, :, 1:].reshape((nsignals,
                                                   nsignals*(order-1)),
                                                  order='F')

    # Find eigenvalues
    evals, evecs = eig(companion)

    # Take the magnitude
    evals = np.abs(evals)

    # Get the smaller eigen values
    evals_smaller = evals[np.where(evals != evals.max())]

    # Express the ratio
    stability_ratio = evals.max() / np.sum(evals_smaller)

    return np.float64(stability_ratio)


__all__.append('stability_ratio')
