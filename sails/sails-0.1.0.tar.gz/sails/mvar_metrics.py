#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np

from sails.support import ensure_leading_positive, ensure_leading_negative
from sails import plotting

__all__ = []


class AbstractMVARMetrics(object):
    """
    TODO: Description
    """
    @property
    def S(self):
        """Spectral Matrix of shape [nsignals, nsignals, order, epochs]"""
        return spectral_matrix(self.H, self.resid_cov)

    @property
    def PSD(self):
        """Power Spectral Density matrix"""
        return np.abs(psd_matrix(self.S, self.sample_rate))

    @property
    def inv_S(self):
        """TODO: Document"""
        return inv_spectral_matrix(self.H, self.resid_cov)

    @property
    def coherency(self):
        """TODO: Document"""
        return coherency(self.S)

    @property
    def magnitude_squared_coherence(self):
        """TODO: Document"""
        return magnitude_squared_coherence(self.S)

    @property
    def imaginary_coherence(self):
        """TODO: Document"""
        return imaginary_coherence(self.S)

    @property
    def phase_coherence(self):
        """TODO: Document"""
        return phase_coherence(self.S)

    @property
    def partial_coherence(self):
        """TODO: Document"""
        return partial_coherence(self.inv_S)

    @property
    def ff_directed_transfer_function(self):
        """TODO: Document"""
        return ff_directed_transfer_function(self.H)

    @property
    def d_directed_transfer_function(self):
        """TODO: Document"""
        return d_directed_transfer_function(self.H, self.inv_S)

    @property
    def directed_transfer_function(self):
        """TODO: Document"""
        return directed_transfer_function(self.H)

    @property
    def partial_directed_coherence(self):
        """TODO: Document"""
        return partial_directed_coherence(self.Af)

    @property
    def isolated_effective_coherence(self):
        """TODO: Document"""
        return isolated_effective_coherence(self.Af, self.resid_cov)

    @property
    def geweke_granger_causality(self):
        """TODO: Document"""
        return geweke_granger_causality(self.S, self.H, self.resid_cov)

    def plot_diags(self, metric='S', inds=None, F=None, ax=None):

        met = getattr(self, metric)
        plotting.plot_diagonal(self.freq_vect, met, title=metric, F=F, ax=ax)

    def plot_summary(self, metric='S', ind=1):

        met = getattr(self, metric)
        plotting.plot_metric_summary(self.freq_vect, met, ind=ind)

    def get_spectral_generalisation(self, metric='S'):

        met = np.abs(getattr(self, metric)[:, :, :, 0])
        met = met.reshape((met.shape[0]**2, met.shape[2]))

        return met.T.dot(met)

    def get_node_weight(self, metric='S'):

        met = np.abs(getattr(self, metric)[:, :, :, 0])
        for ii in range(met.shape[2]):
            met[:, :, ii] = met[:, :, ii] - np.diag(np.diag(met[:, :, ii]))

        nconnections = met.shape[0]+met.shape[1]-1

        return met[:, 0, :] + met[0, :, :] / nconnections


__all__.append('AbstractMVARMetrics')


