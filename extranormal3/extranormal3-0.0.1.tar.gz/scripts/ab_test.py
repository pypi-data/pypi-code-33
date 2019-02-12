#!/usr/bin/env python3
#######################################

import sys
import os
import os.path
import time
#import re

import logging
# ------------------------ logging levels ------------------------------------
logging.basicConfig(level= logging.INFO,
                    format='%(module)s.%(funcName)s: %(levelname)-7s: %(message)s')  
config_log = logging.INFO
# ----------------------------------------------------------------------------

from optparse import OptionParser

import numpy
from scipy import optimize
import matplotlib.pyplot as plt

from extranormal3 import normal_xas

#---------- test -----------
E0 = 20003.9

PRE_EDGE_START = -200
PRE_EDGE_END = -60
PRE_FIT_DEGREE = 1


POST_EDGE_START = 100
POST_EDGE_END = 1200
POST_FIT_DEGREE = 2
#---------------------------

if __name__ == '__main__':
    
    parser = OptionParser()
    '''
    parser.add_option("-p", "--parallel", dest="parallel",
                      action="store_true", default=False,
                      help="parallel execution (using mpirun)")
    '''           
    (options, args) = parser.parse_args()
                  
    if len(args) == 0:  
        print ("Usage: "+ os.path.basename(__file__) +"  data_file")
        sys.exit()

    if not os.path.exists(args[0]):
        logging.error(" Data file "+ args[0] +" does not exist")
        sys.exit() 
    data_file = args[0]
    
    edge = E0
    preedge_params = {}
    preedge_params['from'] = edge + PRE_EDGE_START
    preedge_params['to'] = edge + PRE_EDGE_END
    preedge_params['deg'] = PRE_FIT_DEGREE
    
    postedge_params = {}
    postedge_params['from'] = edge + POST_EDGE_START
    postedge_params['to'] = edge + POST_EDGE_END
    postedge_params['deg'] = POST_FIT_DEGREE
    
    spectrum = numpy.loadtxt(data_file, comments = '#', usecols=(0,2), unpack=True )
    ref = numpy.loadtxt(data_file, comments = '#', usecols=(3,), unpack=True )
    
    fig, ax = plt.subplots()
    line1, = ax.plot(spectrum[0], spectrum[1], label='Measured spectrum')
    
    norm_vals = normal_xas.normalize(spectrum, edge, preedge_params, postedge_params)[0]
    
    '''
    print (norm_vals)
    print (norm_vals.shape)
    norm_const = normal_xas.normalize(spectrum, edge, preedge_params, postedge_params)[1]
    print (norm_const)
    print (numpy.array([norm_const]).shape)    
    print (numpy.concatenate((norm_vals, numpy.array([norm_const])), axis=0))
    '''
    
    
    line2, = ax.plot(spectrum[0], norm_vals, label='Normalized spectrum')
    
    ax.legend(loc='lower right')
    plt.grid()
    #plt.show() 
    
    norm_spectra, norm_consts = normal_xas.normalize_all(spectrum[0], [spectrum[1], ref], 
                                                  edge, preedge_params, postedge_params)
    print (norm_spectra.shape)
    #print (numpy.ones((len(norm_consts), 1)).shape ) 
    #print (numpy.hstack((norm_spectra, numpy.ones((len(norm_consts), 1)))) )
    norm_consts = norm_consts.reshape((len(norm_consts),1))
    print (norm_consts.shape)
    print (norm_consts)
    print (numpy.hstack((norm_spectra, norm_consts)) )
    
    
    #print (normal_xas.normalize_all(spectrum[0], [spectrum[1], ref], edge, preedge_params, postedge_params))
    
    #print (norm_params)
    