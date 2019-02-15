# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 23:45:09 2018

@author: stasb
"""

import pkg_resources
import numpy as np
import pandas as pd
from numba import compiler, types
from scipy.optimize import root
from .integrators import base_integrator, dop853_integrator
from .solout import default_solout

class base_model:
    '''
    Class base_model is intended to provide interface to all presented or
    future models used in orbipy.
    Model consists of but not limited to: 
        - physical constants,
        - reference to integrator object,
        - ...
    '''
    def __init__(self):
        self._constants = np.zeros((1,))
        self.integrator = None
        self.columns = []
        self.stm = False
        
    @property
    def constants(self):
        return self._constants
    
    @constants.setter
    def constants(self, constants):
        self._constants = constants
        
    def get_state_size(self, stm=None):
        pass
    
    def get_zero_state(self):
        pass
    
    def prop(self, s0, t0, t1, ret_df=True):
        pass
    
    def to_df(self):
        return pd.DataFrame()
        
    def __repr__(self):
        return "base_model class instance"

class nondimensional_model(base_model):
    '''
    Class nondimensional_model is intended to provide interface to all
    presented or future nondimensional models used in orbipy.
    '''
    def get_nd_coefs(self):
        return {'T':1., 'L':1.}

def load_constants_csv(fname):
    with open(fname, 'rt') as f:
        df = pd.read_csv(f, index_col=0)
    return df

class crtbp3_model(nondimensional_model):
    '''
    Class crtbp3_model presents Circular Restricted Three-Body Problem model
    in nondimensional formulation (see Murray, Dermott "Solar System Dynamics").
    
    Example
    -------
    
    
    '''
    constants_csv = pkg_resources.resource_filename(__name__, 'data/crtbp_constants.csv')
    constants_df = load_constants_csv(constants_csv)
    
    columns = ['t', 'x', 'y', 'z', 'vx', 'vy', 'vz']
    columns_stm = columns + ["stm%d%d"%(i,j) for i in range(6) for j in range(6)]

    def __init__(self, const_set='Sun-Earth (default)', 
                       integrator=None, 
                       solout=default_solout(), stm=False):
        '''
        Initializes crtbp3_model instance using name of a constant set,
        reference to integrator and reference to solout callback.
        
        Parameters
        ----------
        
        const_set : str
            Constant set name. Following will be loaded from
            'data/crtbp_constants.csv' file:
                - mu - gravitational constant, mu = m/(M+m), \
                    where m is smaller mass, M is bigger mass;
                - R - distance between primaries in km;
                - T - synodic period of primaries in seconds.
                
        integrator : object
            Object used for numerical intergration of model equation set.
            Should inherit from base_integrator.
            By default: dop853_integrator
            
        solout : object
            Solout callback object will be used for gathering all 
            integration steps from scipy.integrate.ode integrators
            and for event detection routines.
            Should inherit from base_solout.
            By default: default_solout which can only gather all
            integration steps.
        '''
#        doesn't work with russian symbols in file path        
#        self.df = pd.read_csv(self.constants_csv, index_col=0)
        self._constants = np.array(self.constants_df.loc[const_set,'mu':'T'].values, dtype=float)
        self.M = self.constants_df.loc[const_set, 'M']
        self.m = self.constants_df.loc[const_set, 'm']
        self.mu = self._constants[0]
        self.mu1 = 1.0 - self.mu
        self.R = self._constants[1]
        self.T = self._constants[2]
        self.const_set = const_set
        if integrator is None:
            self.integrator = dop853_integrator()
        else:
            if not isinstance(integrator, base_integrator):
                raise TypeError('integrator should be an instance ob base_integrator')
            self.integrator = integrator
        self.solout = solout
        self.stm = stm
        self.columns = crtbp3_model.columns_stm if self.stm else crtbp3_model.columns
        if stm:
#            self.right_part = compiler.compile_isolated(crtbp3_model.crtbp_ode_stm, 
#                                                        [types.double, types.double[:], types.double[:]], 
#                                                        return_type=types.double[:]).entry_point
            self.right_part = self.crtbp_ode_stm_compiled
        else:
#            self.right_part = compiler.compile_isolated(crtbp3_model.crtbp_ode, 
#                                                        [types.double, types.double[:], types.double[:]], 
#                                                        return_type=types.double[:]).entry_point
            self.right_part = self.crtbp_ode_compiled
            
        self.L = self.lagrange_points()
        self.L1 = self.L[0, 0]
        self.L2 = self.L[1, 0]
        self.L3 = self.L[2, 0]

    def get_nd_coefs(self):
        '''
        Calculates nondimensional coefficients which is used by scaler
        for conversion between nondimensional units and physical.
        '''
        return {'T':self.T / (2*np.pi),
                'L':self.R}
        
    @property
    def solout(self):
        '''
        solout property getter
        '''
        return self._solout
    
    @solout.setter
    def solout(self, solout):
        '''
        solout property setter
        '''
        if not solout:
            raise RuntimeWarning('Incorrect solout function/object')
            self._solout = default_solout()
        else:
            self._solout = solout    
        if self.integrator:
            self.integrator.solout = self._solout
        

    def lagrange_points(self):
        '''
        Numerically calculate position of all 5 Lagrange points.
        
        Returns
        -------
        
        L : np.array of (5, 3) shape
            Positions of Lagrange points for this model.
        '''
        def opt(x, constants):
            s = self.get_zero_state()
            s[0] = x[0]
            return self.right_part(0., s, constants)[3]
        
        L = np.zeros((5, 3))
        L[0, 0] = root(opt,  0.5, args=(self._constants,)).x[0]
        L[1, 0] = root(opt,  2.0, args=(self._constants,)).x[0]
        L[2, 0] = root(opt, -1.0, args=(self._constants,)).x[0]
        L[3, 0] = 0.5 - self.mu
        L[3, 1] = 0.5*3**0.5
        L[4, 0] = 0.5 - self.mu
        L[4, 1] = -0.5*3**0.5
        return L

    def omega(self, s):
        if s.ndim == 1:
            r1 = ((s[0] + self.mu )**2 + s[1]**2 + s[2]**2)**0.5
            r2 = ((s[0] - self.mu1)**2 + s[1]**2 + s[2]**2)**0.5
            return 0.5*(s[0]**2 + s[1]**2) + self.mu1/r1 + self.mu/r2        
        else:
            r1 = np.sqrt((s[:,0] + self.mu )**2 + s[:,1]**2 + s[:,2]**2)
            r2 = np.sqrt((s[:,0] - self.mu1)**2 + s[:,1]**2 + s[:,2]**2)
            return 0.5*(s[:,0]**2 + s[:,1]**2) + self.mu1/r1 + self.mu/r2
        
    def jacobi(self, s):
        if s.ndim == 1:
            return 2*self.omega(s) - s[3]**2 - s[4]**2 - s[5]**2
        else:
            return 2*self.omega(s) - s[:,3]**2 - s[:,4]**2 - s[:,5]**2

    #@staticmethod
    def crtbp_ode(t, s, constants):
        '''
        Right part of CRTPB ODE
    
        Parameters
        ----------
        t : scalar
            Nondimensional time (same as angle of system rotation).
    
        s : np.array with 6 components
            State vector of massless spacecraft (x,y,z,vx,vy,vz).
    
        constants : np.array
             mu = constants[0] - gravitaional parameter of crtbp model
    
        Returns
        -------
    
        ds : np.array
            First order derivative with respect to time of spacecraft
            state vector (vx,vy,vz,dvx,dvy,dvz)
        '''
        mu2 = constants[0]
        mu1 = 1 - mu2
        
        x, y, z, vx, vy, vz = s
        
        yz2 = y * y + z * z
        r13 = ((x + mu2) * (x + mu2) + yz2) ** (-1.5)
        r23 = ((x - mu1) * (x - mu1) + yz2) ** (-1.5)
    
        mu12r12 = (mu1 * r13 + mu2 * r23)
    
        ax =  2 * vy + x - (mu1 * (x + mu2) * r13 + mu2 * (x - mu1) * r23)
        ay = -2 * vx + y - mu12r12 * y
        az =             - mu12r12 * z
        
        ds = np.array([vx, vy, vz, ax, ay, az])
        
        return ds

    crtbp_ode_compiled = \
    compiler.compile_isolated(crtbp_ode, 
                              [types.double, types.double[:], types.double[:]], 
                              return_type=types.double[:]).entry_point

    #@staticmethod    
    def crtbp_ode_stm(t, s, constants):
        '''
        Right part of CRTPB ODE with State Transform Matrix calculation.
    
        Parameters
        ----------
        t : scalar
            Nondimensional time (same as angle of system rotation).
    
        s : np.array with 42 (=6+6*6) components
            State vector of massless spacecraft (x,y,z,vx,vy,vz) along with
            flattened STM matrix (stm00,stm01,stm02,...stm55).
    
        constants : np.array
             mu = constants[0] - gravitaional parameter of crtbp model
    
        Returns
        -------
    
        ds : np.array
            First order derivative with respect to time of spacecraft
            state vector along with flattened derivative of STM matrix
            (vx,vy,vz,dvx,dvy,dvz,dstm00,dstm01,...,dstm55)
        '''
    
        x, y, z, vx, vy, vz = s[:6]
        stm0 = np.ascontiguousarray(s[6:]).reshape(6,6)
        mu2 = constants[0]
        mu1 = 1 - mu2
        
        yz2 = y * y + z * z;
        xmu2 = x + mu2
        xmu1 = x - mu1
    
        r1 = (xmu2**2 + yz2)**0.5
        r2 = (xmu1**2 + yz2)**0.5
        r13, r15 = r1**(-3), r1**(-5)
        r23, r25 = r2**(-3), r2**(-5)
    
        mu12r12 = (mu1 * r13 + mu2 * r23);
    
        ax =  2. * vy + x - (mu1 * xmu2 * r13 + mu2 * xmu1 * r23);
        ay = -2. * vx + y - mu12r12 * y;
        az =              - mu12r12 * z;
            
        Uxx = 1. - mu12r12 + 3*mu1*xmu2**2*r15 + 3*mu2*xmu1**2*r25
        Uxy = 3*mu1*xmu2*y*r15 + 3*mu2*xmu1*y*r25
        Uxz = 3*mu1*xmu2*z*r15 + 3*mu2*xmu1*z*r25
        Uyy = 1. - mu12r12 + 3*mu1*y**2*r15 + 3*mu2*y**2*r25
        Uyz = 3*mu1*y*z*r15 + 3*mu2*y*z*r25
        Uzz = -mu12r12 + 3*mu1*z**2*r15 + 3*mu2*z**2*r25
        
        A = np.array(((0.,  0.,  0.,   1., 0., 0.),
                      (0.,  0.,  0.,   0., 1., 0.),
                      (0.,  0.,  0.,   0., 0., 1.),
                      (Uxx, Uxy, Uxz,  0., 2., 0.),
                      (Uxy, Uyy, Uyz, -2., 0., 0.),
                      (Uxz, Uyz, Uzz,  0., 0., 0.)))
    
        stm1 = np.dot(A,stm0)
        ds = np.empty_like(s)
        ds[0], ds[1], ds[2], ds[3], ds[4], ds[5] = vx, vy, vz, ax, ay, az
        ds[6:] = stm1.ravel()
        
        return ds

    crtbp_ode_stm_compiled = \
    compiler.compile_isolated(crtbp_ode_stm, 
                              [types.double, types.double[:], types.double[:]], 
                              return_type=types.double[:]).entry_point

    def get_state_size(self, stm=None):
        '''
        Calculate size of a spacecraft state vector.
        '''
        if stm is None:
            return 42 if self.stm else 6
        else:
            return 42 if stm else 6
    
    def get_zero_state(self):
        '''
        Returns
        -------
            zs : numpy.ndarray
                State vector of appropriate size filled with zeros.
                If state contains STM then STM is filled by eye matrix.
        '''
        if self.stm:
            zs = np.zeros(42)
            zs[6::7] = 1.0 # set eye matrix
            return zs
        else:
            return np.zeros(6)
    
    def prop(self, s0, t0, t1, ret_df=True):
        '''
        Propagate spacecraft from initial state s0 at time t0 up to time t1.
        
        Parameters
        ----------
        
        s0 : np.array
            Spacecraft initial state of size that match model
            
        t0 : float
            Initial time
            
        t1 : float
            Boundary time
            
        ret_df : bool
            If True, returns pd.DataFrame
            Else, returns np.array
            
        Returns
        -------
            df : np.array (ret_df=False) of pd.DataFrame (ret_df=True)
                Array or DataFrame consists of spacecraft states for all
                steps made by integrator from t0 to t1.
        
        '''
        self._solout.reset()
        self.integrator.integrate(self.right_part, s0, t0, t1, fargs=(self._constants,))
        if ret_df:
            return self.to_df(self._solout.out)
        else:
            return np.array(self._solout.out)
    
    def to_df(self, arr, columns=None):#, index_col='t'):
        if columns is None:
            columns = self.columns
        df = pd.DataFrame(arr, columns=columns)
#        df.set_index(index_col, inplace=True)
        return df
    
    def __repr__(self):
        return 'CRTBP3 model%s:%r'%(' with STM' if self.stm else '', 
                                    self.const_set)
    
        