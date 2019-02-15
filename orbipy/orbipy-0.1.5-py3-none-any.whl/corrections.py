# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 12:22:48 2018

@author: stasb
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brent, bisect

from .models import base_model
from .events import event_detector
from .directions import base_direction

class base_correction:
    '''
    Base interface class for all methods that calculate
    delta-V (correction impulse) for elimination of unstable component of
    motion in the vicinity of unstable Lagrange points.
    '''
    
    def __init__(self, model, direction):
        if not isinstance(model, base_model):
            raise TypeError('model should be an instance of base_model')
        self.model = model
        if not isinstance(direction, base_direction):
            raise TypeError('direction should be an instance of base_direction')
        self.direction = direction
        
    def calc_dv(self, t, s):
        pass

class border_correction(base_correction):
    '''
    Calculates delta-V using left and right borders.
    For example, borders are two planes orthogonal to x axis: one located 
    to the left of unstable point and one - to the right.
    See S.A. Aksenov, S.A. Bober "Calculation and Study of Limited Orbits
    around the L2 Libration Point of the Sun–Earth System". Cosmic Research, 
    2018, Vol. 56, No. 2, pp. 144–150.
    '''
    error_borders_unreachable = "Borders unreachable"
    error_before_unreachable = "Cant't reach event(s) before borders"
    error_max_iterations_reached = "Maximum iterations number reached"
    error_root_separation = "Can't separate discontinuity point"
    
    def __init__(self, model, direction,
                 left, right, before=[],
                 iterations=(20,100), maxt=10*np.pi,
                 dv0 = 1e-12,
                 tol=1e-16):
        '''
        Constructor
        '''
        super().__init__(model, direction)
        self.before = before
        if type(self.before) not in (list, tuple):
            self.before = (self.before,)
        self.left = left
        if type(self.left) not in (list, tuple):
            self.left = (self.left,)
        self.right = right
        if type(self.right) not in (list, tuple):
            self.right = (self.right,)
        self.iterations=iterations
        self.maxt = maxt
        self.dv0 = dv0
        self.tol = tol        

    def calc_dv(self, t, s):
        '''
        Calculate magnitude of delta-v correction vector directed
        along self.direction.
        
        Parameters
        ----------
        t : float
            Time when correction should be made
            
        s : numpy array
            State 
            
        Return
        ------
        dv : numpy array
            Delta-v vector embedded in model zero state.
            Correction maneuver can be made like this:
                s += dv
            
        '''
        if self.before:
            detector_before = event_detector(self.model, self.before, tol=self.tol)
        detector = event_detector(self.model, self.left+self.right, tol=self.tol)
        
        s1 = s.copy()
        vstart = s[3:6].copy()
        dv = self.dv0
        d = self.direction(t, s)

        def get_border(v):
            s1[3:6] = vstart+v*d
            if self.before:
                _, ev0 = detector_before.prop(s1, t, t+self.maxt, ret_df=False)
                if ev0.shape[0] < 1:
                    raise RuntimeError(self.error_before_unreachable)
                s2 = ev0[-1,4:]
            else:
                s2 = s1
            _, ev = detector.prop(s2, t, t+self.maxt, ret_df=False)
            if ev.shape[0] < 1:
                raise RuntimeError(self.error_borders_unreachable)
            return -1 if ev[-1,0] < len(self.left) else 1

        # root separation
        for i in range(self.iterations[0]):  
            pa = get_border(-dv)
            pb = get_border( dv)
            if pa == pb:
                dv *= 10
            else:
                break
#        print('separation: %e, it=%d'%(self.dv0,i))
        if i == self.iterations[0]:
            raise RuntimeError(self.error_root_separation)
        
        # root calculation
        res = bisect(get_border, -dv, dv, 
                     xtol=self.tol, maxiter=self.iterations[1],
                     full_output=True)
        v = res[0]
#        print('bisection: %e, it=%d'%(v, res[1].iterations))
        r = self.model.get_zero_state()
        r[:] = 0
        r[3:6] = v * d
        return r
    
class max_time_correction(base_correction):
    error_borders_unreachable = "Borders unreachable"

    def __init__(self, model,
                 direction,
                 border,
                 iterations=500, maxt=10*np.pi,
                 dv0 = 0.1, tol=1e-16):
        super().__init__(model, direction)
        self.border = border
        if type(self.border) not in (list, tuple):
            self.border = (self.border,)
        self.iterations=iterations
        self.maxt = maxt
        self.tol = tol
        self.dv0 = dv0
        self.mode = 0

    def calc_dv(self, t, s):
        detector = event_detector(self.model, self.border, tol=self.tol)
        d = self.direction(t, s)

        def time2border(v, s, beta_n):
#            print(v)
            s1 = s.copy()
            s1[3:6] += v * d
            arr, ev = detector.prop(s1, t, t+self.maxt, ret_df=False)
#            plt.plot(arr[:,1], arr[:,2])
            if ev.shape[0] < 1:
                raise RuntimeError(self.error_borders_unreachable)
            return -ev[-1,3]
        
        v = brent(time2border, args=(s, d),
                  brack=(-self.dv0, self.dv0),
                  tol=self.tol, maxiter=self.iterations)
        
        res = self.model.get_zero_state()
        res[:] = 0
        res[3:6] = v * d
        return res        
       
