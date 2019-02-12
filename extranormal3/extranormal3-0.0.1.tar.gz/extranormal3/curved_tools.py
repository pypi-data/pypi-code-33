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

from optparse import OptionParser

from math import factorial
import numpy
from scipy import optimize, interpolate, signal
#scipy.signal.savgol_filter(x, window_length, polyorder, deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0)[source]

from matplotlib import pylab

#####################


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
    return pylab.polyval(args, x)   
    
    
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

def dist(curve1, curve2):
    
    if all(curve1[0] == curve2[0]):
        dif = curve1[1]-curve2[1]
        return numpy.sqrt(numpy.dot(dif, dif))
    
    print ("Interpolation needed")      
    return 0

def ejump_app(y):
    
    max_val = max(y)
    argmax_inx = numpy.argmax(y)
    
    if argmax_inx == 0:
        return max_val
        
    min_val = min(y[:argmax_inx])
    
    return max_val - min_val
    

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



def grid_edge(energies, deriv_vals):
    
    deriv_argmax = numpy.argmax(deriv_vals) # - index
    edge_indx = deriv_argmax
    
    deriv2_vals = derivative_vals(numpy.array([energies, deriv_vals]))
    #numpy.savetxt('deriv2.dat', numpy.transpose(numpy.array([energies, deriv2_vals])), fmt = '%12.6g') # DEBUG
    
    deriv2_argmax = numpy.argmax(deriv2_vals[:deriv_argmax])
    logging.debug('deriv2_argmax = '+ str(energies[deriv2_argmax])) 
    
    deriv2_sign = numpy.sign(deriv2_vals[deriv2_argmax:deriv_argmax])
    # if deriv2 changes sign before deriv_argmax,
    # edge position is before deriv_argmax
    if (1 in deriv2_sign) and (-1 in deriv2_sign):
        logging.debug('Derivative curve has a double peak before going down to zero')
        
        deriv2_argmin = deriv2_argmax + numpy.argmin(deriv2_vals[deriv2_argmax:deriv_argmax])
        logging.debug('deriv2_argmin = '+ str(energies[deriv2_argmin])) 
        
        edge_indx = numpy.argmax(deriv_vals[:deriv2_argmin])
    
    # Position (in pixels) of the maximum of the derivative curve:
    edge_pos = energies[edge_indx] 
    
    return  edge_pos, edge_indx


"""
def get_edge(spectrum):
    '''
    return edge_pos and its index
    '''
    energies  = spectrum[0]  # notation
    
    # Derivative of the measured spectrum calculated "on 5 points" 
    # to filter noisy measures:
    deriv_vals = derivative_vals(spectrum)
    #numpy.savetxt('deriv.dat', numpy.transpose(deriv), fmt = '%12.6g') # DEBUG
    
    return grid_edge(energies, deriv_vals)
"""   


def curve_sampling(curve, res_threshold):

    if min(curve[0,1:] - curve[0,:-1])>= res_threshold:
        #print "No reference sampling needed" # DEBUG
        return curve

    #print "\nProceeding to the reference sampling " # DEBUG
    x_sampled = []
    y_sampled = []

    i = 0
    while i < len(curve[0]) -2:
        
        x_sampled.append(curve[0][i])
        y_sampled.append(curve[1][i])
        
        while curve[0,i+1] - curve[0,i] >= res_threshold and i < len(curve[0]) -2:
            
            x_sampled.append(curve[0][i+1])
            y_sampled.append(curve[1][i+1])
            i += 1
            
        last_accepted = i
        #print last_accepted # DEBUG
        #print curve[0][last_accepted] # DEBUG
            
        while curve[0,i+1] - curve[0,last_accepted] < res_threshold \
                  and i < len(curve[0]) -2:
            i += 1

        if i < len(curve[0]) -2:
            i += 1
            
    if curve[0, -1] - curve[0, last_accepted] >= res_threshold:
        x_sampled.append(curve[0][-1])
        y_sampled.append(curve[1][-1])
        
    sampled_curve = numpy.array([x_sampled,y_sampled] )

    #print "Reference sampling done\n" # DEBUG
    return sampled_curve

#signal.savgol_filter(x, window_length, polyorder, deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0)[source]

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



###############  fitting section #########    
sigmoid = lambda p, x: 2*p[2]/(1+numpy.exp(p[4]*(x-p[1])))

peak_shape = {
'asy_lorentzian': lambda p, x: p[3]+ 2*p[0]/(numpy.pi*sigmoid(p, x))/(1+4*(x-p[1])*(x-p[1])/(sigmoid(p, x)*sigmoid(p, x))),
'gaussian': lambda p, x: p[3]+ p[0]*numpy.exp(-(x-p[1])*(x-p[1])/(2*p[2]*p[2])), 
'lorentzian': lambda p, x: p[3]+ p[0]*p[2]/((x-p[1])*(x-p[1])+p[2]*p[2])
}


