"""
Signals, represented implicitly, with plotting and combinations.
"""
import pickle
import math
from cmax import util

from cmax.plotWindow import PlotWindow

# Unchanged from original distribution

# define size of graphing window 
# graphwidth = 400 # old value
graphwidth = 570
graphheight = 300

# NOTE: Ideally, graphwidth should be tuned to the number of samples in such a way
# that samples are an integer number of pixels apart on the screen.
# 570 seems to be just right for 250 samples (1000 steps and subsample 4).
# Samples are two pixels apart and there is space on the left for caption.
# Adjusting window width to get integer pixel spacing has now been
# automated in __init__ method of class GraphCanvas of gw.py

class Signal:
    """
    Represent infinite signals.  This is a generic superclass that
    provides some basic operations.  Every subclass must provide a
    C{sample} method.

    Be sure to start idle with the C{-n} flag, if you want to make
    plots of signals from inside idle.
    """
    
    def plot(self, start=0, end=100, plotWin=None, title='Signal value versus time'):
        samples = [self.sample(i) for i in range(start,end)]
        if plotWin is None:
            plotWin = PlotWindow(title)
        plotWin.stem(list(range(start,end)),samples)
        plotWin.axis([start,end,min(0,min(samples)),max(samples)])
        return plotWin

    def __add__(self, other):
        """
        @param other: C{Signal}
        @return: New signal that is the sum of C{self} and C{other}.
        
        Does not modify either argument.
        """
        return SummedSignal(self, other)
    
    def __rmul__(self, scalar):
        """
        @param scalar: number
        @return: New signal that is C{self} scaled by a constant.
        
        Does not modify C{self}
        """
        return ScaledSignal(self, scalar)

    def __mul__(self, scalar):
        """
        @param scalar: number
        @return: New signal that is C{self} scaled by a constant.
        
        Does not modify C{self}
        """
        return ScaledSignal(self, scalar)

    def period(self, n = None, z = None):
        """
        @param n: number of samples to use to estimate the period;  if
        not provided, it will look for a C{length} attribute of C{self}
        @param z: zero value to use when looking for zero-crossings of
        the signal;  will use the mean by default.
        @return: an estimate of the period of the signal, or
        'aperiodic' if it can't get a good estimate
        """
        if n == None:
            n = self.length
        crossingsD = self.crossings(n, z)
        if len(crossingsD) < 2:
            return 'aperiodic'
        else:
            return list_mean(gaps(crossingsD))*2

    def crossings(self, n = None, z = None):
        """
        @param n: number of samples to use;  if
        not provided, it will look for a C{length} attribute of C{self}
        @param z: zero value to use when looking for zero-crossings of
        the signal;  will use the mean by default.
        @return: a list of indices into the data where the signal crosses the
        z value, up through time n
        """
        if n == None: n = self.length
        if z == None: z = self.mean(n)
        samples = self.samples_in_range(0, n)
        return [i for i in range(n-1) if \
                   samples[i] > z and samples[i+1] < z or\
                   samples[i] < z and samples[i+1] > z]

    def mean(self, n = None):
        """
        @param n: number of samples to use to estimate the mean;  if
        not provided, it will look for a C{length} attribute of C{self}
        @return: sample mean of the values of the signal from 0 to n
        """
        if n == None: n = self.length
        return list_mean(self.samples_in_range(0, n))

    def samples_in_range(self, lo, hi):
        """
        @return: list of samples of this signal, from C{lo} to C{hi-1}
        """
        return [self.sample(i) for i in range(lo, hi)]    
    
#!

def gaps(data):
    """
    Return a list of the gap sizes, given a list of numbers.  (If input
    is length n, result is length n-1)
    """
    result = []
    for i in range(len(data)-1):
        result.append(data[i+1] - data[i])
    return result

def polyR(s, p):
    """
    @param s: C{Signal}
    @param p: C{poly.Polynomial}
    @return: New signal that is C{s} transformed by C{p} interpreted
    as a polynomial in I{R}.
    """
    # range(10, -1, -1) counts down from 10 to 0, inclusive
    return util.sum([c * Rn(s, k) \
                 for (c, k) in zip(p.coeffs, list(range(p.order, -1, -1)))])

def polyR(s, p):
    """
    @param s: C{Signal}
    @param p: C{poly.Polynomial}
    @return: New signal that is C{s} transformed by C{p} interpreted
    as a polynomial in I{R}.
    """
    # This implementation uses Horner's rule
    v = p.coeffs[0] * s
    for c in p.coeffs[1:]:
        v = R(v) + c * s
    return v
#!
class CosineSignal(Signal):
    """
    Primitive family of sinusoidal signals.
    """
    def __init__(self, omega = 1, phase = 0):
        """
        @parameter omega: frequency
        @parameter phase: phase in radians
        """
        self.omega = omega
        self.phase = phase
    def sample(self, n):
        return math.cos(self.omega * n + self.phase)
    def __str__(self):
        return 'CosineSignal(omega=%f,phase=%f)'%(self.omega, self.phase)

class UnitSampleSignal(Signal):
    """
    Primitive unit sample signal has value 1 at time 0 and value 0
    elsewhere.
    """
    def sample(self, n):
        if n == 0:
            return 1
        else:
            return 0
    def __str__(self):
        return 'UnitSampleSignal'

us = UnitSampleSignal()
"""Unit sample signal instance"""

class ConstantSignal(Signal):
    """
    Primitive constant sample signal.
    """
    def __init__(self, c):
        """
        param c: value of signal at all times
        """
        self.c = c
    def sample(self, n):
        return self.c
    def __str__(self):
        return 'ConstantSignal(%f)'%(self.c)
