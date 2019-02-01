#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import warnings

import numpy as np

from .stats import find_cov_multitrial, durbin_watson, \
    stability_index, stability_ratio, \
    rsquared_from_residuals, percent_consistency

from .modelvalidation import approx_model_selection_criteria

__all__ = []


def A_to_companion(A):
    """
    Tranforms a [nsignals x nsignals x order] MVAR parameter array into the
    [nsignals*order x nsignals*order] companion form. This assumes there is no
    leading identity matrix in the A form.

    :param A: MVAR parameter array of size [nsignals, nsignals, order]
    """

    nsignals = A.shape[0]
    order = A.shape[2]
    companion = np.eye(nsignals*(order), k=nsignals, dtype=A.dtype).T
    companion[:nsignals, :] = A.reshape((nsignals, nsignals*order), order='F')

    return companion


def get_residuals(data, parameters, delay_vect, backwards=False):
    """
    TODO: Description

    :param data: TODO
    :param parameters: TODO
    :param delay_vect: TODO
    :param backwards: TODO

    :returns: TODO
    """
    # TODO: double check that we are including all the order
    resid = np.zeros_like(data, dtype=complex)

    # for each epoch...
    for ntrial in range(data.shape[2]):
        if backwards:
            pred = np.zeros_like(data[:, :, 0], dtype=complex)

            for m in range(1, len(delay_vect)):
                tmp = parameters[:, :, m].dot(data[:, :, ntrial])
                pred[:, :-delay_vect[m]] += tmp[:, delay_vect[m]:]

            resid[:, :, ntrial] = data[:, :, ntrial] - pred[...]

        else:
            pred = np.zeros_like(data[:, :, 0], dtype=complex)

            for m in range(1, len(delay_vect)):
                tmp = parameters[:, :, m].dot(data[:, :, ntrial])
                pred[:, delay_vect[m]:] += tmp[:, :-delay_vect[m]]

            resid[:, :, ntrial] = data[:, :, ntrial] - pred[...]

    return resid


__all__.append('get_residuals')


class AbstractLinearModel(object):
    """
    TODO: Description
    """

    # This is only used within NAF
    hdf5_outputs = ['data_cov', 'resid_cov', 'parameters',
                    'maxorder', 'delay_vect']

    @property
    def nsignals(self):
        """Number of signals in fitted model"""
        return self.parameters.shape[0]

    @property
    def order(self):
        """Order of fitted model"""
        return self.parameters.shape[2] - 1

    @property
    def companion(self):
        """Parameter matrix in companion form"""
        return A_to_companion(self.parameters[:, :, 1:])

    def compute_diagnostics(self, data, compute_pc=False):
        """
        Compute several diagnostic metrics from a fitted MVAR model and a
        dataset.

        :rtype: diags.ModelDiagnostics
        :return: ModelDiagnostics object containing LL, AIC, BIC, stability
                 ratio, durbin-watson, R squared and percent consistency
                 measures
        """

        from .diags import ModelDiagnostics

        ret = ModelDiagnostics()

        # Get residuals
        resid = self.get_residuals(data)

        # Get covariance of the residuals
        ret.resid_cov = find_cov_multitrial(resid, resid)

        # Compute Durbin-Watson test for residual autocorrelation
        ret.DW = durbin_watson(resid, step=np.diff(self.delay_vect)[0])

        # Compute the stability index and ratio
        ret.SI = stability_index(self.parameters)
        ret.SR = stability_ratio(self.parameters)

        # Estimate the R^2 - per signal
        ret.R_square = rsquared_from_residuals(data, resid, per_signal=True)

        # Estimate Percent Consistency - Ding et al 2000.
        if compute_pc:
            # This can cause memory issues with large datasets
            ret.PC = percent_consistency(data, resid)

        # Compute LL, AIC and BIC
        # LL, AIC, BIC = est_model_selection_criteria(self.parameters, resid)

        # Approximate AIC and BIC
        LL, AIC, BIC = approx_model_selection_criteria(self.parameters, resid)

        ret.LL = LL
        ret.AIC = AIC
        ret.BIC = BIC

        return ret

    def get_residuals(self, data):
        """
        Returns the prediction error from a fitted model. This is a wrapper
        function for get_residuals()

        :param data: TODO
        """

        if self.parameters.ndim == 3:
            resid = get_residuals(data,
                                  self.parameters,
                                  self.delay_vect,
                                  backwards=False)
        elif self.parameters.ndim == 4:
            # We have different parameters for each epoch
            resid = get_residuals(np.atleast_3d(data[..., 0]),
                                  self.parameters[..., 0],
                                  self.delay_vect,
                                  backwards=False)
            for e in range(1, self.parameters.shape[3]):
                tmp = get_residuals(np.atleast_3d(data[..., e]),
                                    self.parameters[..., e],
                                    self.delay_vect,
                                    backwards=False)
                resid = np.concatenate((resid, tmp), axis=2)

        return resid