#class border_correction_deprecated(base_correction):
#    error_borders_unreachable = "Borders unreachable"
#    error_max_iterations_reached = "Maximum iterations number reached"
#    error_root_separation = "Can't separate discontinuity point"
#    
#    def __init__(self, model, direction, 
#                 left, right,
#                 iterations=(20,100),
#                 maxt=10*np.pi,
#                 dv0=1e-12, 
#                 tol=1e-16):
#        super().__init__(model, direction)
#        self.left = left
#        if type(self.left) not in (list, tuple):
#            self.left = (self.left,)
#        self.right = right
#        if type(self.right) not in (list, tuple):
#            self.right = (self.right,)
#        self.iterations=iterations
#        self.maxt = maxt
#        self.dv0 = dv0
#        self.tol = tol        
#
#    def calc_dv(self, t, s):
#        detector = event_detector(self.model, self.left+self.right, tol=self.tol)
#        
#        s1 = s.copy()
#        vstart = s[3:5].copy()
#        dv = self.dv0        
#        d = self.direction(t, s)
#
#        def get_border(v):
#            s1[3:6] = vstart+v*d
#            _, ev = detector.prop(s1, t, t+self.maxt, ret_df=False)
#            if ev.shape[0] < 1:
#                raise RuntimeError(self.error_borders_unreachable)
#            return -1 if ev[-1,0] < len(self.left) else 1
#
#        # root separation
#        for i in range(self.iterations[0]):  
#            pa = get_border(-dv)
#            pb = get_border( dv)
#            if pa == pb:
#                dv *= 10
#            else:
#                break
##        print('separation: %e, it=%d'%(self.dv0,i))
#        if i == self.iterations[0]:
#            raise RuntimeError(self.error_root_separation)
#        # root calculation
#        res = bisect(get_border, -dv, dv, 
#                     xtol=self.tol, maxiter=self.iterations[1],
#                     full_output=True)
#        v = res[0]
##        print('bisection: %e, it=%d'%(dv, res[1].iterations))
#        r = self.model.get_zero_state()
#        r[:] = 0
#        r[3:6] = v * d
#        return r

#class border_correction_old(base_correction):
#    '''
#    Calculates delta-V using left and right borders.
#    For example, borders are two planes orthogonal to x axis: one located 
#    to the left of unstable point and one - to the right.
#    See S.A. Aksenov, S.A. Bober "Calculation and Study of Limited Orbits
#    around the L2 Libration Point of the Sun–Earth System". Cosmic Research, 
#    2018, Vol. 56, No. 2, pp. 144–150.
#    '''
#    error_borders_unreachable = "Borders unreachable"
#    error_max_iterations_reached = "Maximum iterations number reached"
#    
#    def __init__(self, model, left, right,
#                 iterations=100, maxt=10*np.pi,
#                 angles=(90, 0), dv0 = 0.1, 
#                 tol=1e-16):
#        '''
#        Initializes border_correction instance.
#        
#        Parameters
#        ----------
#        model : base_model instance
#            Intended for constructing event_detector that detects border
#            crossing by spacecraft.
#            
#        left, right : list(base_event, ...) or tuple(base_event, ...)
#            Lists of events that represents left and right borders.
#            
#        iterations : int
#            Maximum number of iterations allowed for delta-V calculation.
#            
#        maxt : float
#            Maximum time allowed for spacecraft to reach borders.
#            
#        angles : tuple of two floats
#            angles[0] for first correction and angles[1] - for the rest.
#            
#        dv0 : float
#            Initial step for delta-V calculation.
#            
#        tol : float
#            Absolute tolerance for delta-V value.
#        '''
#        super().__init__(model)
#        self.left = left
#        if type(self.left) not in (list, tuple):
#            self.left = (self.left,)
#        self.right = right
#        if type(self.right) not in (list, tuple):
#            self.right = (self.right,)
#        self.iterations=iterations
#        self.maxt = maxt
#        self.angles = angles
#        self.dv0 = dv0
#        self.tol = tol
#
#    def calc_dv(self, t, s):
#        '''
#        Calculates delta-V.
#        
#        Parameters
#        ----------
#        t : float
#            Initial time for delta-V calculation.
#            
#        s : numpy.ndarray
#            State vector of spacecraft at time t.
#            
#        Return
#        ------
#        dv : numpy.ndarray
#            Calculated delta-V.
#            Size of array is as model.get_zero_state() returns.
#        '''
#        detector = event_detector(self.model, self.left+self.right, tol=self.tol)
#
#        s1 = s.copy()
#        vstart = s1[3:5].copy()
#        dv = self.dv0
#        
#        rads = math.radians(self.angles[self.mode])
#        beta_n = np.array([math.cos(rads), math.sin(rads)])
#           
#        _, ev = detector.prop(s1, t, t+self.maxt, ret_df=False)
#        if ev.shape[0] < 1:
#            raise RuntimeError(self.error_borders_unreachable)
#        p = 0 if ev[-1,0] < len(self.left) else 1
#        s1[3:5] = vstart + dv * beta_n
#
#        _, ev = detector.prop(s1, t, t+self.maxt, ret_df=False)
#        if ev.shape[0] < 1:
#            raise RuntimeError(self.error_borders_unreachable)
#        p1 = 0 if ev[-1,0] < len(self.left) else 1
#        
#        if p == p1 and p == 1:
#            dv = -dv
#           
#        v = dv        
#        i = 0
#        while math.fabs(dv) > self.tol and i < self.iterations:
#            s1[3:5] = vstart + v * beta_n
#            _, ev = detector.prop(s1, t, t+self.maxt, ret_df=False)
#            if ev.shape[0] < 1:
#                raise RuntimeError(self.error_borders_unreachable)
#            p1 = 0 if ev[-1,0] < len(self.left) else 1
#         
#            if p1 != p:
#                v -= dv
#                dv *= 0.5
#    
#            v += dv
#            i += 1
#        if i == self.iterations:
#            raise RuntimeError(self.error_max_iterations_reached)
#        self.mode = 1
#        res = self.model.get_zero_state()
#        res[:] = 0
#        res[3:5] = v * beta_n
#        return res

