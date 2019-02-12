#!/usr/bin/env python3
#######################################

import sys
import os
import os.path

import logging
# ------------------------ logging levels ------------------------------------
logging.basicConfig(level= logging.DEBUG,
                    format='%(module)s.%(funcName)s: %(levelname)-7s: %(message)s')  
config_log = logging.INFO
# ----------------------------------------------------------------------------

import numpy
from scipy import  fftpack

from extranormal3 import curved_tools
#------------------------------------
dx=0.05
smoothfactor=7
#------------------------------------


def kaiser_window(x, x_min, x_max, tau, dx):
    
        pos  = int(numpy.round((x_min - x[0])/dx))
        logging.debug(' pos = '+str(pos))
        #print x[0], x_min
        lenx = int(numpy.round(x_max - x_min)/dx)
        logging.debug(' lenx = '+str(lenx))
        
        win  = numpy.zeros(len(x))
        win[pos : pos+lenx] = numpy.kaiser(lenx, tau)
        
        return win


def get_r_points(k_points):
    print ('coucou')
    return k_points
    
    
def la_fouriere(x, y, k_min, k_max, tau=2, smoothfactor=7, dx=0.05, kaiser=True):
    #def ft(chi,k1,k2,kw=1,tau=2,np=1024,kaiser=True)
    """
    - scipy based fourier transform 
    - usable on exafs data for forward fourier transform
    - tau is the tau of the kaiser window (called dk in Athena)
    - k_min and k_max are the limits of the window
      (When kaiser is not used a box window is used instead.)
    - return frequencies, imaginary part, real part and envelope
    """
    logging.debug(' la_fouriere function........')
    
    if len(x) != len(y):
        logging.error(' Invalid data length')
        raise Exception(' Invalid data length')
        
    x, y = curved_tools.equalstep_interp(x, y, dx)
    
    if kaiser:
        win  = kaiser_window(x, k_min, k_max, tau, dx)
    else:
        win = numpy.ones(len(x))
        win[(x < k_min) + (x > k_max)] = 0.

    # N = lenk number of samplepoints
    # T = dk sample spacing
    
    freqsx2 = len(x)*smoothfactor
    
    #y = numpy.array(y) * numpy.array(x)**kw * win    
    #yf = fftpack.fft(numpy.array(y) * numpy.array(x)**kw * win, freqsx2)
    yf = fftpack.fft(numpy.array(y)*win, freqsx2)
    
    #xf = numpy.linspace(0.0, 1.0/(2.0*dx), freqsx2)
    xf = numpy.fft.fftfreq(freqsx2, dx/numpy.pi)
    
    #return  xf,  yf
    
    lenx = len(xf)
    
    magnitudes = numpy.abs(yf[:lenx/2])
    
    return xf[:lenx/2], magnitudes
    
    
def fouriere4all(k_points, exafs_data, k_min, k_max, tau=2, kaiser=True):
    
    
    otvet = [la_fouriere(k_points, exafs_data[i], k_min, k_max, tau=2, 
                         smoothfactor=smoothfactor, dx=dx, kaiser=True)
             for i in range(len(exafs_data))]
                 
    return otvet
    
    fourier_matrix = []
    for i in range(len(exafs_data)):
        #try:
        if 1==1:            
            r, yf = la_fouriere(x, exafs_data[i], k_min, k_max, tau=tau,
                                smoothfactor=smoothfactor)
            lenr = len(r)
            ampli_yf = numpy.abs(yf[:lenr/2])

            if len(fourier_matrix)==0:
                fourier_matrix.append(r[:lenr/2])
            fourier_matrix.append(ampli_yf)

        ''' 
        except:
            print 'Unexpected format: file ', f
            sys.exit()
        '''
    

                      
                      
                     
    
    
    