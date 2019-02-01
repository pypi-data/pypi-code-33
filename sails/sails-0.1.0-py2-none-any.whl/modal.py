#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import scipy
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

from sails.support import ensure_leading_negative
from sails.modelfit import coloured_noise_fit

__all__ = []


def adjust_phase(x):
    """
    Method for normalising eigenvector matrices to meet the conditions in
    eqn 21 of Neumaier & Schneider 2001.

    :param x: Vector of complex numbers to adjust the phase of
    :returns: Vector of numbers with adjusted phase
    """

    ox = np.zeros_like(x)

    # Rows of x
    for j in range(x.shape[0]):
        a = np.atleast_2d(np.real(x[j, :])).T
        b = np.atleast_2d(np.imag(x[j, :])).T
        tmp = np.dot(b.T, b) - np.dot(a.T, a)
        phi = .5 * np.arctan(2 * np.sum(a*b / tmp))
        bnorm = np.linalg.norm(np.sin(phi) * a + np.cos(phi) * b)
        anorm = np.linalg.norm(np.cos(phi) * a + np.sin(phi) * b)

        if bnorm > anorm:
            if phi < 0:
                phi = phi - (np.pi/2.)
            else:
                phi = phi + (np.pi/2.)

        ox[j, :] = x[j, :] * np.exp((0+1j) * phi)

    return ox


__all__.append('adjust_phase')


