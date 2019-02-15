# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 13:30:46 2018

@author: stasb
"""

import numpy as np
from numpy.random import rand
import pandas as pd

from .models import base_model
from .corrections import base_correction
from .events import base_event, event_detector
from .scaler import scaler

class base_station_keeping:
    '''
    Class base_station_keeping is base class for all station-keeping
    techniques in OrbiPy.
    
    In astrodynamics, the orbital maneuvers made by thruster burns that 
    are needed to keep a spacecraft in a particular assigned orbit are 
    called orbital station-keeping.
    https://en.wikipedia.org/wiki/Orbital_station-keeping
    
    Common scheme
    -------------
    All impulsive station-keeping techniques for unstable orbits near 
    Lagrange points use common scheme:
        (1) Orbit determination (made by first_correction)
        (2) Propagation up to specified time or event (rev)
        (3) Calculation of delta-v (made by correction) and execution of maneuver
        (4) Repeat (2)-(3) for N times
    '''
    def __init__(self, model, first_correction, correction,
                 rev, events,  maxt,
                 verbose=True):
        if not isinstance(model, base_model):
            raise TypeError('model should be an instance of base_model')
        self.model = model
        if not isinstance(first_correction, base_correction):
            raise TypeError('first_correction should be an instance of base_correction')
        self.first_correction = first_correction
        if not isinstance(correction, base_correction):
            raise TypeError('correction should be an instance of base_correction')
        self.correction = correction
        self.rev = rev
        self.is_rev_event = isinstance(rev, base_event)
        self.events = events
        self.maxt = maxt
        self.verbose = verbose
        self.reset()

    def reset(self):
        self.dvout = []
        self.evout = []
        
    def prop(self, t0, s0, N=10, ret_df=True):
        pass
    
    
class simple_station_keeping(base_station_keeping):
    '''    
    Common scheme
    -------------
    All impulsive station-keeping techniques for unstable orbits near 
    Lagrange points use common scheme:
        (1) Orbit determination (made by first_correction)
        (2) Propagation up to specified time or event (rev)
        (3) Calculation of delta-v (made by correction) and execution of maneuver
        (4) Repeat (2)-(3) for N times
        
    Class simple_station_keeping implements common scheme.
    
    See also
    --------
    base_station_keeping
    '''
    
    def __init__(self,
                 model,
                 first_correction, 
                 correction,
                 rev=np.pi,
                 events = [],
                 maxt=10*np.pi,
                 verbose=True):
        super().__init__(model, first_correction, correction, 
                         rev, events, maxt, verbose)
        
    def reset(self):
        super().reset()
        self.arr = []
        
    def prop(self, t0, s0, N=10, ret_df=True):
        self.reset()
                
        s1 = s0.copy()
        t1 = t0        
        
        if self.is_rev_event:
            events = tuple(self.events)+(self.rev,)
            maxt = self.maxt
        else:
            events = tuple(self.events)
            maxt = self.rev
            
        detector = event_detector(self.model, events)
        if self.verbose: print('Simple station-keeping:', end=' ')
        for i in range(N):
            if i == 0:
                # first correction == orbit determination
                dv = self.first_correction.calc_dv(t1, s1)
            else:
                dv = self.correction.calc_dv(t1, s1)
            s1 += dv
            self.dvout.append([t1, *dv])
            cur_rev, ev = detector.prop(s1, t1, t1+maxt, ret_df=False)
            if ev.shape[0] > 0:
                self.evout.append(ev)
            t1 = cur_rev[-1,0]
            s1 = cur_rev[-1,1:].copy()
#            t1 = ev[-1,2]
#            s1 = ev[-1,3:].copy()
            self.arr.append(cur_rev.copy() if i==N-1 else cur_rev[:-1].copy())
            if self.verbose: print(i, end=' ')
        
        if self.verbose: print()
        arr = np.vstack(tuple(self.arr))
        if len(self.dvout) > 0:
            self.dvout = np.array(self.dvout)
        if len(self.evout) > 0:
            self.evout = np.vstack(tuple(self.evout))
        if ret_df:
            df = self.model.to_df(arr)
            return df
        else:
            return arr
        
class montecarlo_station_keeping(base_station_keeping):
    '''
    Common scheme
    -------------
    All impulsive station-keeping techniques for unstable orbits near 
    Lagrange points use common scheme:
        (1) Orbit determination (made by first_correction)
        (2) Propagation up to specified time or event (rev)
        (3) Calculation of delta-v (made by correction) and execution of maneuver
        (4) Repeat (2)-(3) for N times
        
    Monte-Carlo station-keeping
    ---------------------------
    Corrections are calculated using states with added random noise but
    maneuvers performed using states without noise. Noise is uniform and
    generated with numpy.random.rand generator (MT19937 algorithm).
    Noise is applied for:
        - spacecraft position: random vector in a ball of unc_pos radius;
        - spacecraft velocity: random vector in a ball of unc_vel radius;
        - delta-v: random vector in a ball which radius is unc_dv 
        percents of delta-v magnitude;
    '''
    def __init__(self, 
                 model,
                 first_correction,
                 correction,
                 unc_pos = (5, 'km'),
                 unc_vel = (5, 'cm/s'),
                 unc_dv  = 5, # percent
                 rev=np.pi,
                 events=[],
                 maxt=10*np.pi,              
                 verbose=True):
        super().__init__(model, first_correction, correction, rev, events, maxt, verbose)        
        self.scale = scaler.from_model(self.model)
        self.unc_pos = unc_pos
        self.unc_vel = unc_vel
        self.unc_dv  = unc_dv
        self.unc_pos_nd = self.scale.convert(self.unc_pos[0], self.unc_pos[1], 'nd')
        self.unc_vel_nd = self.scale.convert(self.unc_vel[0], self.unc_vel[1], 'nd/nd')
#        self.randout = []

    def reset(self):
        super().reset()
        self.randout = []

    @staticmethod
    def rand_ball_one():
        d = rand(3) * 2 - 1
        while d[0]**2+d[1]**2+d[2]**2 > 1:
            d = rand(3) * 2 - 1
        return d
    
    @staticmethod
    def rand_ball_v(v, r):
        d = rand(3) * 2 - 1
        while d[0]**2+d[1]**2+d[2]**2 > 1:
            d = rand(3) * 2 - 1
        return v + d * r
    
    @staticmethod
    def rand_ball_percent(v, r):
        d = rand(3) * 2 - 1
        while d[0]**2+d[1]**2+d[2]**2 > 1:
            d = rand(3) * 2 - 1
        nrm = (v[0]**2+v[1]**2+v[2]**2)**0.5
        return v + d * (nrm * r)

    def prop(self, t0, s0, N=10, ret_df=True):
        self.reset()
                
        s1 = s0.copy()
        t1 = t0        
        arr = []

        if self.is_rev_event:
            events = tuple(self.events)+(self.rev,)
            maxt = self.maxt
        else:
            events = tuple(self.events)
            maxt = self.rev
            
        detector = event_detector(self.model, events)
        
        if self.verbose: print('Montecarlo station-keeping:', end=' ')
        for i in range(N):
            up = self.rand_ball_one()*self.unc_pos_nd
            uv = self.rand_ball_one()*self.unc_vel_nd
            us = s1.copy()
            us[ :3] += up
            us[3:6] += uv
#            dv = self.correction.calc_dv(t1, us)
            if i == 0:
                # first correction == orbit determination
                dv = self.first_correction.calc_dv(t1, s1)
            else:
                dv = self.correction.calc_dv(t1, us)
            self.dvout.append([t1, *dv])        
            udv = self.rand_ball_percent(dv[3:6], self.unc_dv/100.)
            if i == 0:
                self.randout.append([*up, *uv, *dv[3:6]])
                s1 += dv
            else:
                self.randout.append([*up, *uv, *udv])
                s1[3:6] += udv
#            cur_rev, ev = event_detector(self.model, (self.rev,)).prop(s1, t1, t1+self.maxt, ret_df=False)
            cur_rev, ev = detector.prop(s1, t1, t1+maxt, ret_df=False)
            if ev.shape[0] > 0:
                self.evout.append(ev)

            t1 = cur_rev[-1,0]
            s1 = cur_rev[-1,1:].copy()
#            t1 = ev[-1,2]
#            s1 = ev[-1,3:].copy()
            arr.append(cur_rev.copy() if i==N-1 else cur_rev[:-1].copy())
            if self.verbose: print(i, end=' ')
        
        
        if self.verbose: print()
        arr = np.vstack(tuple(arr))
        if len(self.evout) > 0:
            self.evout = np.vstack(tuple(self.evout))
        
        if ret_df:
            df = self.model.to_df(arr)
            return df
        else:
            return arr