class ModalMvarMetrics(AbstractMVARMetrics):

    # This is only used when used within NAF
    hdf5_outputs = ['resid_cov', 'freq_vect', 'H', 'modes']

    @classmethod
    def initialise(cls, model, sample_rate, freq_vect, nmodes=None):
        """
        Compute some basic values from the pole-residue decomposition of the A
        matrix

        Currently only implemented for a single realisation (A.ndim == 3)

        :param model: TODO
        :param sample_rate: TODO
        :param freq_vect: TODO
        :param nmodes: TODO
        """

        # Create object
        ret = cls()
        A = model.parameters
        resid_cov = model.resid_cov

        if A.ndim == 4:
            NotImplementedError('Modal Metrics only implemented for single '
                                'realisations of A')
        else:
            # Add dummy epoch
            A = A[..., None]

        A = ensure_leading_negative(A)

        if resid_cov.ndim == 2:
            resid_cov = resid_cov[..., None]  # Add a dummy epoch
        if resid_cov.shape[2] != A.shape[0]*A.shape[2]:
            # Repeat resid cov per epoch/mode (probably only valid for
            # modes...)
            resid_cov = np.repeat(resid_cov, A.shape[0]*A.shape[2], axis=-1)

        ret.resid_cov = resid_cov
        ret.freq_vect = freq_vect
        ret.sample_rate = sample_rate

        # Compute transfer function
        from .modal import MvarModalDecomposition
        ret.modes = MvarModalDecomposition.initialise(model,
                                                      sample_rate=sample_rate,
                                                      normalise=False)
        ret.H = ret.modes.transfer_function(sample_rate, freq_vect)

        return ret

    @classmethod
    def initialise_from_modes(cls, model, modes, sample_rate, freq_vect, mode_inds=None, sum_modes=True):
        # Create object
        ret = cls()
        ret.modes = modes
        ret.freq_vect = freq_vect
        ret.sample_rate = sample_rate

        A = model.parameters
        resid_cov = model.resid_cov

        if A.ndim == 4:
            NotImplementedError('Modal Metrics only implemented for single '
                                'realisations of A')
        else:
            # Add dummy epoch
            A = A[..., None]

        A = ensure_leading_positive(A)

        if resid_cov.ndim == 2:
            resid_cov = resid_cov[..., None]  # Add a dummy epoch
        if resid_cov.shape[2] != A.shape[0]*A.shape[2]:
            # Repeat resid cov per epoch/mode (probably only valid for
            # modes...)
            resid_cov = np.repeat(resid_cov, A.shape[0]*A.shape[2], axis=-1)
        ret.resid_cov = resid_cov

        if mode_inds is None:
            mode_inds = np.arange(modes.nmodes)

        # Compute transfer function
        ret.H = ret.modes.transfer_function(sample_rate, freq_vect,
                                            modes=mode_inds,
                                            sum_modes=sum_modes)

        return ret


__all__.append('ModalMvarMetrics')


class FourierMvarMetrics(AbstractMVARMetrics):
    """
    TODO: Document
    """

    # This is only used when used within NAF
    hdf5_outputs = ['resid_cov', 'freq_vect', 'H', '_A', 'Af']

    @classmethod
    def initialise(cls, model, sample_rate, freq_vect, nmodes=None):
        """
        Compute some basic values from A across our frequency vector

        """

        # Create object
        ret = cls()
        A = model.parameters
        resid_cov = model.resid_cov

        if A.ndim == 3:
            A = A[..., None]  # Add a dummy epoch

        ret._A = A

        A = ensure_leading_positive(A)

        if resid_cov.ndim == 2:
            resid_cov = resid_cov[..., None]  # Add a dummy epoch

        if resid_cov.shape[2] != A.shape[3]:
            # Repeat resid cov per epoch/mode (probably only valid for
            # modes...)
            resid_cov = np.repeat(resid_cov, A.shape[3], axis=-1)

        ret.resid_cov = resid_cov
        ret.freq_vect = freq_vect
        ret.sample_rate = sample_rate

        # Get frequency transform of A
        ret.Af = ar_spectrum(A, resid_cov, sample_rate, freq_vect)

        # Get transfer function
        ret.H = transfer_function(ret.Af)

        return ret


__all__.append('FourierMvarMetrics')


