# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 21:16:30 2018

@author: stasb
"""

import numpy as np
import math
from .events import event_detector, eventY

class differential_correction:
    def __init__(self, model, iterations=30, tol=1e-12):
        self.iterations = iterations
        self.tol = tol
        self.model = model

    @property
    def model(self):
        return self._model
    
    @model.setter
    def model(self, model):
        if not model.stm:
            raise ValueError('Differential correction needs state-transition matrix (STM)')
        self._model = model
        self._detector = event_detector(self._model, [eventY()], self.tol)
            
    def find_halo(self, s0, fixed='z0', ret_it=False, ftol=1e-12):
        i = 0
        s = s0.copy()
        while i < self.iterations:
            _, evout = self._detector.prop(s, 0., 700*np.pi, ret_df=False)
#            print(evout[-1, 2])
            ev = evout[-1, 3:] # i(0), cnt(1), t(2), x(3), y(4), z(5), ...
            xf = ev[:6]
#            print(xf)
            if math.fabs(xf[3]) < ftol and math.fabs(xf[5]) < ftol:
                break
#            print('shape:', ev.shape)
            dxdt = self._model.right_part(0., ev, self._model.constants)
#            print(xf, dxdt)
            Phi = ev[6:42].reshape(6, 6)
        
            if fixed == 'x0':
                m = np.array([[Phi[3,2], Phi[3,4]], [Phi[5,2], Phi[5,4]]])\
                -1/dxdt[1]*np.array([[dxdt[3]],[dxdt[5]]])@np.array([Phi[1,2], Phi[1,4]], ndmin=2)
                dx = np.linalg.solve(m, -xf[[3,5]])
                s[[2,4]] += dx
                
            if fixed == 'z0':
                m = np.array([[Phi[3,0], Phi[3,4]], [Phi[5,0], Phi[5,4]]])\
                -1/dxdt[1]*np.array([[dxdt[3]],[dxdt[5]]])@np.array([Phi[1,0], Phi[1,4]], ndmin=2)
                dx = np.linalg.solve(m, -xf[[3,5]])
                s[[0,4]] += dx 
    
            i += 1
        if i < self.iterations:
            pass
#            print("Converged i =", i, "halo", s)
        else:
            print("Hasn't converged")
        if ret_it:
            return s, i
        return s
    