class MvarModalDecomposition(object):
    """
    Object which calculates the modal decomposition of a fitted model
    derived from the AbstractLinearModel class.
    """

    # This is only used when used within NAF
    hdf5_outputs = ['nsignals', 'order', 'companion', 'evals', 'evecsr',
                    'evecsl', 'decoupled_cov', 'abs_lambda_sq', 'excitation',
                    'modeinds', 'freq_vect', 'period', 'dampening_time',
                    'freq_vect_hz', 'peak_frequency', 'dampening_time_hz',
                    'freq_response', 'phase_response', 'pole_pairs', 'residue',
                    'freq_response_modal', 'phase_response_modal', 'nmodes',
                    'delay_vect']

    @classmethod
    def initialise(cls, model, sample_rate=None, normalise=False):
        """
        Compute the modal pole-residue decomposition of the A matrix from a
        fitted MVAR model.

        Currently only implemented for a single realisation (A.ndim == 3)

        :param model: Fitted model object.  Must be derived from
                      AbstractLinearModel.
        :param sample_rate: sample rate of system in Hz
        :param normalise: Whether to adjust the phase of the eigenvectors

        :returns: Modal decomposition object
        """

        # Create object
        ret = cls()

        A = model.parameters
        nsignals = ret.nsignals = A.shape[0]
        ret.order = A.shape[2] - 1
        nmodes = nsignals * ret.order

        if A.ndim == 4:
            pass
        else:
            # Add dummy epoch
            A = A[..., None]

        A = ensure_leading_negative(A)

        if model.resid_cov.ndim == 2:
            # Add a dummy epoch
            model.resid_cov = model.resid_cov[..., None]

        nrealisations = A.shape[3]

        # preallocate arrays
        ret.evals = np.zeros((nmodes, nrealisations), dtype=complex)
        ret.evecsr = np.zeros((nmodes, nmodes, nrealisations), dtype=complex)
        ret.evecsl = np.zeros((nmodes, nmodes, nrealisations), dtype=complex)

        ret.modeinds = np.zeros((nmodes, nrealisations), dtype=int)
        ret.pole_pairs = np.zeros_like(ret.evals, dtype=int) * np.nan

        for ii in range(nrealisations):

            # Generate companion form
            from .modelfit import A_to_companion
            ret.companion = A_to_companion(A[:, :, 1:, ii])

            # Roots are now the eigenvalues of the companion matrix
            ret.evals[:, ii], ret.evecsl[:, :, ii], ret.evecsr[:, :, ii] = \
                scipy.linalg.eig(ret.companion, left=True, right=True)

            # Apply normalisation from http://climate-dynamics.org/wp-content/uploads/2015/08/arfit.pdf
            if normalise:
                ret.evecsr[:, :, ii] = adjust_phase(ret.evecsr[:, :, ii].T).T

            # take left eigenvecs from right, might preserve scaling better
            ret.evecsl[:, :, ii] = np.linalg.inv(ret.evecsr[:, :, ii].conj().T)

            ret.modeinds[:, ii] = np.argsort(np.abs(ret.evals[:, ii]))[::-1]

            # Loop through poles with an imaginary part and find pairings, poles
            # with a zero imaginary part are left indexed as nan
            ppidx = 0
            for idx in range(len(ret.pole_pairs)):
                if ret.evals[idx].imag > 0:
                    # Find the conjugate pair
                    cidx = (abs(ret.evals[idx] - ret.evals.conj())).argmin()
                    ret.pole_pairs[idx] = ppidx
                    ret.pole_pairs[cidx] = ppidx
                    ppidx += 1

        # Compute the period and dampening time per mode
        # We ignore /0 warnings as they are expected for real modes
        old_warning = np.geterr()['divide']
        np.seterr(divide='ignore')
        ret.period = 2*np.pi / np.abs(np.angle(ret.evals))
        np.seterr(divide=old_warning)

        ret.dampening_time = -1.0 / np.log(np.abs(ret.evals))
        if sample_rate is not None:
            ret.peak_frequency = sample_rate / ret.period
            ret.dampening_time_hz = sample_rate / ret.dampening_time
        else:
            ret.peak_frequency = None
            ret.dampening_time_hz = None

        ret.nmodes = nmodes
        ret.delay_vect = model.delay_vect

        return ret

    @property
    def period_hz(self):
        """This is an old and deprecated way of accessing peak_frequency"""
        return self.peak_frequency

    def compute_residues(self):
        """
        Compute the residue matrix from the eigenvectors associated with each
        pole.
        """

        # Compute the residue matrices and frequency responses per mode
        residue = np.zeros((self.nsignals, self.nsignals, self.nmodes), dtype=complex)

        for imode in range(len(self.evals)):
            # Compute residue matrix from left and right eigenvectors
            l = np.atleast_2d(self.evecsl[:self.nsignals, imode]).conj()
            r = np.atleast_2d(self.evecsr[:self.nsignals, imode]).T
            residue[:, :, imode] = l.dot(r).T

        return residue

    def compute_modal_parameters(self):
        """
        Compute the order 1 or 2 autoregressive coefficients associated with
        each pole or conjugate pair.
        """

        # Compute the residue matrices and frequency responses per mode
        residue = self.compute_residues()

        A = np.zeros((self.nsignals, self.nsignals, 3, self.pole_pairs.max()+1))

        # Loop through nodes and connections
        for ii in np.arange(self.nsignals):
            for jj in np.arange(self.nsignals):
                # For each pole pair
                for kk in np.arange(self.pole_pairs.max()+1):
                    inds = self.pole_pairs[:, 0] == kk
                    b, a = signal.invresz(residue[ii, jj, inds].squeeze(),
                                          self.evals[inds, 0], [0])

                    # I'm scaling the ar coefficients by the leading numerator coeff.
                    # This scaling doesn't affect the roots (ie peak frequency) but
                    # will show up in the relative measures.
                    A[ii, jj, :len(a), kk] = a * b[0]

        return A

    def modal_freqz(self):
        """
        Compute filter characteristics for each pole
        """

        # Compute the frequency response for the whole system
        w, h = signal.freqz(1, self.evals)
        mag_response = np.abs(h)
        phase_response = np.unwrap(np.angle(h))

        return w, mag_response, phase_response

    def excitation(self, resid_cov):
        """
        http://climate-dynamics.org/wp-content/uploads/2015/08/arfit.pdf
        """

        # Compute the excitation per mode
        inv_evecsr = np.linalg.inv(self.evecsr)

        decoupled_cov = inv_evecsr[:, :self.nsignals].dot(resid_cov[:, :, 0])
        decoupled_cov = decoupled_cov.dot(inv_evecsr[:, :self.nsignals].conj().T)

        abs_lambda_sq = np.power(np.abs(self.evals), 2)

        excitation = (np.diag(decoupled_cov) / (1 - abs_lambda_sq)).real
        excitation = excitation / np.sum(excitation)

        return excitation

    def transfer_function(self, sample_rate, freq_vect, modes=None,
                          sum_modes=True):
        """
        Compute the transfer function in pole-residue form, splitting the
        system into modes with separate transfer functions. The full system
        transfer function is then a linear sum of each modal transfer function.

        :param sample_rate: sample rate of system in Hz
        :param freq_vect: Vector of frequencies at which to evaluate function
        :param modes: List of mode indices to evaluate over (optional)
        :param sum_modes: Boolean indicating whether to sum modes or return all
        """

        if (sample_rate is None and freq_vect is not None) or \
           (sample_rate is not None and freq_vect is None):
            raise ValueError('Please define both sample_rate and '
                             'freq_vect (or neither to return '
                             'normalised frequency 0->pi)')

        if freq_vect is None and sample_rate is None:
            # Use normalised frequency
            freq_vect_rads = np.linspace(0, np.pi, 512)
        else:
            # convert user defined frequecies to radians
            freq_vect_rads = (freq_vect / (sample_rate / 2.)) * np.pi

        # Allow us to pick out which modes we want
        if modes is None:
            modes = list(range(len(self.evals)))

        if sum_modes is False:
            nmodes = len(modes)
        else:
            nmodes = 1

        # Compute transfer function per mode
        residue = self.compute_residues()
        H = np.zeros((residue.shape[0],
                      residue.shape[0],
                      len(freq_vect_rads),
                      nmodes), dtype=complex)

        # Compute point on unit circle for each frequency
        z = np.cos(freq_vect_rads) + 1j*np.sin(freq_vect_rads)

        idx = 0

        for imode in modes:

            for ifreq in range(len(freq_vect_rads)):

                # Compute transfer function for this frequency and this mode
                num = residue[:, :, imode] * z[ifreq]
                dom = z[ifreq] - self.evals[imode]

                if sum_modes:
                    H[:, :, ifreq, 0] += num / dom
                else:
                    H[:, :, ifreq, idx] = num / dom

            idx += 1

        return H

    def per_mode_transfer_function(self, sample_rate, freq_vect):
        """
        Extracts the transfer function for each mode by summing the transfer
        function across pole-pairs where necessary

        :param sample_rate: sample rate of system in Hz
        :param freq_vect: Vector of frequencies at which to evaluate function
        """

        H = self.transfer_function(sample_rate, freq_vect)

        mi = self.mode_indices

        ret = np.zeros((len(freq_vect), len(mi)), dtype=complex)

        for idx, i in enumerate(mi):
            ret[:, idx] = np.sum(H[..., i], axis=3).squeeze()

        return ret

    def modal_transfer_function(self, sample_rate, modes=None):
        """
        Compute a transfer function matrix based on the excitation period for
        each mode

        :param sample_rate: sample rate of system in Hz
        :param modes: List of mode indices to evaluate over (optional)
        """

        # Allow us to pick out which modes we want
        if modes is None:
            modes = list(range(len(self.evals)))

        # Compute transfer function per mode
        H = np.zeros((self.residue.shape[0],
                      self.residue.shape[0],
                      len(modes)), dtype=complex)

        idx = 0

        for imode in modes:
            fv_rad = (self.peak_frequency[imode] / (sample_rate / 2.)) * np.pi

            # Compute point on unit circle for the relevant frequency
            z = np.cos(fv_rad) + 1j*np.sin(fv_rad)

            # Compute tranfer function for this frequency and this mode
            num = self.residue[:, :, imode] * z
            dom = z - self.evals[imode]
            H[:, :, idx] = num / dom

            idx += 1

        return H

    def get_mode_inds(self, fmin=0, fmax=None,
                      mag_thresh=0, resid_thresh=0,
                      index_mode='inclusive'):

        if fmax is None:
            fmax = self.freq_vect_hz[-1]/2

        if index_mode == 'inclusive':

            inds = (self.peak_frequency >= fmin) * (self.peak_frequency <= fmax)

            if mag_thresh is not None:
                inds = inds * (np.abs(self.evals) >= mag_thresh)

            if resid_thresh is not None:
                inds = inds * (np.abs(self.residue_norm[:, None]) >= resid_thresh)

        elif index_mode == 'exclusive':

            inds = (self.peak_frequency > fmin) * (self.peak_frequency < fmax)

            if mag_thresh is not None:
                inds = inds * (np.abs(self.evals) > mag_thresh)

            if resid_thresh is not None:
                inds = inds * (np.abs(self.residue_norm[:, None]) > resid_thresh)

        else:
            raise ValueError("index_mode {0} not recognised, please use"
                             "'inclusive' or 'exclusive'".format(index_mode))

        return np.where(inds)[0]

    # TODO: Validate this function
    def modal_timecourse(self, data):
        """
        Compute the modal time-course from a dataset and a fitted model. This
        is the tranformation of a set of [nsignals x time] data observations
        into modal coordinates of shape [nmodes x time].

        :param data: TODO
        """

        # Preallocate modal time-course array
        r = np.zeros((self.nmodes, data.shape[1], data.shape[2]))

        for idx in range(self.order, data.shape[1]):

            # Get modal time-course for this sample
            for iep in range(data.shape[2]):

                # Generate delay embedded data for this sample
                deldat = np.zeros((self.nsignals*(self.order-1),))
                for idelay in range(1, len(self.delay_vect)):
                    deldat[(idelay-1)*self.nsignals:idelay*self.nsignals] = \
                        data[:, idx-idelay, iep]
                    r[:, idx, iep] = self.companion.dot(deldat)

        return r

    @property
    def residue_norm(self):
        """
        TODO
        """
        nmodes = len(self.modeinds)
        residue = self.compute_residues()
        return np.linalg.norm(residue.reshape(-1, nmodes), axis=0)

    @property
    def mode_indices(self):
        """
        Returns a list of tuples of mode indices where each tuple contains the
        indices of either a pole-pair or an unpaired pole

        :return: list of tuples containing indices into the modes
        """
        modes = []
        handled_nodes = np.zeros_like(self.pole_pairs)
        for k in range(self.pole_pairs.shape[0]):
            # Deal with nodes we've already handled as conjugate pairs
            if handled_nodes[k] == 1:
                continue

            # Is this a real mode
            if np.isnan(self.pole_pairs[k]):
                # Single, real mode
                modes.append((k,))
                handled_nodes[k] = 1
            else:
                # Need to find pair index
                pidx = self.pole_pairs[k]

                indices = np.where(self.pole_pairs == pidx)[0]
                modes.append(tuple(indices))
                for idx in indices:
                    handled_nodes[idx] = 1

        return modes

    def pole_plot(self, ax=None, normscale=50, plottype='unitcircle'):
        """
        Plot the poles of the current system.

        :param ax: Optional axis on which to plot
        :param normscale: Scaling factor for points on plot
        :param plottyle: String defining which plot to make, can be 'unitcircle' or 'eigenspectrum'

        :return: Reference to axes on which plot was drawn
        """
        if ax is None:
            plt.figure()
            ax = plt.subplot(111)

        norm_factors = self.residue_norm / self.residue_norm.max()

        if plottype == 'unitcircle':

            x = np.cos(np.linspace(0, 2*np.pi, 128))
            y = np.sin(np.linspace(0, 2*np.pi, 128))
            plt.grid(True)

            ax.plot(x, y, 'k')

            ax.plot(.75*x, .75*y, 'k--', linewidth=.2)
            ax.plot(.5*x, .5*y, 'k--', linewidth=.2)
            ax.plot(.25*x, .25*y, 'k--', linewidth=.2)

            ax.plot(1.15*x[8:25], 1.15*y[8:25], 'k')
            ax.arrow(1.15*x[23], 1.15*y[23], x[24]-x[23], y[24]-y[23],
                     head_width=.05, color='k')

            handled_nodes = np.zeros_like(self.pole_pairs)

            plt.hold(True)

            for k in range(self.pole_pairs.shape[0]):
                # Deal with nodes we've already handled as conjugate pairs
                if handled_nodes[k] == 1:
                    continue

                # Need to find pair index
                pidx = self.pole_pairs[k]

                # Deal with real pole case
                if np.isnan(pidx):
                    indices = [k]
                else:
                    indices = np.where(self.pole_pairs == pidx)[0]

                # Stash the real and imaginary parts
                r = []
                i = []
                ms = None

                for idx in indices:
                    handled_nodes[idx] = 1

                    r.append(self.evals[idx].real)
                    i.append(self.evals[idx].imag)

                    # The scaling should be the same for the conjugate pair
                    if ms is None:
                        ms = norm_factors[idx]*normscale

                # Plot them all together to maintain the same colour
                # for each pair
                plt.plot(r, i, '+', ms=ms, markeredgewidth=2)

            ax.set_xlabel('Real')
            ax.set_ylabel('Imaginary')

            ax.set_ylim(-1.2, 1.2)
            ax.set_xlim(-1.2, 1.2)

            ax.annotate('Frequency', xy=(.56, 1.02))

        elif plottype == 'eigenspectrum':

            mags = np.abs(self.evals)
            mags = mags / (1-mags)

            if self.peak_frequency is None:
                x_vect = self.period
                xlabel = 'Period (samples)'
            else:
                x_vect = self.peak_frequency
                xlabel = 'Frequency (Hz)'

            yt = np.linspace(0, 1., 11)
            yt_scaled = yt / (1-yt)

            ax.scatter(x_vect, mags, c='k', marker='o', s=norm_factors*normscale)
            ax.set_yticks(yt_scaled[:-2])
            ax.set_yticklabels(yt[:-2])
            ax.grid(True)
            ax.set_xlabel(xlabel)
            ax.set_ylabel('Pole Magnitude')

        return ax


