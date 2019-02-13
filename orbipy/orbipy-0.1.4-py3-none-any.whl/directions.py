# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 16:08:03 2019

@author: stasb
"""

import numpy as np
import math
from scipy.optimize import brent
from .events import event_detector, base_event
from .models import base_model

class base_direction:    
    '''
    Class direction is a base class for all direction calculation
    algorithms in OrbiPy. Direction is a normalized 3D vector.
    Directions are used in correction methods to define axis of
    correction maneuver.
    '''
    def __call__(self, t, s):
        return np.array([1., 0., 0.])
    
class xy_angle_direction(base_direction):
    '''
    Constant direction in XY plane determined by angle
    counted from X axis anticlockwise.
    '''
    def __init__(self, angle):
        self.angle = angle
        rads = math.radians(self.angle)
        self.direction = np.array([math.cos(rads), math.sin(rads), 0.])
        
    def __call__(self, t, s):
        return self.direction

class x_direction(base_direction):
    '''
    Constant direction along X axis.
    '''
    direction = np.array([1., 0., 0.])
        
    def __call__(self, t, s):
        return self.direction


class y_direction(base_direction):
    '''
    Constant direction along Y axis.
    '''
    direction = np.array([0., 1., 0.])

    def __call__(self, t, s):
        return self.direction

        
class velocity_direction(base_direction):
    '''
    Direction along spacecraft velocity.
    '''
    def __call__(self, t, s):
        return s[3:6]/(s[3]**2+s[4]**2+s[5]**2)**0.5

class unstable_direction_stm(base_direction):
    '''
    Unstable direction at which most effective corrections
    can be made. Calculated using eigenvector corresponding
    to real positive (i.e. unstable) eigenvalue of State
    Transition Matrix calculated after a specified time
    elapsed since initial time.
    '''
    def __init__(self, 
                 model,
                 event=np.pi,
                 maxt=10*np.pi,
                 ignore_z=False):
        if not isinstance(model, base_model):
            raise TypeError('model should be an instance of base_model')
        if not hasattr(model, 'stm') or model.stm==False:
            raise ValueError('model should support STM calculation')
        self.model = model
        self.maxt = maxt
        self.event = event
        self.is_event = isinstance(event, base_event)
        self.ignore_z = ignore_z
        self.eigvals = []
        self.eigvecs = []

    def __call__(self, t, s):
        s0 = self.model.get_zero_state()
        s0[:s.shape[0]] = s
        if self.is_event:
            detector = event_detector(self.model, [self.event])
            _, ev = detector.prop(s0, t, t+self.maxt)
            _, df = detector.split_data(ev)            
            stm = df.values[-1,7:].reshape(6,6)
        else:
            arr = self.model.prop(s0, t, t+self.event, ret_df=False)
            # t(0),x(1),y(2),z(3),vx(4),vy(5),vz(6),stm00(7), ...
            stm = arr[-1,7:].reshape(6,6)
        eigvals, eigvecs = np.linalg.eig(np.linalg.inv(stm)[0:3,0:3])

        idx = 0 if eigvals[0].real > eigvals[1].real else 1
        
        d = np.abs(eigvecs[:,idx])

        if d[0] < 0.:
            d = -d
        if self.ignore_z:
            d[2] = 0.
        d = d / (d[0]**2+d[1]**2+d[2]**2)**0.5
        return d
    
class unstable_direction(base_direction):
    '''
    Unstable direction at which most effective corrections
    can be made. Calculated by maximization of velocity deviation
    after forward propagation of disturbed state for maxt time.
    '''
    def __init__(self, 
                 model,
                 disturbance=1e-8,
                 maxt=np.pi,
                 tol=1e-5,
                 iterations=100):
        if not isinstance(model, base_model):
            raise TypeError('model should be an instance of base_model')
        self.model = model
        self.disturbance = disturbance
        self.maxt = maxt
        self.iterations = iterations
        self.tol = tol

    def __call__(self, t, s):
        s0 = self.model.get_zero_state()
        s0 = s[:s0.shape[0]]
        # t(0),x(1),y(2),z(3),vx(4),vy(5),vz(6),stm00(7), ...
        c = self.model.prop(s0, t, t+self.maxt, ret_df=False)[-1]
        def goal(beta):
            s1 = s0.copy()
            s1[3] += self.disturbance * math.cos(beta)
            s1[4] += self.disturbance * math.sin(beta)
            p = self.model.prop(s1, t, t+self.maxt, ret_df=False)[-1]
            return -((p[3]-c[3])**2+(p[4]-c[4])**2)
        
        ret = brent(goal, brack=(0,2*np.pi), maxiter=self.iterations, 
                    tol=self.tol, full_output=True)
#        print(ret)
        
        beta = ret[0]
        d = np.array([math.cos(beta), math.sin(beta), 0.])
        
        if d[0] < 0.:
            d = -d

        return d