def modal_transfer_function(evals, evecl, evecr, nchannels,
                            sample_rate=None, freq_vect=None):
    """
    Comute the transfer function in pole-residue form, splitting the system
    into modes with separate transfer functions. The full system transfer
    function is then a linear sum of each modal transfer function.

    """

    if (sample_rate is None and freq_vect is not None) or \
       (sample_rate is not None and freq_vect is None):
        raise ValueError('Please define both sample_rate and freq_vect '
                         '(or neither to return normalised frequency 0->pi)')

    if freq_vect is None and sample_rate is None:
        # Use normalised frequency
        freq_vect_rads = np.linspace(0, np.pi, 512)
    else:
        # convert user defined frequecies to radians
        freq_vect_rads = (freq_vect / (sample_rate / 2.)) * np.pi

    # Compute transfer function per mode
    H = np.zeros((nchannels, nchannels,
                 len(freq_vect_rads), len(evals)), dtype=complex)

    # Compute point on unit circle for each frequency
    z = np.cos(freq_vect_rads) + 1j*np.sin(freq_vect_rads)

    for imode in range(len(evals)):

        # Compute residue matrix from left and right eigenvectors
        l = np.atleast_2d(evecl[:nchannels, imode]).T
        r = np.atleast_2d(evecr[:nchannels, imode]).conj()
        residue = l.dot(r)

        for ifreq in range(len(freq_vect_rads)):

            # Compute tranfer function for this frequency and this mode
            num = residue * z[ifreq]
            dom = z[ifreq] - evals[imode]
            H[:, :, ifreq, imode] = num / dom

    return H


__all__.append('modal_transfer_function')


# Spectrum estimators


def sdf_spectrum(A, sigma, sample_rate, freq_vect):
    """
    Estimate of the Spectral Density as found on wikipedia and Quirk & Liu 1983

    This assumes that the spectral representation of A is invertable

    """
    # model order
    order = A.shape[2] - 1
    nsignals = A.shape[0]
    T = 1./sample_rate
    spectrum = np.zeros((nsignals, nsignals, len(freq_vect)), dtype=complex)
    eye = np.eye(nsignals)

    for node1 in range(nsignals):
        for node2 in range(nsignals):
            for idx, f in zip(list(range(len(freq_vect))), freq_vect):

                est = eye[node1, node2]

                for k in range(1, order+1):
                    est = A[node1, node2, k] * np.exp(0-1j*2*np.pi*k*f*T)

                num = sigma[node1, node2] * T
                dom = np.abs(est)**2
                spectrum[node1, node2, idx] = num / dom

    return spectrum


__all__.append('sdf_spectrum')


def psd_spectrum(A, sigma, sample_rate, freq_vect):
    """
    Estimate the PSD representation of a set of MVAR coefficients as stated in
    Penny 2000 Signal processing course array.ps 7.41

    This assumes that the spectral representation of A is invertable

    TODO: This doesn't behave as expected for univariate?, sdf_spectrum
    recommended

    :param A: TODO
    :param sigma: TODO
    :param sample_rate: TODO
    :param freq_vect: TODO

    :returns: TODO
    """
    # model order
    order = A.shape[2] - 1
    nsignals = A.shape[0]
    T = 1./sample_rate
    spectrum = np.zeros((nsignals, nsignals, len(freq_vect)), dtype=complex)
    eye = np.eye(nsignals)

    for node1 in range(nsignals):
        for node2 in range(nsignals):
            for idx, f in zip(list(range(len(freq_vect))), freq_vect):

                # Normalised digital frequency
                f = f / sample_rate

                est = eye[node1, node2]

                for k in range(1, order+1):
                    est += A[node1, node2, k] * np.exp(0-1j*2*np.pi*k*f)

                spectrum[node1, node2, idx] = est

    # Compute the PSD_mvar

    psd = np.zeros_like(spectrum)
    for idx, f in zip(list(range(len(freq_vect))), freq_vect):
        A_inv = np.linalg.inv(spectrum[..., idx])
        # Hermitian of the inverse
        A_inv_herm = np.array(np.mat(A_inv).H)
        psd[:, :, idx] = T * (A_inv.dot(sigma).dot(A_inv_herm))

    return psd


__all__.append('psd_spectrum')


