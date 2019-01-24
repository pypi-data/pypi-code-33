"""
Downsample input signal

MAGIC
@author: Roshni
"""
import scipy.signal as signal


def calculate(freq, strain, q):
    freq = signal.decimate(freq, q, ftype = 'fir', zero_phase = True)
    strain = signal.decimate(strain, q, ftype = 'fir', zero_phase = True)
    # Remove stray points from downsampling
    freq = freq[1:]
    strain = strain[1:]
    return freq, strain