def fit_peak(x, y, init_sigma, shape_name='gaussian'):

    if init_sigma == 0.:
        print ('starting sigma = 0. is not accepted for peak fit')
        raise 'starting sigma = 0. is not accepted for peak fit'
        
    
    errfunc = lambda p, x, y: peak_shape[shape_name](p, x) - y 
        
    max_val = max(y)
    
    center = x[numpy.argmax(y)]
    logging.debug('center = '+ str(center))
    p0 = [max_val, center, init_sigma, 0., 0] # Initial guess 
    
    params, success = optimize.leastsq(errfunc, p0[:], args=(x, y))
    
    return params, success

# --------------------------------------------------
def shift_errfunc(p, curve, ref_piece):
    '''
    p = [shift_val]
    '''
    shift_val = p[0]    
    #shifted_curve = numpy.array(curve[0]+shift_val, curve[1])
    
    if curve[0][0]+shift_val > ref_piece[0][0] or curve[0][-1]+shift_val < ref_piece[0][-1]:
        raise ValueError ('ref x is supposed to be contained in the curve x bounds')
        
    shifted_interp = interpolate.interp1d(curve[0]+shift_val, curve[1])
    
    return numpy.abs(ref_piece[1]-shifted_interp(ref_piece[0]))
    

def shift2ref(curve, ref_piece, shift_firstguess=0.):
    
    if curve[0][0] > ref_piece[0][0] or curve[0][-1] < ref_piece[0][-1]:
        raise ValueError ('ref x is supposed to be contained in the curve x bounds')
        #return 0, 0
        
    p0 = [shift_firstguess]
    res = optimize.leastsq(shift_errfunc, p0, args=(curve, ref_piece))
    logging.debug(res)
    '''
    try:
        res = optimize.leastsq(shift_errfunc, p0, args=(curve, ref_piece))
    except:
        raise ValueError ('COUCOU')
    '''    
    shift_val = res[0][0]
    success = res[1]
    #fiterror = sum(res[2]['fvec']**2)
    #print fiterror    
    
    return shift_val, success
# ----------------------------------------------------
    
    
"""
def get_correction(spectrum, params):
    
    deriv_vals = derivative_3points(spectrum)
    edge_indx = numpy.argmax(deriv_vals) # - index   
    e_shift = spectrum[0][edge_indx] - E0
     
    '''
    print '------------ check E shift -------------'
    x = spectrum[0] - e_shift
    #y = spectrum[1]
    y = deriv_vals
    pylab.plot(x, y)
    pylab.grid(True)
    pylab.show()
    '''
    spectrum[0] = spectrum[0] - e_shift
    
    # pre-edge fit 
    start_ix, end_ix = spectrum[0].searchsorted([E0+params['pre_edge_start'], 
                                                 E0+params['pre_edge_end']])
    prefit = numpy.polyfit(spectrum[0][start_ix:end_ix],
                           spectrum[1][start_ix:end_ix], 
                           params['pre_fit_degree'])
    
    
    '''
    print '------------ check pre-edge fit -------------'
    x = spectrum[0]
    y = spectrum[1]
    z = numpy.polyval(prefit, spectrum[0])
    pylab.title('check pre-edge fit')
    pylab.plot(x, y)
    pylab.plot(x, z, label='Fit degree')
    pylab.grid(True)
    pylab.show()
    '''
    
    spectrum[1] = spectrum[1] - numpy.polyval(prefit, spectrum[0]) 
    
    # post-edge fit
    start_ix, end_ix = spectrum[0].searchsorted([E0+params['post_edge_start'], 
                                                 E0+params['post_edge_end']])
    postfit = numpy.polyfit(spectrum[0][start_ix:end_ix],
                            spectrum[1][start_ix:end_ix], params['post_fit_degree'])
    
    print '------------ check post-edge fit -------------'
    x = spectrum[0]
    y = spectrum[1]
    z = numpy.polyval(postfit, spectrum[0])
    pylab.title('check post-edge fit')
    pylab.plot(x, y)
    pylab.plot(x, z, label='Fit degree')
    pylab.grid(True)
    pylab.show()
    
    
    
    print '------------ check normalization -------------'
    x = spectrum[0]
    y = spectrum[1]/numpy.polyval(postfit, E0)
    pylab.title('check normalization')
    pylab.plot(x, y)
    pylab.grid(True)
    pylab.show()
    
    
    return prefit, postfit
"""
        
