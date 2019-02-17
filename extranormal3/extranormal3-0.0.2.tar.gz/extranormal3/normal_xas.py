#!/usr/bin/env python3
#######################################

import sys
import os
import os.path

import logging
# ------------------------ logging levels ------------------------------------
logging.basicConfig(level= logging.INFO,
                    format='%(module)s.%(funcName)s: %(levelname)-7s: %(message)s')  
config_log = logging.INFO
# ----------------------------------------------------------------------------

import numpy

from extranormal3 import curved_tools

class InvalidInput(Exception): pass:
    
    
def process_params(energies, edge, preedge_params, postedge_params):
    
    if not (energies[0] < edge and edge < energies[-1]):
        sys.tracebacklimit = -1
        raise Exception('Edge value does not belong to the data energy range')
    
    if preedge_params['from']<0 and preedge_params['to']<0:
        # relative pre-edge fit bounds 
        preedge_params['from'] += edge
        preedge_params['to'] += edge
        postedge_params['from'] += edge
        postedge_params['to'] += edge
        
    if preedge_params['from'] < energies[0]:
        preedge_params['from'] = energies[0]
        
    if postedge_params['to'] > energies[-1]:
        postedge_params['to'] = energies[-1]
        
        

def flatten(spectrum, edge, preedge_fit, postedge_fit):
        '''
        spectrum is supposed to be shifted to the edge by now
        preedge_fit = self.preedge_params['fit_func'] from normal_gui.NormalWindow
        postedge_fit = self.postedge_params['fit_func'] from normal_gui.NormalWindow
        '''
        flattening_params = list(postedge_fit)[:-1]+[0.]
        flattening_params[-2] -= preedge_fit[-2]
        #print flattening_params
        
        beforeE0_inxs, = numpy.where(spectrum[0] < edge)
        afterE0_inxs, = numpy.where(spectrum[0] >= edge)
        
        flattening = numpy.zeros(len(spectrum[0]))            
        flattening[afterE0_inxs] = numpy.polyval(flattening_params, 
                                                 spectrum[0][afterE0_inxs])
        flattening[afterE0_inxs] = (flattening[afterE0_inxs] - 
                                    numpy.polyval(flattening_params, edge))
        return flattening            


def normalize(spectrum, edge, preedge_params, postedge_params, checked_params=False):
    
    if not checked_params:
        process_params(spectrum[0], edge, preedge_params, postedge_params)
    
    try:
        preedge_fitcurve,  preedge_fitcoeffs = curved_tools.poly_fit(spectrum, preedge_params)
        postedge_fitcurve,  postedge_fitcoeffs = curved_tools.poly_fit(spectrum, postedge_params)
    except:
        #sys.tracebacklimit = -1
        raise Exception('Invalid fit parameters')
    
    # http://cars9.uchicago.edu/~ravel/software/doc/Athena/html/bkg/norm.html
    norm_const = (numpy.polyval(postedge_fitcoeffs, edge)-
                  numpy.polyval(preedge_fitcoeffs, edge))
    
    flattening = flatten(spectrum, edge, preedge_fitcoeffs, postedge_fitcoeffs)    
    
    #return numpy.array([spectrum[0], (spectrum[1]-preedge_fitcurve[1]-flattening)/norm_const])
    return numpy.array((spectrum[1]-preedge_fitcurve[1]-flattening)/norm_const), norm_const

    
def normalize_all(energies, abs_data, edge, preedge_params, postedge_params):
    '''
    *** This function is only applicable to the interpolated data ***
    
    '''
    #print(energies, abs_data)
    if any([len(energies) != len(vals) for vals in abs_data]):
        sys.tracebacklimit = -1
        raise InvalidInput(' Invalid data format')
        #raise Exception(' Invalid data format')
    
    try:
        process_params(energies, edge, preedge_params, postedge_params)
    except:
        sys.tracebacklimit = -1
        raise InvalidInput('Invalid or inconsistent normalization parameters')
        
    '''        
    otvet = numpy.asarray([normalize(numpy.array([energies, abs_vals]), edge, preedge_params, postedge_params) 
            for abs_vals in abs_data])
    '''           
    otvet = [normalize(numpy.array([energies, abs_vals]), edge, preedge_params, postedge_params)
            for abs_vals in abs_data]
                
    norm_spectra_list = []
    norm_consts_list = []
    for tuple_instance in otvet:
        norm_spectra_list.append(tuple_instance[0])
        norm_consts_list.append(tuple_instance[1])
        
    norm_spectra = numpy.array(norm_spectra_list)
    norm_consts = numpy.array(norm_consts_list)
    
    return norm_spectra, norm_consts
    
    '''
    return numpy.array([normalize(numpy.array([energies, abs_vals]), 
                                  edge, preedge_params, postedge_params, 
                                  True)
                        for abs_vals in abs_data])
    '''           
    
    
    