__all__.append('MvarModalDecomposition')


def find_noise_poles(modes, model, X, sample_rate, metric='diff', include_real_poles=True):

    coloured_noise, f_alphas = coloured_noise_fit(X, model.order)
    coloured_modes = MvarModalDecomposition.initialise(coloured_noise, sample_rate=sample_rate)

    from scipy import interpolate
    hz, I = np.unique(coloured_modes.peak_frequency[:, 0], return_index=True)
    pchip = interpolate.pchip(coloured_modes.peak_frequency[I, 0],
                              np.abs(coloured_modes.evals[I, 0]))

    I = np.argsort(modes.peak_frequency[:, 0])
    interp_poles = pchip(modes.peak_frequency[:, 0])
    orig_poles = np.abs(modes.evals[:, 0])

    if metric == 'diff':
        vals = (orig_poles-interp_poles)
    elif metric == 'diff_noisenorm':
        vals = (orig_poles-interp_poles) / interp_poles
    elif metric == 'diff_datanorm':
        vals = (orig_poles-interp_poles) / orig_poles
    elif metric == 'diff_sumnorm':
        vals = (orig_poles-interp_poles) / (orig_poles+interp_poles)

    thresh = 0
    if include_real_poles:
        good_modes = np.where(vals > thresh)[0]
    else:
        good_modes = np.where((vals > thresh) & (np.abs(modes.evals[:, 0].imag) > 1e-10))[0]
    bad_modes = np.setdiff1d(np.arange(modes.nmodes), good_modes)

    return good_modes, bad_modes, vals


