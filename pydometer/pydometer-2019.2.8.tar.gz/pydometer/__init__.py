
"""This library provides several functions for converting acceleration data (g
in 3 axes) to step count.  Functions will return (step count, [step locations])."""

################################### Imports: ###################################

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from pydometer.filters import lpf

################################## Functions: ##################################

def steps_matlab_filtered(data, sr=None, filtering=True):
    """A very simple method; see "Counting Steps by Capturing Acceleration Data from
    Your Android Device" on mathworks.com.  filtering has been added as an option.
    """
    x, y, z = data.gx, data.gy, data.gz
    mag = np.sqrt(x**2 + y**2 + z**2)
    if filtering:
        mag = lpf(mag, sr)
    magNoG = mag - np.mean(mag)
    minPeakHeight = np.std(magNoG)
    pks, peak_props = find_peaks(magNoG, height=minPeakHeight)
    return len(pks), pks

def steps_matlab(data, sr=None):
    """The original method from the mathworks site (i.e. with no filtering)."""
    return steps_matlab_filtered(data, sr=sr, filtering=False)

#################################### Setup: ####################################

methods = {
    'matlab': steps_matlab,
    'best':   steps_matlab_filtered,
}

#################################### Class: ####################################

class Pedometer:
    def __init__(self, gx=None, gy=None, gz=None, sr=None, data=None):
        """The Pedometer can be initialized with a dataframe ('data') that has gx, gy,
        and gz columns.  otherwise, initialize with separate gx,gy,gz arrays.
        sr may be specified (Hz), or it will be computed from data.index if possible.
        """
        self.sr = None
        if data is not None:
            self.data = data
            if isinstance(data.index, pd.DatetimeIndex):
                secs_per_sample = (data.index[1]-data.index[0]).total_seconds()
                self.sr = 1.0/secs_per_sample
        elif gx is not None and gy is not None and gz is not None:
            self.data = pd.DataFrame([gx, gy, gz], columns=['gx','gy','gz'])
        else:
            raise ValueError("Must provide data, or gx/gy/gz.")
        if self.sr is None and sr is not None:
            self.sr = sr

    def get_steps(self, method='best'):
        """Get step count using using the specified method, which is one of the options
        in the methods dict.  Some methods will not work without sample rate (sr)."""
        return methods[method](self.data, self.sr)

################################################################################
