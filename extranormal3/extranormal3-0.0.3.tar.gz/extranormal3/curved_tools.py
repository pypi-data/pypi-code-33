#!/usr/bin/env python
#######################################

import sys
import os
import os.path
import time
#import re

import logging
# ------------------------ logging levels ------------------------------------
logging.basicConfig(level= logging.DEBUG,
                    format='%(module)s.%(funcName)s: %(levelname)-7s: %(message)s')  
config_log = logging.INFO
# ----------------------------------------------------------------------------

#from optparse import OptionParser

from math import factorial
import numpy
from scipy import interpolate #optimize, signal
#scipy.signal.savgol_filter(x, window_length, polyorder, deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0)[source]

#from matplotlib import pylab



# ----------------------- updated funcs --------------------
def poly_fit(spectrum, user_params):
    start_ix, end_ix = spectrum[0].searchsorted([user_params['from'], 
                                                user_params['to']])
    if  end_ix <= start_ix:
        print (start_ix, end_ix)
        sys.tracebacklimit = -1
        raise Exception('Invalid energy bounds for fit')
                                   
    fit_coeffs = numpy.polyfit(spectrum[0][start_ix:end_ix], 
                               spectrum[1][start_ix:end_ix], 
                               user_params['deg'])
                           
    return numpy.array([spectrum[0], numpy.polyval(fit_coeffs, spectrum[0])]), fit_coeffs


def centered_polynomial(x, *args):
    
    # tupo
    res = []
    for i in range(len(x)):
        res.append(numpy.dot(numpy.array([x[i]**(n+1) for n in range(len(args))]), args))
        
    return numpy.array(res)

def poly_calc(x, *args):
    #return pylab.polyval(args, x)   
    return numpy.polyval(args, x)   
    
def equalstep_interp(x, y, step):
    '''
    ddk=numpy.diff(x)            
    #print 'init steps:' + str(ddk)  # debug
    
    if not(numpy.allclose(ddk[0],ddk)):
    '''
    if 1==1:
        
        logging.debug(' x[0]= '+ str(x[0]) +', x[-1]= '+ str(x[-1]) +'; '+ 
                      str(len(x)) + ' points')

        lin_y = interpolate.interp1d(x, y, 'linear', bounds_error=False, fill_value=0.)
        x = numpy.arange(x[0], x[-1] + step, step)
        y = lin_y(x)
        
        logging.debug('interp_x[0]= '+ str(x[0]) +', interp_x[-1]= '+ str(x[-1]) +'; '+ 
                      str(len(x)) + ' points')
        
    return x, y      

# -------------------- funcs on stand by -------------------

def derivative_3points(curve):

    f_diffs = curve[1,2:] - curve[1, :-2]
    f_diffs = numpy.concatenate(([curve[1,1] - curve[1,0]],
                             f_diffs,
                             [curve[1,-1] - curve[1,-2]]))
    
    x_diffs = curve[0,2:] - curve[0,:-2]
    x_diffs = numpy.concatenate( ([curve[0,1] - curve[0,0]],
                              x_diffs,
                              [curve[0,-1] - curve[0,-2]]) )

    return f_diffs/x_diffs
    
    
def derivative_5points(curve):

    f_diffs = curve[1,4:] - curve[1, :-4]
    f_diffs = numpy.concatenate(([curve[1,1] - curve[1,0]],
                             [curve[1,2] - curve[1,0]],
                             f_diffs,
                             [curve[1,-1] - curve[1,-3]],
                             [curve[1,-1] - curve[1,-2]]))
    
    x_diffs = curve[0,4:] - curve[0,:-4]
    x_diffs = numpy.concatenate( ([curve[0,1] - curve[0,0]],
                              [curve[0,2] - curve[0,0]],
                              x_diffs,
                              [curve[0,-1] - curve[0,-3]],
                              [curve[0,-1] - curve[0,-2]]) )

    return f_diffs/x_diffs


def derivative_vals(curve, points_nb=5):

    if points_nb == 5:
        return derivative_5points(curve)
    else:
        return derivative_3points(curve)
        

def max_deriv_pos(spectrum, deriv_over=3):
    '''
    deriv_over how many points: 3 or 5 are available
    '''
    if deriv_over == 5:
        deriv_vals = derivative_5points(spectrum)
    else:
        deriv_vals = derivative_3points(spectrum)
        
    edge_indx = numpy.argmax(deriv_vals) # - index  
    
    return spectrum[0][edge_indx]


#http://stackoverflow.com/questions/22988882/how-to-smooth-a-curve-in-python
def savitzky_golay(y, window_size, order, deriv=0, rate=1):

    import numpy as np

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
        
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    #print b
    #print m
    
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    
    y = np.concatenate((firstvals, y, lastvals))
    
    return np.convolve( m[::-1], y, mode='valid')