#!!
class SummedSignal(Signal):
    """
    Sum of two signals
    """
    def __init__(self, s1, s2):
        """
        @param s1: C{Signal}
        @param s2: C{Signal}
        """
        self.s1 = s1
        self.s2 = s2
    def sample(self, n):
        return self.s1.sample(n) + self.s2.sample(n)

class ScaledSignal(Signal):
    """
    Signal multiplied everywhere by a constant
    """
    def __init__(self, s, c):
        """
        @param s: C{Signal}
        @param c: number
        """
        self.s = s
        self.c = c
    def sample(self, n):
        return self.s.sample(n) * self.c

class R(Signal):
    """
    Signal delayed by one time step, so that C{R(S).sample(n+1) = S.sample(n)}
    """
    def __init__(self, s):
        """
        @param s: C{Signal}
        """
        self.s = s
    def sample(self, n):
        return self.s.sample(n-1)

class Rn(Signal):
    """
    Signal delayed by several time steps
    """
    def __init__(self, s, n):
        """
        @param s: C{Signal}
        @param n: integer specifying number of time steps to delay C{s}
        """
        self.s = s
        self.n = n
    def sample(self, n):
        return self.s.sample(n-self.n)

class FilteredSignal(Signal):
    """
    Signal filtered by a function, applied to a fixed-sized window of
    previous values
    """
    def __init__(self, s, f, w):
        """
        @param s: C{Signal}
        @param f: C{Procedure} maping C{w} numbers into a number
        @param w: positive integer
        """
        self.s = s
        self.f = f
        self.w = w
    def sample(self, n):
        return self.f([self.s.sample(n - i) for i in range(w)])

class StepSignal(Signal):
    """
    Signal that has value 1 for all n >= 0, and value 0 otherwise.
    """
    def sample(self, n):
        if n >= 0:
            return 1
        else:
            return 0

def mean_filtered(s, k):
    """
    @param s: C{Signal}
    @param k: positive integer filter size
    @return: C{s} filtered with a mean filter of size C{k}
    """
    return FilteredSignal(s, listMean, k)

def list_mean(vals):
    """
    @param vals: list of numbers
    @return: mean of C{vals}
    """
    return sum(vals)/float(len(vals))

def make_signal_from_pickle(pathName):
    """
    @param pathName: string specifying directory and file name
    @return: C{ListSignal} with data read in from C{pathname}.  That
    path must contain a pickled list of numbers.
    """
    f = open(pathName, 'r')
    data = pickle.load(f)
    f.close()
    print('Loaded signal with', len(data), 'points')
    return ListSignal(data)

# modified to return last valid sample if asked for sample beyond end
# and to return the first valid sample if asked for sample before start

class ListSignal(Signal):
    """
    Signal defined with a specific list of sample values, from 0 to some
    fixed length;  It has value 0 elsewhere.
    """
    def __init__(self, samples):
        """
        @param samples: list of numbers
        """
        self.samples = samples
        """The non-zero sample values of this signal (starting at index 0)"""
        self.length = len(samples)
        """The length of the explicitly-represented part of this signal"""
        
    def sample(self, n):
        if n < 0:
            n = 0
        elif n >= len(self.samples):
            n = len(self.samples)-1
        return self.samples[n]
    def __str__(self):
        return 'ListSignal([ %f, ...])'%self.samples[0]

# subsampled signal --- bkph
# extended to non-integer subsample using interpolation

cubicinterpolation=False
# cubicinterpolation=True # enable cubic interpolation

# def cubicinterpolation(dx, fm1, fp0, fp1, fp2):
#     dxm = dx-1
#     wm2 = - dxm * dxm * dx
#     wm1 = - wm2 - dxm
#     wp2 = dxm * dx * dx
#     wp1 = - wp2 + dx
#     return wm2*fm1 + wm1*fp0 + wp1*fp1 + wp2*fp2

class ListSignalSampled(Signal):
    """
    Signal defined with a specific list of sample values, from 0 to some
    fixed length;  It has the last value past the end and the
    first value before the start.
    """
    def __init__(self, samples, subsample):
        """
        @param samples: list of numbers
        """
        nlen = len(samples)
        if type(subsample) == type(0): # integer subsample case
            subsamples = [samples[k] for k in range(0,nlen,subsample)]
        else: # non-integer subsample case - bkph
            subsamples=[]
            nsublen = int(nlen/subsample)
            for i in range(0,nsublen):
                x = i * subsample
                k = int(x)
                dx = x - k
                if dx == 0:
                    val = samples[k]
                else:
                    if k+1 == nlen: # should not happen...
                        break;
                    if not cubicinterpolation or k == 0 or k == nlen-2:
                        val = (1-dx)*samples[k] + dx*samples[k+1] # linear
                    else: # use cubic interpolation - bkph
                        dxm = dx-1
                        wm2 = - dxm * dxm * dx
                        wm1 = - wm2 - dxm
                        wp2 =   dxm * dx * dx
                        wp1 = - wp2 + dx
                        val = wm2*samples[k-1]+wm1*samples[k]+\
                              wp1*samples[k+1]+wp2*samples[k+2]
                subsamples.append(val)

        self.samples = subsamples 
        """The non-zero sample values of this signal (starting at index 0)"""
        self.length = len(self.samples)
        """The length of the explicitly-represented part of this signal"""
        
    def sample(self, n):
        if n < 0:
            n = 0
        elif n >= len(self.samples):
           n = len(self.samples)-1
        return self.samples[n]
    def __str__(self):
        return 'ListSignal([ %f, ...])'%self.samples[0]
#!!