__all__.append('AbstractLinearModel')


class VieiraMorfLinearModel(AbstractLinearModel):
    """
    TODO: Description
    """

    # This is only used within NAF
    hdf5_outputs = AbstractLinearModel.hdf5_outputs + ['bwd_parameters']

    def get_residuals(self, data, forward_parameters=True):
        """
        Returns the prediction error from a fitted model. This is a wrapper
        function for get_residuals()

        :param forward_parameters: If True, use forward parameters, otherwise
                                   use backward parameters
        :type forward_parameters: bool
        """

        if not forward_parameters:
            if self.bwd_parameters.ndim == 3:
                resid = get_residuals(data,
                                      self.bwd_parameters,
                                      self.delay_vect,
                                      backwards=True)
            elif self.bwd_parameters.ndim == 4:
                # We have different parameters for each epoch
                resid = get_residuals(data[..., 0],
                                      self.bwd_parameters[..., 0],
                                      self.delay_vect,
                                      backwards=True)
                for e in range(1, self.bwd_parameters.shape[3]):
                    tmp = get_residuals(data[..., e],
                                        self.bwd_parameters[..., e],
                                        self.delay_vect,
                                        backwards=True)
                    resid = np.concatenate((resid, tmp), axis=2)
        else:
            resid = AbstractLinearModel.get_residuals(self, data)

        return resid

    @classmethod
    def fit_model(cls, data, delay_vect):
        """
        Estimates the multichannel autoregressive spectral estimators
        using a Vieira-Morf algorithm. Equations are referenced to Marple,
        appendix 15.B.

        This is the multitrial versions of the algorithm, using the AMVAR
        method outlined in Ding 2000.

        :param data: array of shape [nsignals, nsamples, ntrials]
        :type data: numpy.ndarray

        :param delay_vect: Vector containing evenly spaced delays to be
                           assessed in the model.  Delays are represented in
                           samples.  Must start with zero.
        :type delay_vect: numpy.ndarray

        :param assess_order: Optional True/False value indicating whether
                             additional information about each iteration of
                             the fit should be returned. Defaults to False
        :type assess_order: bool

        :returns: A populated object containing the fitted forward and
                  backwards coefficients and several other useful variables and
                  methods.
        """

        # Create object
        ret = cls()

        # Shorter reference
        X = data

        # Set-up inital parameters
        delay_vect = delay_vect.astype(int)
        nsignals = X.shape[0]
        ntrials = X.shape[2]
        ret.assess_order = False
        maxorder = delay_vect.shape[0]-1

        # Begin model fitting
        #  Relevant parameters:
        #  A      - Forward linear prediction coefficients matrix
        #  B      - Backward linear prediction coefficients matrix
        #  PF     - Forward linear prediction error covariance
        #  PB     - Backward linear prediction error covariance
        #  PFH    - Estimate of forward linear prediction error covariance
        #  PBH    - Estimate of backward linear prediction error covariance
        #  PFBH   - Estimate of linear prediction error covariance
        #  RHO    - Estimate of the partial correlation matrix
        #  EF     - Forward linear prediction error
        #  EB     - Backward linear prediction error

        # Initialisation

        # Eq 15.91
        # Initialise prediction error as the data
        EF = X.copy().astype(complex)
        EB = X.copy().astype(complex)

        # Eq 15.90
        # Initialise error covariance as the data covariance
        PF = find_cov_multitrial(X, X)
        PB = find_cov_multitrial(X, X)

        # Set order zero coefficients to identity
        A = np.ndarray((nsignals, nsignals, maxorder+1), dtype=complex)
        A[:, :, 0] = np.eye(nsignals)

        # TODO: double check that this is correct behaviour
        B = np.ndarray((nsignals, nsignals, maxorder+1), dtype=complex)
        B[:, :, 0] = np.zeros(nsignals)

        # Main Loop

        M = 0
        while M < maxorder:

            # Create clean arrays for the estimates of the error covariance
            PFH = np.zeros((nsignals, nsignals))
            PBH = np.zeros((nsignals, nsignals))
            PFBH = np.zeros((nsignals, nsignals))

            # Eq 15.89 - get estimates of forward and backwards covariance
            PFH = find_cov_multitrial(EF[:, delay_vect[M+1]:, :],
                                      EF[:, delay_vect[M+1]:, :])
            PBH = find_cov_multitrial(EB[:, delay_vect[M]:-delay_vect[1], :],
                                      EB[:, delay_vect[M]:-delay_vect[1], :])
            PFBH = find_cov_multitrial(EF[:, delay_vect[M+1]:, :],
                                       EB[:, delay_vect[M]:-delay_vect[1], :])

            # Eq 15.88 - compute estimated normalised partial correlation
            # matrix
            tmp = np.linalg.inv(np.linalg.cholesky(PFH)).dot(PFBH)
            chol = np.linalg.cholesky(PBH)
            RHO = tmp.dot(np.array(np.mat(np.linalg.inv(chol)).H))

            M += 1

            # Eq 15.82 & 15.83 - Update forward and backward reflection
            # coefficients
            tmp = np.linalg.cholesky(PF).dot(RHO)
            A[:, :, M] = - tmp.dot(np.linalg.inv(np.linalg.cholesky(PB)))

            tmp = np.linalg.cholesky(PB).dot(np.array(np.mat(RHO).H))
            B[:, :, M] = - tmp.dot(np.linalg.inv(np.linalg.cholesky(PF)))

            # Eq 15.75 & 15.76 - Update forward and backward error covariances
            tmp = np.eye(nsignals) - (A[:, :, M].dot(B[:, :, M]))
            PF = tmp.dot(PF)

            tmp = np.eye(nsignals) - (B[:, :, M].dot(A[:, :, M]))
            PB = tmp.dot(PB)

            # might not need this if statement, subsequent xrange will handle
            # it, # though this is clearer
            if M > 1:
                A_t = A.copy()
                B_t = B.copy()

                # We are working from the equations - the FORTRAN is wrong!

                # Eq 15.71 & 15.72 - Update forward and backward predictor
                # coefficients
                for k in range(1, M):
                    mk = M-k

                    # TODO  - double check backwards coeffs against Ding2000
                    # simulations
                    A[:, :, k] = A_t[:, :, k] + A[:, :, M].dot(B_t[:, :, mk])
                    B[:, :, k] = B_t[:, :, k] + B[:, :, M].dot(A_t[:, :, mk])

            # Eq 15.84 & 15.85 - Update the residuals
            for t in range(ntrials):
                tmp = EF[:, :, t].copy()
                tmp2 = EB[:, :, t].copy()

                update_A = A[:, :, M].dot(tmp2[:, :-delay_vect[1]])
                EF[:, delay_vect[1]:, t] = tmp[:, delay_vect[1]:] + update_A

                update_B = B[:, :, M].dot(tmp[:, delay_vect[1]:])
                EB[:, delay_vect[1]:, t] = tmp2[:, :-delay_vect[1]] + update_B

        # Sanity check and return

        # Sanity check for single channel case
        if nsignals == 1 and np.allclose(PF, PB) is False:
            ret.status = -1
            warnings.warn("Warning: problem with model fit. PF != PB. "
                          "See single channel identity in Marple "
                          "top of p405")

        # Populate return object
        ret._data = X
        ret.data_cov = find_cov_multitrial(X, X)
        ret.resid_cov = find_cov_multitrial(EF, EF)
        ret.maxorder = maxorder
        ret.delay_vect = delay_vect

        # Correct for sign flip in VM estimatation
        ret.parameters = -A
        ret.bwd_parameters = -B

        return ret