def ar_spectrum(A, sigma, sample_rate, freq_vect):
    """
    Estimate the spectral representation of a set of MVAR coefficients as
    suggested by Baccala & Sameshima 2001, the equation without a number just
    below equation 13.

    :param A: TODO
    :param sigma: TODO
    :param sample_rate: TODO
    :param freq_vect: TODO

    :returns: TODO
    """

    # This routine assumes that our parameter matrix is of the form where
    # we have a leading positive.  Ensure that this is the case.
    A = ensure_leading_positive(A)

    if A.ndim == 3:
        A = A[..., None]

    # model order
    order = A.shape[2] - 1

    nsignals = A.shape[0]
    nepochs = A.shape[3]

    spectrum = np.zeros((nsignals, nsignals,
                         len(freq_vect), nepochs), dtype=complex)

    for node1 in range(nsignals):
        for node2 in range(nsignals):
            for e in range(nepochs):
                for idx, f in zip(list(range(len(freq_vect))), freq_vect):

                    # Normalised digital frequency
                    f = f / sample_rate

                    est = 0+0j

                    for k in range(1, order+1):
                        est -= A[node1, node2, k, e] * np.exp(0-1j*2*np.pi*k*f)

                    spectrum[node1, node2, idx, e] = est

    return spectrum


__all__.append('ar_spectrum')