def get_noise_thresh_gamma(modes, fmin, fmax):

    from scipy.stats import gamma

    x = np.linspace(0, 1, 1024)
    freq_centres = np.linspace(fmin, fmax, 64)
    thresh = np.zeros_like(freq_centres)

    for ii in range(len(freq_centres)):
        inds = modes.get_mode_inds(fmin=freq_centres[ii]-2,
                                   fmax=freq_centres[ii]+2)
        m = np.abs(modes.evals[inds])
        mle_tuple = gamma.fit(1-m, 1)
        rv1 = gamma.pdf(x=x, a=mle_tuple[0], loc=mle_tuple[1], scale=mle_tuple[2])
        thresh[ii] = 1-x[np.argmax(rv1)]

    from scipy import interpolate
    f = interpolate.interp1d(freq_centres, thresh, bounds_error=False)

    return freq_centres, thresh, f(modes.peak_frequency)


def cluster_modes(X, n_clusters, pca_dims):
    """
    X: array [vals,nmodes]
    """

    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans

    pc = PCA(n_components=pca_dims, whiten=True, copy=True).fit(X)
    km = KMeans(n_clusters=n_clusters)
    clusters = km.fit_predict(pc.components_.T)

    return clusters, km.inertia_


def get_cluster_average(clusters, vals):
    """
    clusters: int array [nmodes,] (cluster inds include zero)
    vals: array [...,nmodes]
    """

    out = np.zeros((vals.shape[:-1], clusters.max()+1))
    for c in range(clusters.max()+1):
        out[..., c] = vals[..., clusters == c].mean(axis=-1)

    return out
