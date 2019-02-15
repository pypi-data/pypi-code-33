# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 00:31:13 2018

@author: stasb

This module is intended for event detection technique.

Event defined as time when some function E(t,s) called event-function reaches
specific value E*. In other words event detection is a root-finding process
for EF(t,s)=E(t,s)-E* function.
Detection splits into two steps: root separation and root refinement.
Root separation is finding two consecutive times ti, tj and states si, sj
(calculated through integration) such as EF(ti,si)*EF(tj,sj) < 0.
Root refinement is calculation of time t* and state s* such as 
|EF(t*,s*)| < eps, where eps is specified accuracy.

Root separation takes into account direction at which event-function reaches
its E* value:
    
direction <=> condition
    -1        EF(ti,si)>0 and EF(tj,sj)<0
     1        EF(ti,si)<0 and EF(tj,sj)>0
     0        EF(ti,si)*EF(tj,sj) < 0
     
Events can be terminal and non terminal. Terminal events tells integrator
when it should terminate integration process and therefore can be treated
as boundary conditions.


"""

import math
import pandas as pd
import numpy as np
from scipy.optimize import root as scipy_root
#from scipy.optimize import brentq
from scipy.interpolate import interp1d

from .solout import default_solout, event_solout
from .models import base_model
from .plotter import plottable

class event_detector:
    '''
    Class event_detector is intended for event detection during
    integration of ODE system.
    '''
    columns = ['e', 'cnt', 'trm']
    
    def __init__(self, model, events, tol=1e-12, accurate_model=None):
#        if not issubclass(model.__class__, base_model):
        if not isinstance(model, base_model):
            raise TypeError("model should be instance of base_model class or of a subclass thereof")
        self.model = model
        if accurate_model is not None and not isinstance(accurate_model, base_model):
            raise TypeError("accurate_model should be instance of base_model class or of a subclass thereof")
        self.accurate_model = model if accurate_model is None else accurate_model
#        if not events:
#            raise ValueError("Empty events list")
        self.events = events
        self.solout = event_solout(self.events)
        self.tol = tol
        
    def prop(self, s0, t0, t1, 
             ret_df=True, 
             last_state='none'):
        '''
        
        Parameters
        ----------
        
        last_state : str
            Make last state of trajectory consistent with 'last' terminal event
                - 'none' - do not change trajectory;
                - 'last' - 'last' event is terminal event with greater row index in event states DataFrame;
                - 'mint' - 'last' event is terminal event that occured earlier than other terminal events
        '''
        for e in self.events:
            if hasattr(e, 'reset'):
                e.reset()
        old_solout, old_solout2 = self.model.solout, self.accurate_model.solout
        self.model.solout = self.solout
        df = self.model.prop(s0, t0, t1, ret_df=False)
        evdf = self.accurate(ret_df=False)
        self.model.solout, self.accurate_model.solout = old_solout, old_solout2
        
        # make last state consistent with terminal events
        last_state = last_state.lower()
        if evdf.shape[0] > 0 and last_state != 'none':
            cev, arr = self.split_data(evdf)
            arr_trm = arr[cev[:,2]==1]
            if arr_trm.shape[0] > 0:
                if last_state == 'last':
                    df[-1] = arr_trm[-1]
                elif last_state == 'mint':
                    s = arr_trm[np.argmin(arr_trm[:,0])]
                    df[-1] = s

        if ret_df:
            df = self.model.to_df(df)
            evdf = self.to_df(evdf)            
        return df, evdf
    
    def accurate(self, ret_df=True):
        self.accurate_model.solout = default_solout()
        
        evout = []
        for e in self.solout.evout:
            event = self.events[e[0]]
            if event.accurate:
                ts = self.solout.out[e[2]]
#                print('ts shape:', len(ts))
                t0 = ts[0]
                s0 = ts[1:]
                t1 = self.solout.out[e[2]+1][0]
                sa = self.root(event, t0, t1, s0)
#                print('acc shape:', len(sa))
            else:
                sa = self.solout.out[e[2]]
#                print('not acc shape:', len(sa))
            evout.append([e[0], e[1], event.terminal, *sa])
        
        if ret_df:
            df = self.to_df(evout)
            return df
        return np.array(evout)
        
    def root(self, event, t0, t1, s0):
        s_opt = [0] # for saving calculated state during root calculation

        def froot(t, s0, t0):
            if t == t0:
                s = np.array([t, *s0])
            else:
                s = self.accurate_model.prop(s0, t0, t, ret_df=False)[-1]
            s_opt[0] = s
            res = event(t, s[1:])
#            print(event, t, s[1:], '->', res)
            return res
            
        scipy_root(froot, args=(s0, t0), x0=t0, tol=self.tol)

#       scipy.optimize.solve_ivp uses:
#        brentq(froot, t0, t1, args=(s0, t0), xtol=self.tol, rtol=self.tol)
        return s_opt[0]
    
    def to_df(self, arr, columns=None):#, index_col=None):
#        if index_col is None:
#            index_col = event_detector.columns[0]
        if columns is None:
            columns = event_detector.columns+self.model.columns
        return self.model.to_df(arr, columns)#, index_col)
    
    def split_data(self, data):
        '''
        Splits data by columns: ['e', 'cnt', 'trm'] and ['t', 'x', 'y' ,...]
        '''
        if isinstance(data, pd.DataFrame):
#            d = data.reset_index()
            return data[event_detector.columns], data[self.model.columns]
        n = len(event_detector.columns)
        return data[:,:n], data[:,n:]

class base_event(plottable):
    '''
    Class base_event is a common interface for all event classes in OrbiPy.
    Event stores necessary data and calculates value of event-function which
    it represents. Event detection is a root finding of event-function.
    '''
    coord = 'e'
    
    def __init__(self, 
                 value=0,
                 direction=0,
                 terminal=True,
                 accurate=True,
                 count=-1):
        self.value = value
        self.terminal = terminal
        self.direction=direction
        self.accurate=accurate
        self.count=count
        
    def __call__(self, t, s):
        return 0
    
    def get_df(self):
        return pd.DataFrame({self.coord:self.value}, index=[0])
    
    def plot_df(self, df, ax, projection, **kwargs):
        p = projection.split('-')
        c = self.coord
        kwargs['label'] = self.__repr__()
        if p[0] == c:
            ax.axvline(df[c].values, **kwargs)
        elif p[1] == c:
            ax.axhline(df[c].values, **kwargs)
    
    def __repr__(self):
        return self.__class__.__name__ + \
               ':[val]%r [dir]%r [trm]%r [acc]%r [cnt]%r'%(self.value,
               self.direction, self.terminal, self.accurate, self.count)

class event_combine(base_event):
    '''
    Class event_combine combines list of events in one that looks
    like first event in list but acts like all of them simultaneously.
    This event occur when any of events in list occur.
    '''
    def __init__(self, events):
        if not events:
            raise ValueError('At least one event should be specified')
        self.events = events
            
    def __getattr__(self, attr):
#        print('combine_getattr', attr)
        return getattr(self.events[0], attr)

    def __call__(self, t, s):
        ret = 1.0
        for e in self.events:
            ret *= e(t, s)
        return ret
    
    def __repr__(self):
        return 'event_combine: ' + self.events.__repr__()
    
class event_chain(base_event):
    '''
    Class event_chain looks like last event in chain but works like sequence
    of events: events should occur in specified order and only last event
    will behave like event.
    All events in chain should be terminal!
    '''
    
    def __init__(self, events, autoreset=False):
        if not events:
            raise ValueError('At least one event should be specified')
        self.events = events
        self.autoreset = autoreset
        self.last = len(self.events) - 1
        self.select_event(0)

    def select_event(self, idx):
#        print('event_chain idx:', idx)
        self.idx = idx
        self.event_checker = event_solout([self.events[self.idx]])
            
        
    def reset(self):
        self.select_event(0)
        
    def __getattr__(self, attr):
#        print('chain_getattr', attr)
        return getattr(self.events[self.last], attr)

    def __call__(self, t, s):
        if self.idx == self.last:
            ret = self.events[self.idx](t, s)
            if self.autoreset and \
               self.event_checker(t, s) == -1:
                self.reset()
            return ret
        else:
            if self.event_checker(t, s) == -1:
                self.select_event(self.idx+1) # select next event
             # returning 0 will work because of strict inequalities in
             # event_solout
            return 0.0

    def __repr__(self):
        return 'event_chain: '+self.events.__repr__()

    
class center_event(base_event):
    '''
    Class center_event is a base class for all events that uses
    center (point) in calculations.
    '''
    def __init__(self, 
                 center=np.zeros(3), 
                 value=0, 
                 direction=0, 
                 terminal=True, 
                 accurate=True, 
                 count=-1):
        super().__init__(value, direction, terminal, accurate, count)
        self.center = center
        
    def __repr__(self):
        return super().__repr__() + ' [center]%r'%self.center
        
class model_event(base_event):
    '''
    Class model_event is a base class for all events that uses
    model in calculations.
    '''
    def __init__(self, 
                 model, 
                 value=0, 
                 direction=0, 
                 terminal=True, 
                 accurate=True, 
                 count=-1):
        super().__init__(value, direction, terminal, accurate, count)
        self.model = model

    def __repr__(self):
        return super().__repr__() + ' [model]%r'%self.model
            
class eventT(base_event):
    coord = 't'

    def __call__(self, t, s):
        return t - self.value

class eventSinT(base_event):      
    def __call__(self, t, s):
        return math.sin((t/self.value)*math.pi)

class eventX(base_event):      
    coord = 'x'
    
    def __call__(self, t, s):
        return s[0] - self.value
        
class eventY(base_event):        
    coord = 'y'

    def __call__(self, t, s):
        return s[1] - self.value
    
class eventZ(base_event):
    coord = 'z'

    def __call__(self, t, s):
        return s[2] - self.value
    
class eventVX(base_event):
    coord = 'vx'

    def __call__(self, t, s):
        return s[3] - self.value
    
class eventVY(base_event):
    coord = 'vy'

    def __call__(self, t, s):
        return s[4] - self.value
    
class eventVZ(base_event):
    coord = 'vz'

    def __call__(self, t, s):
        return s[5] - self.value
    
class eventAX(model_event):        
    coord = 'ax'

    def __call__(self, t, s):
        return self.model.right_part(t, s, self.model.constants)[3] - self.value
    
class eventAY(model_event):       
    coord = 'ay'

    def __call__(self, t, s):
        return self.model.right_part(t, s, self.model.constants)[4] - self.value
    
class eventAZ(model_event):
    coord = 'az'

    def __call__(self, t, s):
        return self.model.right_part(t, s, self.model.constants)[5] - self.value

class eventR(center_event):
    splits = 64
    def __call__(self, t, s):
        return ((s[0]-self.center[0])**2+
                (s[1]-self.center[1])**2+
                (s[2]-self.center[2])**2) - self.value**2
                
    def get_df(self):
        alpha = np.linspace(0, 2*np.pi, self.splits)
        c01 = self.center[0]+self.value*np.cos(alpha)
        c10 = self.center[1]+self.value*np.sin(alpha)
        c02 = self.center[0]+self.value*np.cos(alpha)
        c20 = self.center[2]+self.value*np.sin(alpha)
        c12 = self.center[1]+self.value*np.cos(alpha)
        c21 = self.center[2]+self.value*np.sin(alpha)
        z = np.zeros(self.splits, dtype=float)
        return pd.DataFrame({'x':np.hstack((c01,c02,  z)), 
                             'y':np.hstack((c10,  z,c12)),
                             'z':np.hstack((  z,c20,c21))})
    
    def plot_df(self, df, ax, projection, **kwargs):
        p = projection.split('-')
        all_prj = ('x-y', 'x-z', 'y-z')
        for i, prj in enumerate(all_prj):
            if projection in (prj, prj[::-1]):
                s = slice(i*self.splits,(i+1)*self.splits)
                ax.plot(df[p[0]][s].values, 
                        df[p[1]][s].values, **kwargs)
                break


class eventDR(center_event):
    def __call__(self, t, s):
        v = s[3:]   
        r = s[:3] - self.center
        r = r / (r[0]**2+r[1]**2+r[2]**2)**0.5
        return r[0]*v[0]+r[1]*v[1]+r[2]*v[2]

class eventRdotV(center_event):       
    def __call__(self, t, s):
        r = s[:3] - self.center
        v = s[3:6]
        return r[0]*v[0]+r[1]*v[1]+r[2]*v[2]

class eventAlphaX(center_event):
    def __call__(self, t, s):
        return math.atan2(s[1], s[0]-self.center) - self.value

class eventOmegaX(center_event):
    def __call__(self, t, s):
        v = s[3:5]
        r = (s[0]-self.center, s[1])
        omega = (r[0]*v[1]-r[1]*v[0])/(r[0]**2+r[1]**2)
        return omega - self.value
    
class eventConeX(center_event):
    def __call__(self, t, s):
        angle = math.atan2((s[1]**2+s[2]**2)**0.5, s[0]-self.center)
        return angle - self.value

class eventInsidePathXY(center_event):
    def __init__(self, path, center, direction=0, terminal=True, accurate=True, count=-1):
        super().__init__(center, 0, direction, terminal, accurate, count)
        if len(center) < 2:
            raise TypeError('center should be iterable with 2 components (x, y)\n%r'%center)
        self.set_path(path)
        
    def set_path(self, path):
        if not isinstance(path, np.ndarray) or path.ndim < 2:
            raise TypeError('path should be numpy array with 2 dimensions\n%r'%path)
        self.path = path
        theta = np.arctan2(self.path[:,1]-self.center[1],
                           self.path[:,0]-self.center[0])
        order = np.argsort(theta)
        theta = theta[order]
        r = np.sum((self.path-self.center[:2])**2, axis=1)
        r = r[order]
        self.rint = interp1d(theta, r, fill_value='extrapolate', kind='cubic')
        self.theta = theta
        self.r = r
        
    def theta_r(self, t, s):
        x, y = s[0] - self.center[0], s[1] - self.center[1]
        r = x**2 + y**2 + s[2]**2
        theta = math.atan2(y, x)
        return theta, r
        
    def __call__(self, t, s):
        x, y = s[0] - self.center[0], s[1] - self.center[1]
        r = x**2 + y**2 + s[2]**2
        theta = math.atan2(y, x)
        return r - self.rint(theta)  # inside path (event < 0)
    
    def get_df(self):
        return pd.DataFrame({'x':self.path[:,0], 
                             'y':self.path[:,1]})
    
    def plot_df(self, df, ax, projection, **kwargs):
        p = projection.split('-')
        if projection in ('x-y','y-x'):
            ax.plot(df[p[0]].values, 
                    df[p[1]].values, **kwargs)

    
class eventFOV(center_event):
    def __init__(self, 
                 orbit,
                 center, 
                 r, 
                 direction=0, 
                 terminal=True, 
                 accurate=True, 
                 count=-1):
        super().__init__(center, r, direction, terminal, accurate, count)
        self.setOrbit(orbit)

    def setOrbit(self, orbit):
        if not isinstance(orbit, np.ndarray) or orbit.ndim < 2 or orbit.shape[1] < 4:
            raise TypeError('[orbit] should be numpy array of (n, 4) shape: (t,x,y,z)\n%r'%orbit)
        self.orbit = orbit
        self.oint = interp1d(self.orbit[:,0], 
                             self.orbit[:,1:4],
                             axis=0,
                             kind='cubic',
                             fill_value='extrapolate')

    def __call__(self, t, s):
        cone = self.oint(t)[0]
        cone_c = self.center - cone
        cone_s =  s[:3] - cone
#        print(cone_c, cone_s)
#        try:
        d_c = (cone_c[0]**2+cone_c[1]**2+cone_c[2]**2)**0.5
        d_s = (cone_s[0]**2+cone_s[1]**2+cone_s[2]**2)**0.5
        alpha_cone_c = math.atan2(self.value,d_c)
        alpha_cone_s = math.acos(np.dot(cone_c, cone_s)/(d_c*d_s))
#        except:
#            pass
        return alpha_cone_c-alpha_cone_s
        