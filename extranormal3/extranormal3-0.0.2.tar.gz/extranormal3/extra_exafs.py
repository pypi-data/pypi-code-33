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
from scipy import optimize, interpolate

from extranormal3 import curved_tools

#------------
K_step = 0.05
K_max_margin = 1
#------------

def get_idx_bounds(ene, sample_edge, ek_start, ek_end):
    
    E_bounds = True    
    
    if E_bounds:
        logging.debug('Emin = '+ str(ek_start) +', Emax = '+ str(ek_end))
        
        rel_Ebounds = True if sample_edge > ek_start else False        
        logging.debug('In get_idx_bounds: ABSOLUTE values for energy bounds are given')
        '''
        if not rel_Ebounds:  # get them relative
            e_start = e_start - edge
            e_end = e_end - edge
            rel_Ebounds = True
        '''
        if rel_Ebounds:
            start_idx = min(ene.searchsorted(sample_edge + ek_start), len(ene)-10)
            end_idx = min(ene.searchsorted(sample_edge + ek_end), len(ene)-1)
        else: 
            start_idx = min(ene.searchsorted(ek_start), len(ene)-10)
            end_idx = min(ene.searchsorted(ek_end), len(ene)-1)
        
        logging.debug(' Idx bounds: '+ str(start_idx) +' and '+ str(end_idx))
        
    else:  # k2energy
        logging.debug(' K bounds given: '+ str(ek_start) +', '+ str(ek_end))
        
        e_start = ek_start**2/0.2625
        e_end = ek_end**2/0.2625            
        logging.debug(" E bounds: "+ str(e_start) +', '+ str(e_end))
        
        start_idx = ene.searchsorted(sample_edge + e_start)
        if ene[start_idx]- (sample_edge + e_start) > (sample_edge + e_start) - ene[start_idx-1]:
            start_idx -= 1
        
        end_idx = min(ene.searchsorted(sample_edge + e_end), len(ene)-1)            
        logging.debug(' Idx bounds: '+ str(start_idx) +' and '+ str(end_idx))
        
    return start_idx, end_idx
    

def get_K_points(ene, sample_edge, start_idx, end_idx):
    '''
    should be called just ones
    '''
    if ene[start_idx] < sample_edge:
        raise Exception(' Invalid index when converting E to K')
    
    E_points = ene[start_idx:end_idx]
    K_points = numpy.sqrt(0.2625 * (E_points-sample_edge))
    nb_points = int((K_points[-1] - K_points[0])/K_step)
    K_interp = numpy.array([K_points[0] + K_step*i for i in range(nb_points)])
    
    return K_interp, K_points


def polynomial(k_points, mu_in_bounds, k_interp, I_jump, poly_deg, kweight, 
               plot=False):
    
    if I_jump == 0.:
        raise Exception(' Intensity jump at edge cannot aqual to zero')
        
    mu_calc = interpolate.interp1d(k_points, mu_in_bounds, 'linear', bounds_error=False, fill_value=0.)
    mu_interp = mu_calc(k_interp)
    
    '''
    fit_sigma = [k_interp[-1]**kweight for i in range(20)]
    fit_sigma = fit_sigma + [1./k_interp[i]**kweight for i in range(20, len(k_interp))]
    '''
    bkg_polynomial = optimize.curve_fit(curved_tools.poly_calc, k_interp, mu_interp, 
                                        [1.,]*poly_deg+[mu_interp[0]], 
                                        sigma=1./k_interp**kweight
                                        #sigma=fit_sigma
                                        )[0]
                                        
    bkg = numpy.polyval(bkg_polynomial, k_interp)
    
    if plot:
        import pylab
        pylab.plot(k_interp, bkg)
        
    chi_vals = (mu_interp - bkg)/I_jump
    
    return chi_vals, bkg
        
                    
#class NoJunpsEx(Exception): pass
    
def extract_all(energies, abs_data, edge, I_jumps, e_start, e_end,
                poly_deg, kweight, m):
    '''
    *** This function is applicable to the interpolated data ***
    
    data : data[0] = energies, data[1:] = absorbance columns
    '''
    if any([len(energies) != len(vals) for vals in abs_data]):
        raise Exception(' Invalid data format')
            
    if len(I_jumps) != len(abs_data):
        raise Exception(' Invalid data format or inconsistent meta data')
        #raise NoJunpsEx(' Invalid data format or inconsistent meta data')
        
    '''
    rel_Ebounds = True if edge > e_start else False
        
    if not rel_Ebounds:  # get them relative
        e_start = e_start - edge
        e_end = e_end - edge
        rel_Ebounds = True
    '''
    
    #  e_start, e_end are for the moment ABSOLUTE (not relative to Edge)
    start_idx, end_idx = get_idx_bounds(energies, edge, e_start, e_end)  
    
    k_interp, k_points = get_K_points(energies, edge, start_idx, end_idx) 
    logging.debug(' Kmin = '+ str(k_points[0]) +',  Kmax = '+ str(k_points[-1]))
    
    '''
    end_idx = min(energies.searchsorted(edge + e_end), len(energies)-1)
    kmax_extra = numpy.sqrt(0.2625 * (energies[end_idx] - edge))
    '''
    kmax_extra = k_points[-1]
    
    if poly_deg <= 0:
        poly_deg = min(9, int(numpy.round(kmax_extra/2.)))
        print ('Auto defined poly_deg = '+ str(poly_deg))
    
    if kweight <= 0:
        if kmax_extra >=16:
            kweight = 3
        elif 12 < kmax_extra < 16:
            kweight = 2
        elif kmax_extra < 12:
            kweight =1
        print ('Auto defined kweight = '+ str(kweight))
        
    otvet = [polynomial(k_points, abs_data[i][start_idx: end_idx], k_interp, I_jumps[i], poly_deg, kweight)
             for i in range(len(abs_data))]
    
    exafs_list = []
    Km_exafs_list = []
    bkgr_list = []
    for tuple_instance in otvet:
        exafs_list.append(tuple_instance[0])
        Km_exafs_list.append((k_interp**m)*tuple_instance[0])
        bkgr_list.append(tuple_instance[1])

    exafs = numpy.array(exafs_list)
    Km_exafs= numpy.array(Km_exafs_list)
    bkgr = numpy.array(bkgr_list)
        
    return Km_exafs, exafs, bkgr
    
    
    