__all__.append('VieiraMorfLinearModel')


class OLSLinearModel(AbstractLinearModel):
    """
    TODO: Description
    """

    @classmethod
    def fit_model(cls, data, delay_vect):
        """
        TODO: Description
        """

        # Create object
        ret = cls()

        # Set-up inital parameters
        nsignals = data.shape[0]
        nsamples = data.shape[1]
        ret.assess_order = False
        maxorder = delay_vect.shape[0]-1
        maxlag = delay_vect[-1].astype(int)

        # Preallocate design matrix
        X = np.zeros((nsamples-maxlag, nsignals*maxorder))
        # Preallocate observation matrix
        Y = np.zeros((nsamples-maxlag, nsignals))

        # Create design matrix
        for idx in range(nsamples-maxlag):
            X[idx, :] = data[:, -delay_vect[1::].astype(int)+idx].reshape(-1)
            Y[idx, :] = data[:, idx, 0]

        # B is shaped [maxorder*nsignals, nsignals]
        #
        # [ A[1, 1, 1] A[1, 1, 2] ... A[1, 1, p] A[1, 2, 1] A[1, 2, 2] ... A[1, 2, p] ]
        # [ A[2, 1, 1] A[2, 1, 2] ... A[2, 1, p] A[2, 2, 1] A[2, 2, 2] ... A[2, 2, p] ]

        # Normal equations
        B = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(Y)

        # Reshape output
        parameters = np.zeros((nsignals, nsignals, maxorder+1))
        parameters[..., 0] = -np.eye(nsignals)
        for idx in range(nsignals):
            parameters[:, idx, 1:] = B[idx*maxorder:(idx+1)*maxorder].T

        resids = get_residuals(data, -parameters, delay_vect)
        ret.data_cov = find_cov_multitrial(data, data)
        ret.resid_cov = find_cov_multitrial(resids, resids)
        ret.parameters = parameters
        ret.maxorder = maxorder
        ret.delay_vect = delay_vect

        return ret