#############################
if __name__ == '__main__':
    """
    # --------------- test asymetric peak fit ------------
    #p = [1., 0., 1., 0., -1./5]
    #x = numpy.arange(-5, 5, 0.1)
    p = [  4.74422947e-01,   6.54229420e+03,   2.82975987e+00,   8.70039415e-03,  -6.43748392e-01]
    x = numpy.arange(6530, 6550, 0.1)
    #y = sigmoid(p, x)
    y = peak_shape['asy_lorentzian'](p, x)
    pylab.plot(x, y)
    pylab.grid(True)
    pylab.show()
    # ---------------------------------------------------
    """
    parser = OptionParser()
    parser.add_option("-c", "--column", dest="column",
                      type=int, default=2,
                      help="column nb (2 for measured spectrum, 3 for reference)")     
    parser.add_option("-d", "--distance", dest="distance",
                      action="store_true", default=False,
                      help="test distance calculation")                      
    parser.add_option("-j", "--ejump", dest="ejump",
                      action="store_true", default=False,
                      help="test approximate ejump calculation")
    parser.add_option("-s", "--ejump_stats", dest="ejump_stats",
                      action="store_true", default=False,
                      help="test approximate ejump stats")
                      
                      
    (options, args) = parser.parse_args()
    
    y_col = options.column
    
    if options.distance:
        print ('----------- Test intra-spectra distance calculation -----------')
        if len(args) < 2:  
            print ("Usage: "+ os.path.basename(__file__) +"  <multicolumn file1> <multicolumn file2>")
            sys.exit()
    
        if not os.path.exists(args[0]) or not os.path.exists(args[1]):
            print ("Invalid input files")
            sys.exit()
    
        try:
            curve1 = numpy.loadtxt(args[0], comments = '#',
                                   usecols=(0,y_col), unpack=True ) # as 2 colomns
            curve2 = numpy.loadtxt(args[1], comments = '#',
                                   usecols=(0,y_col), unpack=True )                                  
        except:
            print ("Check input files format (multi-column) and content")
            sys.exit()
            
        print ('Distance = ', dist(curve1, curve2))
        
        
    if options.ejump:
        print ('------------- Test approximate ejump calculation --------------')
        if len(args) == 0:  
            print ("Usage: "+ os.path.basename(__file__) +"  <multicolumn file>")
            sys.exit()
    
        if not os.path.exists(args[0]):
            print ("Invalid input files")
            sys.exit()
    
        try:
            curve = numpy.loadtxt(args[0], comments = '#',
                                  usecols=(0,y_col), unpack=True ) # as 2 colomns               
        except:
            print ("Check input file format (multi-column) and content")
            sys.exit()
            
        print ('ejump = ', ejump_app(curve[1]))
        
    """
    if options.ejump_stats:
        print '------------------ Test ejump stats---------------------------'
        #import utils
        '''
        NO INPUT SECURITY
        '''
        ejump_vals = []
        txt_list = [f for f in os.listdir(os.path.curdir) if f.endswith('.txt')]
        for f in txt_list:
            try:
                curve = numpy.loadtxt(f, comments = '#', usecols=(0,y_col), 
                                      unpack=True ) # as 2 colomns
            except:
                print "Invalid format or content: ", f
                continue
            ejump_vals.append(ejump_app(curve[1]))

        ejump_vals = numpy.array(ejump_vals)
        
        m = numpy.mean(ejump_vals)
        
        print 'min ejump =', min(ejump_vals)
        print 'mean ejump =', m
        print 'max ejump =', max(ejump_vals)
        
        print '\nmin dev =', min(numpy.abs(ejump_vals-m))
        print 'max dev =', max(numpy.abs(ejump_vals-m))
        print 'st dev =', numpy.std(ejump_vals)
        
        o_inds = [i for i in range(len(ejump_vals)) if abs(ejump_vals[i]-m)> 3*numpy.std(ejump_vals)]
        
        print 'outliers:', [txt_list[i] for i in o_inds]
        print 'ejump vals=', [ejump_vals[i] for i in o_inds]
    """
        
    '''                 
    if len(args) == 0:  
        print "Usage: "+ os.path.basename(__file__) +"  <config_file>"
        sys.exit()

    if not os.path.exists(args[0]):
        logging.error(" Config file "+ args[0] +" does not exist")
        sys.exit() 
    config_file = args[0]
    '''
    

    '''
    ref_curve = get_ref_curve(calib_config['ref_data'])
    if log_verb:     
        numpy.savetxt(os.path.join(output_path, 'ref_curve.dat'), 
                      numpy.transpose(ref_curve), fmt = '%12.6g')   
    '''         
 
    '''
    for dirname, dirnames, filenames in os.walk('.'):
    # http://stackoverflow.com/questions/120656/directory-listing-in-python
    
        second_spectrum = ([f for f in filenames if f.endswith('00010.txt')])[0]
        logging.debug('second spectrum = '+ second_spectrum)
        second_spectrum = numpy.loadtxt(second_spectrum, comments = '#',
                                        usecols=(0,2), unpack=True ) # as 2 colomns
        prefit, postfit = get_correction(second_spectrum, norm_params)        
        
        for filename in filenames:
            logging.debug(filename)
            spectrum = numpy.loadtxt(filename, comments = '#',
                                     usecols=(0,2), unpack=True ) # as 2 colomns

            deriv_vals = derivative_3points(spectrum)
            edge_indx = numpy.argmax(deriv_vals) # - index   
            e_shift = spectrum[0][edge_indx] - E0
            
            spectrum[0] = spectrum[0] - e_shift
            spectrum[1] = (spectrum[1]-numpy.polyval(prefit, spectrum[0]))/numpy.polyval(postfit, E0)
            
            
            # ------------ plot all normalized spectra -------------
            pylab.title('All spectra normalized')
            pylab.plot(spectrum[0], spectrum[1])
            
        pylab.grid(True)
        pylab.show()
    '''
    '''    
    params = {'axes.titlesize' : 9}
    pylab.rcParams.update(params)
    '''
    



