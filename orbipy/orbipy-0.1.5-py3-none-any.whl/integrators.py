# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 00:23:47 2018

@author: stasb
"""

import numpy as np
import pandas as pd
import scipy.integrate
#from numba import compiler, types


class base_integrator:
    '''
    Base interface for all integrator wrappers that will be used in OrbiPy.
    Integrator should provide solout functionality similar to 
    scipy.integrate.ode.
    '''
    def __init__(self, params):
        self._solout = None
        self._params = params
        
    def get_params(self):
        return self._params
    
    def set_params(self, **params):
        self._params.update(params)
        
    @property
    def solout(self):
        '''Get/set solout callable.
           Solout callable used for full trajectory output and
           event detection.
        '''
        return self._solout
        
    @solout.setter
    def solout(self, solout):
        '''Set solout callable.'''
        self._solout = solout

    def integrate(self, func, s0, t0, t1):
        '''Integrate func from initial state s0 at time t0 to time t1.'''
        return np.array([t0, *s0])

class quasi_integrator(base_integrator):
    '''
    Quasi integrator provides integrator interface as a proxy for already 
    calculated trajectory data (numpy.array or pandas.DataFrame). Can be
    used for calculation of additional events on existing orbit.
    '''
    def __init__(self, data, solout=None):
        self.data = data
        self._solout = solout

    def get_params(self):
        return None
    
    def set_params(self, **params):
        pass
        
    @property
    def solout(self):
        return self._solout
        
    @solout.setter
    def solout(self, solout):
        self._solout = solout

    def integrate(self, func, s0, t0, t1, fargs=()):
        ''' Runs all states from self.data trough solout callable.
        '''
        if isinstance(self.data, pd.DataFrame):
            t = self.data.values[:,0]
            arr = self.data.values[:,1:]
        else:
            t = self.data[:,0]
            arr = self.data[:,1:]
        #self._solout.reset()
        for i in range(len(t)):
            if self._solout(t[i], arr[i]) == -1:
                break
        return self.data
        
class dop853_integrator(base_integrator):
    '''
    Adapter for scipy.integrate.ode class with dop853 integrator.
    '''
    def __init__(self,
                 params={'rtol':1e-12, 'atol':1e-12, 
                         'nsteps':100000, 'max_step':np.inf},
                 solout=None):
        if params and isinstance(params, dict):
            self._params = params.copy()
        else:
            self._params = {}
        self._solout = solout
        self.integrator = None
        self.func = None

    
    def set_params(self, **params):
        self._params.update(params)
        if self.integrator:
            self.integrator.set_integrator('dop853', **self._params)

    @property
    def solout(self):
        return self._solout
        
    @solout.setter
    def solout(self, solout):
        self._solout = solout
        if solout and self.integrator:
            self.integrator.set_solout(self._solout)

    def integrate(self, func, s0, t0, t1, fargs=()):
        if not func:
            raise ValueError('Function is not defined')
        
        if not self.integrator or func != self.func:
            self.func = func
            self.integrator = scipy.integrate.ode(func)
            self.integrator.set_integrator('dop853', **self._params)
                
#        print(self.params['max_step'])
        if self._solout:
            self.integrator.set_solout(self._solout)
        self.integrator.set_f_params(*fargs)        
        self.integrator.set_initial_value(s0, t0)
        return self.integrator.integrate(t1)
    
class dopri5_integrator(base_integrator):
    '''
    Adapter for scipy.integrate.ode class with dopri5 integrator.
    '''
    def __init__(self, 
                 params={'rtol':1e-12, 'atol':1e-12, 
                         'nsteps':100000, 'max_step':np.inf}, 
                 solout=None):
        if params and isinstance(params, dict):
            self._params = params.copy()
        else:
            self._params = {}
        self._solout = solout
        self.integrator = None
        self.func = None
    
    def set_params(self, **params):
        self._params.update(params)
        if self.integrator:
            self.integrator.set_integrator('dopri5', **self._params)

    @property
    def solout(self):
        return self._solout
        
    @solout.setter
    def solout(self, solout):
        self._solout = solout
        if solout and self.integrator:
            self.integrator.set_solout(self._solout)

    def integrate(self, func, s0, t0, t1, fargs=()):
        if not func:
            raise ValueError('Function is not defined')
        
        if not self.integrator or func != self.func:
            self.func = func
            self.integrator = scipy.integrate.ode(func)        
            self.integrator.set_integrator('dopri5', **self._params)
            
        if self._solout:
            self.integrator.set_solout(self._solout)
        self.integrator.set_f_params(*fargs)  
        self.integrator.set_initial_value(s0, t0)
        return self.integrator.integrate(t1)
