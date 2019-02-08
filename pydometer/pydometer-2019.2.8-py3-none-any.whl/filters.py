
import numpy as np
from scipy.signal import firwin, lfilter, butter, filtfilt

def lpf(data, sr, cutoff=5.0, order=5):
    """Low pass filter some data."""
    # TODO: optimize order and cutoff.
    nyq = 0.5 * sr
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)
    #return lfilter(b, a, data)  # shifted
 
# def bpf(ampl, time, sr, start, end, f1=0.5, f2=40.0):
#     """Bandpass filter a signal. f1 and f2 are lower and upper bounds in Hz. start
#     and end are indices into lead.time and lead.ampl.  The filtered signal
#     (time, ampl) for the specified start:end range is returned.
#     """
#     nyq_rate = 0.5 * sr
#     numtaps = 20  # TODO
#     h = firwin(numtaps, [f1, f2], pass_zero=False, nyq=nyq_rate)
#     filtered_signal = lfilter(h, 1.0, ampl[start:end])
#     return time[start:end-int(numtaps/2)], filtered_signal[int(numtaps/2):]
