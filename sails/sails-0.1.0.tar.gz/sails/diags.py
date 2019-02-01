#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import numpy as np

__all__ = []


class DelayDiagnostics(object):
    """
    Class which computes the mutual information as a function of lag from zero
    lag to the first zero crossing of the autocorrelation function.
    """

    # This is only used within NAF
    hdf5_outputs = ['MI', 'MI_diff', 'delay_vect_samples', 'delay_vect_ms',
                    'time_vect', 'autocorrelation', 'maxdelay', 'first_zero']

    def __init__(self):
        # TODO: Add docstrings for these
        self.MI = None

        self.MI_diff = None

        self.delay_vect_samples = None

        self.delay_vect_ms = None

        self.time_vect = None

        self.autocorrelation = None

        self.maxdelay = None

        self.first_zero = None

    @classmethod
    def delay_search(cls, data, maxdelay, step, sample_rate,
                     constant_window=True):
        """
        Compute MI as a function of lag from zero lag to the first zero
        crossing of the autocorrelation function

        If NafOptions().verbose is True, progress will be reported to stdout.

        :param data: array of [signals, samples, trials]
        :type data: numpy.ndarray

        :param maxdelay: maximum delay to consider
        :type maxdelay: int

        :param step: step to increment the delay by
        :type step: int

        :param sample_rate: sample rate of data
        :type sample_rate: float

        :param constant_window: Flag indicating that the same number of
                                datapoints should be included at each delay.
                                Default is True
        :type constant_window: bool
        """

        ret = cls()

        # Set up input parameters
        sample_rate = float(sample_rate)
        ret.maxdelay = maxdelay
        ret.time_vect = np.arange(data.shape[1]) * (1 / sample_rate)
        ret.delay_vect_samples = np.arange(1, ret.maxdelay)
        ret.delay_vect_ms = ret.delay_vect_samples * (1/sample_rate)

        # TODO: Check that we're not out of range of number of samples
        nsignals = data.shape[0]
        nsamples = data.shape[1]
        ntrials = data.shape[2]

        # Compute Autocorrelation
        # printv("Computing Autocorrelations")
        ac = np.zeros((nsignals, ntrials, nsamples), dtype=complex)

        for i in range(nsignals):
            for j in range(ntrials):
                ac[i, j, :] = np.correlate(data[i, :, j], data[i, :, j],
                                           'full')[nsamples-1:]

        ret.autocorrelation = ac

        # Find first zero crossing
        avg = ret.autocorrelation.mean(axis=0).mean(axis=0)
        zero_crossings = np.where(np.diff(np.sign(avg)))[0]

        ret.first_zero = zero_crossings[0]

        # printv("First zero crossing at %s samples %s ms" % (ret.first_zero,
        #                                     ret.time_vect[ret.first_zero]*1000))

        # Compute Mutual Information

        # TODO: Convert this to use stats.mutual_information
        nbins = 21
        bins = np.linspace(-8, 8, nbins)

        ret.MI = np.zeros((nsignals,
                           ret.delay_vect_samples.shape[0]),
                          dtype='float64')

        for d in range(ret.delay_vect_samples.shape[0]):

            delay = ret.delay_vect_samples[d]

            idx = nsamples - delay

            # Calculate MI for each signal, for each trial
            for s in range(nsignals):
                for t in range(ntrials):
                    if constant_window:
                        A = data[s, :-ret.maxdelay, t]
                        B = data[s, delay:-ret.maxdelay+delay, t]
                    else:
                        A = data[s, :-(delay), t]
                        B = data[s, delay:, t]

                    Ps = np.histogram(A, bins=bins)[0]
                    Pst = np.histogram(B, bins=bins)[0]
                    Ps_st = np.histogram2d(A, B, bins=bins)[0]

                    Ps = Ps / float(idx)
                    Pst = Pst / float(idx)
                    Ps_st = Ps_st / float(idx)

                    for i in range(nbins-1):
                        for j in range(nbins-1):
                            if Ps_st[i, j] != 0.0:
                                ret.MI[s, d] += Ps_st[i, j] * \
                                    np.log2(Ps_st[i, j] / (Ps[i] * Pst[j]))

        ret.MI = ret.MI / float(ntrials)

        ret.MI_diff = np.diff(ret.MI)

        # self.MI_dim_selection = model.find_elbow(self.MI)

        return ret


__all__.append('DelayDiagnostics')


class ModelDiagnostics(object):
    """
    TODO: Description
    """

    # This is only used within NAF
    hdf5_outputs = ['R_square', 'SR', 'DW', 'PC', 'AIC', 'BIC', 'LL', 'SI']

    def __init__(self):
        # TODO: Add docstrings for these
        self.R_square = None

        self.SR = None

        self.DW = None

        self.PC = None

        self.AIC = None

        self.BIC = None

        self.LL = None

        self.SI = None

    def __str__(self):
        """Show the measures in a pre-formatted manner"""
        template = "{0:^10}{1:^10}{2:^10}{3:^10}{4:^10}{5:^10}"

        return template.format(np.round(self.SI, 3),
                               np.round(self.SR, 3),
                               np.round(self.DW, 3),
                               np.round(self.AIC, 3),
                               np.round(self.BIC, 3),
                               np.round(self.R_square.mean(), 3))


__all__.append('ModelDiagnostics')