__all__.append('OLSLinearModel')


def sliding_window_fit(model_class, data, delay_vect,
                       win_len_samp, win_step_samp,
                       compute_diagnostics=True):

        # Compute start and end samples of our windows
        start_pts = list(range(0,
                               data.shape[1] - max(delay_vect) - win_len_samp,
                               win_step_samp))
        end_pts = [x + win_len_samp for x in start_pts]

        # Preallocate model outputs
        params = np.zeros((data.shape[0], data.shape[0],
                           len(delay_vect), len(start_pts)))
        resid_cov = np.zeros((data.shape[0], data.shape[0],
                              len(start_pts)))

        # Preallocate diagnostic outputs
        if compute_diagnostics:
            # This is a bit clunky, should probably make a slidingwindow model
            # diagnostics class with a simpler append_pts function. Also review
            # how necessary model diagnostic class is anyway, mainly used for a
            # custom print statement
            from .diags import ModelDiagnostics
            D = ModelDiagnostics()

            D.R_square = []
            D.SR = []
            D.DW = []
            D.PC = []
            D.AIC = []
            D.BIC = []
            D.LL = []
            D.SI = []

        # Main model loop
        x = np.zeros((win_len_samp, len(start_pts)))
        for ii in range(len(start_pts)):
            x = data[:, start_pts[ii]:end_pts[ii], :]

            # Fit model
            m = model_class.fit_model(x, delay_vect)
            params[:, :, :, ii] = m.parameters
            resid_cov[:, :, ii] = m.resid_cov

            # Compute diagnostics
            if compute_diagnostics:
                diag = m.compute_diagnostics(x)
                D.R_square.append(diag.R_square)
                D.SR.append(diag.SR)
                D.SI.append(diag.SI)
                D.DW.append(diag.DW)
                D.AIC.append(diag.AIC)
                D.BIC.append(diag.BIC)
                D.LL.append(diag.LL)

        # Create output class
        M = model_class()
        M.parameters = params
        M.resid_cov = resid_cov
        M.delay_vect = delay_vect
        M.win_len_samp = win_len_samp
        M.win_step_samp = win_step_samp
        M.time_vect = (np.array(start_pts) + np.array(end_pts)) / 2

        if compute_diagnostics:
            return M, D
        else:
            return M


__all__.append('sliding_window_fit')


def coloured_noise_fit(X, model_order):

    from .tutorial_utils import generate_pink_roots, model_from_roots

    # Intialise returned model
    M = AbstractLinearModel()
    M.parameters = np.zeros((X.shape[0], X.shape[0], model_order, X.shape[2]))
    M.resid_cov = np.eye(X.shape[0])  # Assumed for now
    M.delay_vect = np.arange(model_order)

    # Range of 1/f^alpha values to explore
    powers = np.linspace(.05, 1.95, 200)

    fit_inds = np.zeros((X.shape[0],), dtype=int)
    for ichan in range(X.shape[0]):
        ss = np.zeros(powers.shape)
        for ii in range(len(powers)):

            rts = generate_pink_roots(powers[ii], order=model_order)
            m = model_from_roots(rts)

            resid = get_residuals(X[None, ichan, :, :], m.parameters, np.arange(model_order))
            ss[ii] = np.power(resid, 2).sum()

        fit_inds[ichan] = np.argmin(ss).astype(int)
        rts = generate_pink_roots(powers[fit_inds[ichan]], order=model_order)
        M.parameters[ichan, ichan, :, 0] = -np.poly(rts)

    fit_powers = powers[fit_inds]

    return M, fit_powers


__all__.append('coloured_noise_fit')