def transfer_function(Af):
    """
    Function for computing the transfer function of a system

    :param Af: Frequency domain version of parameters (can be calculated
               using ar_spectrum function)
               [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    # Remove identity from Af
    Afi = np.repeat(np.eye(Af.shape[0])[:, :, None],
                    Af.shape[2], axis=-1)[..., None] - Af

    nchannels = Af.shape[0]
    nfreqs = Af.shape[2]
    nepochs = Af.shape[-1]

    tf = np.zeros((nchannels, nchannels,
                   nfreqs, nepochs), dtype=complex)

    for e in range(nepochs):
        for f in range(nfreqs):
            tf[:, :, f, e] = np.linalg.inv(Afi[:, :, f, e])

    return tf


__all__.append('transfer_function')


def spectral_matrix(H, noise_cov):
    """
    Function for computing the spectral matrix, the matrix of spectra and
    cross-spectra.

    :param H: The transfer matrix [nchannels x nchannels x nfreqs x nepochs]
    :param noise_cov: The noise covariance matrix of the system
                      [nchannels x nchannels x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    # Make sure that we have the 4th dimension
    if H.ndim < 4:
        H = H[:, :, :, None]

    S = np.zeros_like(H)

    for i in range(H.shape[2]):
        for j in range(H.shape[3]):
            S[:, :, i, j] = H[:, :, i, j].dot(
                noise_cov[:, :, j]).dot(H[:, :, i, j].T.conj())

    return S


__all__.append('spectral_matrix')


def psd_matrix(S, sample_rate):
    """
    Function for computing the power spectral density matrix with units matched
    to scipy.signal.welch(X, axis=1, scaling='spectrum')

    :param S: The spectral matrix [nchannels x nchannels x nfreqs x nepochs]
    :param sample_rate: The sampling rate of the system

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    return S / sample_rate


__all__.append('psd_matrix')


def inv_spectral_matrix(H, noise_cov):
    """
    Function for computing the inverse spectral matrix.

    :param H: The transfer matrix [nchannels x nchannels x nfreqs x nepochs]
    :param noise_cov: The noise covariance matrix of the system
                      [nchannels x nchannels x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    inv_S = np.zeros_like(H)

    S = spectral_matrix(H, noise_cov)

    for f in range(S.shape[2]):
        for e in range(S.shape[3]):
            inv_S[:, :, f, e] = np.linalg.pinv(np.abs(S[:, :, f, e]))

    return inv_S


__all__.append('inv_spectral_matrix')


def coherency(S):
    """
    Method for computing the Coherency.  This is the complex form of coherence,
    from which metrics such as magnitude squared coherence can be derived

    :params S: The spectral matrix: 3D or 4D
               [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    coh = np.zeros_like(S)

    for i in range(S.shape[0]):
        for j in range(S.shape[0]):
            coh[i, j, :, :] = S[i, j, :, :] / \
                (np.sqrt(np.abs(S[i, i, :, :] * S[j, j, :, :])))

    return coh


__all__.append('coherency')


def magnitude_squared_coherence(S):
    """
    Method for computing the Magnitude Squred Coherence.

    :params S: The spectral matrix: 3D or 4D
               [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    return np.power(np.abs(coherency(S)), 2)


__all__.append('magnitude_squared_coherence')


def imaginary_coherence(S):
    """
    Method for computing the imaginary coherence

    :params S: The spectral matrix: 3D or 4D
               [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    return coherency(S).imag


__all__.append('imaginary_coherence')


def phase_coherence(S):
    """
    Method for computing the phase coherence

    :params S: The spectral matrix: 3D or 4D
               [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    return np.angle(coherency(S))


__all__.append('phase_coherence')


def partial_coherence(inv_S):
    """
    Method for computing the Partial Coherence.

    :params inv_S: The inverse spectral matrix
                   [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    pcoh = np.zeros_like(inv_S)

    for i in range(inv_S.shape[0]):
        for j in range(inv_S.shape[0]):
            pcoh[i, j, :, :] = np.power(np.abs(inv_S[i, j, :, :]), 2) / \
                (inv_S[i, i, :, :] * inv_S[j, j, :, :])

    return pcoh


__all__.append('partial_coherence')


def ff_directed_transfer_function(H):
    """
    Function for computing the full-frequency directed transfer function.

    :param H: The transfer matrix [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    dtf = np.zeros_like(H)

    for e in range(H.shape[3]):
        for i in range(H.shape[0]):
            # Make the denominator for this channel over all frequencies
            dtf_denom = np.sum(np.power(np.abs(H[i, :, :, e]), 2))

            # Estimate ffDTF
            for f in range(H.shape[2]):
                for j in range(H.shape[0]):
                    dtf[i, j, f, e] = np.power(
                        np.abs(H[i, j, f, e]), 2) / dtf_denom

    return dtf


__all__.append('ff_directed_transfer_function')


def d_directed_transfer_function(H, inv_S):
    """
    Function for computing the direct directed transfer function.

    :param H: The transfer matrix [nchannels x nchannels x nfreqs x nepochs]

    :params inv_S: The inverse spectral matrix
                   [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    return partial_coherence(inv_S) * ff_directed_transfer_function(H)


__all__.append('d_directed_transfer_function')


def partial_directed_coherence(Af):
    """
    Function to estimate the partial directed coherence from a set of
    multivariate parameters.

    :param Af: Frequency domain version of parameters (can be calculated
               using ar_spectrum function)

    :returns: PDC : ndarray containing the PDC estimates from the parameters of
                    dimensions [nchannels x nchannels x order]
    """

    pdc = np.zeros_like(Af)

    # Remove identity from Af
    Afi = np.repeat(np.eye(Af.shape[0])[:, :, None],
                    Af.shape[2], axis=-1)[..., None] - Af

    for e in range(Afi.shape[3]):
        for j in range(Afi.shape[0]):
            for f in range(Afi.shape[2]):
                pdc_denom = np.sqrt(
                    (np.abs(Afi[:, j, f, e])**2).sum())
                for i in range(Afi.shape[0]):
                    pdc[i, j, f, e] = np.abs(
                        Afi[i, j, f, e]) / pdc_denom

    return pdc


__all__.append('partial_directed_coherence')


def isolated_effective_coherence(Af, noise_cov):
    """
    Function for estimating the Isolated Effective Coherence as defined in
    Pascual-Marqui et al 2014

    :param Af: Frequency domain version of parameters (can be calculated
               using ar_spectrum function)
               [nchannels x nchannels x nfreqs x nepochs]

    :param noise_cov: The noise covariance matrix of the system
                      [nchannels x nchannels x nepochs]

    :returns: iec: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]

    """

    # Remove identity from Af
    Afi = np.repeat(np.eye(Af.shape[0])[:, :, None],
                    Af.shape[2], axis=-1)[..., None] - Af

    nchannels = Afi.shape[0]
    nfreqs = Afi.shape[2]
    nepochs = Afi.shape[3]

    iec = np.zeros((nchannels, nchannels, nfreqs, nepochs), dtype=complex)

    for e in range(nepochs):
        # Get inverse of hte residual noise covariance and set off-diagonal
        # elements to zero
        S = noise_cov[..., e]  # S = np.linalg.inv(noise_cov[..., e])
        iso_s = np.linalg.inv(np.diag(np.diag(S)))

        for f in range(nfreqs):
            for i in range(nchannels):
                for j in range(nchannels):

                    iso_params = np.diag(np.diag(Afi[:, :, f, e]))
                    # Set all parameters except the diagonal and connection of
                    # interest to zero
                    iso_params[i, j] = Afi[i, j, f, e]

                    denom_col = iso_s[j, j] * np.abs(iso_params[j, j])**2

                    numerator = iso_s[i, i] * np.abs(iso_params[i, j])**2

                    iec[i, j, f, e] = numerator / (numerator + denom_col)

    return iec.real


__all__.append('isolated_effective_coherence')


def directed_transfer_function(H):
    """
    Method for computing the Directed Transfer Function as defined in
    Kaminski & Blinowska 1991

    :param H: The transfer matrix [nchannels x nchannels x nfreqs x nepochs]

    :returns: numpy array of dimensions
              [nsignals x nsignals x frequency x epochs]
    """

    dtf = np.zeros_like(H)

    for e in range(H.shape[3]):
        for i in range(H.shape[0]):
            for f in range(H.shape[2]):
                # Make the denominator for this channel
                dtf_denom = np.sum(np.power(np.abs(H[i, :, f, e]), 2))
                for j in range(H.shape[0]):
                    dtf[i, j, f, e] = np.power(
                        np.abs(H[i, j, f, e]), 2) / dtf_denom

    return dtf


__all__.append('directed_transfer_function')


def geweke_granger_causality(S, H, sigma):
    """
    :param S: Spectral matrix [nchannels x nchannels x nfreqs x nepochs]

    :param H: The transfer matrix [nchannels x nchannels x nfreqs x nepochs]

    :param sigma: TODO

    :returns: TODO [nsignals x nsignals x frequency x nepochs]

    http://dx.doi.org/10.1103/PhysRevE.81.041907

    https://journals.aps.org/pre/pdf/10.1103/PhysRevE.81.041907
    """

    nchannels = S.shape[0]
    nfreqs = S.shape[2]
    nepochs = S.shape[3]

    ggc = np.zeros((nchannels, nchannels, nfreqs, nepochs), dtype=complex)

    for e in range(nepochs):

        # Compute conditional sigma matrix
        cond_sigma = np.zeros((nchannels, nchannels))
        inv_sigma = np.linalg.inv(sigma[:, :, e])
        for ii in range(nchannels):
            for jj in range(nchannels):
                cond_sigma[ii, jj] = sigma[jj, jj, e] - \
                                sigma[ii, jj, e]*inv_sigma[ii, ii]*sigma[jj, ii, e]

        for f in range(nfreqs):
            for ii in range(nchannels):
                for jj in range(nchannels):

                    denom = H[ii, jj, f, e] * cond_sigma[ii, jj] * H[ii, jj, f, e].conj()
                    denom = np.abs(S[ii, ii, f, e] - denom)

                    ggc[ii, jj, f, e] = np.log(np.abs(S[ii, ii, f, e]) / denom)

    return ggc


__all__.append('geweke_granger_causality')
