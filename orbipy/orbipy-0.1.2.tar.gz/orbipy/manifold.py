# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 23:07:24 2019

@author: stasb
"""

import numpy as np
import pandas as pd
from itertools import product
from functools import reduce
from .models import base_model
from .directions import base_direction, x_direction
from .events import event_detector

class manifold:
    '''
    Class manifold provides calculation of stable and unstable manifolds 
    for specified unstable orbit (central manifold) near Lagrange points.
    '''
    labels = list(product(['stable', 'unstable'], ['positive', 'negative']))
    shorts = [x[0][0]+x[1][0] for x in labels]
    mapper = dict([(x[1],x[0]) for x in enumerate(shorts)])

#    mapper = {'sp':0, # stable branch with positive disturbance
#              'sn':1, # stable branch with negative disturbance
#              'up':2, # unstable branch with positive disturbance
#              'un':3} # unstable branch with negative disturbance    
    
    columns = ['br','tr']
    
    def __init__(self, model, orbit, tol=1e-12):
        if not isinstance(model, base_model):
            raise TypeError('model should be an instance of base_model')
        self.model = model
        
        ssize = self.model.get_state_size()
#        if isinstance(orbit, pd.DataFrame):
#            sz = orbit.shape[1]
        if orbit.shape[1] < ssize:
            raise ValueError('orbit states should be at least %r size'%ssize)
        self.orbit = orbit
        
        self.tol = tol
        self.reset()
        
    def reset(self):
        self.trajs = None
        self.evout = None
        
    def calc_manifold(self, 
                      disturbance=1e-10,
                      direction=x_direction(),
                      maxt=np.pi,
                      events=[],
                      verbose=True):
        self.reset()
#        if verbose:
#            print('Manifold calculation:')
        for i in range(4):
            self.calc_branch(i,  disturbance, direction, maxt, events, verbose)
        return self.trajs
        
    def calc_branch(self,
                    branch_idx,
                    disturbance=1e-10, 
                    direction=x_direction(), 
                    maxt=np.pi,
                    events=[],
                    verbose=True,
                    last_state='mint',
                    ret_df=True):
        '''
        Calculates manifold branch. Branch defined by disturbance sign and
        direction of propagation: forward or backward.
        Disturbs each state of orbit with specified disturbance in specified
        direction and propagates disturbed state up to maxt time or up to
        events.
        '''
        
        if not isinstance(direction, base_direction):
            raise TypeError('direction should be an instance of base_direction')
        
        if isinstance(branch_idx, str):
            if branch_idx not in self.shorts:
                raise ValueError('branch_idx should be one of: %r'%self.shorts)
            branch_idx = self.mapper[branch_idx]

        disturbance = (-1)**branch_idx*np.abs(disturbance)

        # stable manifold => backward propagation
        # unstable manifold => forward propagation
        maxt = (-1)**(branch_idx//2+1)*np.abs(maxt)

        if verbose:
            print('Manifold branch:', ' '.join(self.labels[branch_idx]), 
                  ', trajectories:', self.orbit.shape[0])

        if isinstance(self.orbit, pd.DataFrame):
            arr = self.orbit.values[:,1:]
        else:
            arr = self.orbit[:,1:]

        detector = event_detector(self.model, events, self.tol)

        tr_lst = []
        ev_lst = []
        for i, s in enumerate(arr):
            s1 = s.copy()
            s1[3:6] += disturbance * direction(0., s1)
            df, ev = detector.prop(s1, 0.0, maxt, ret_df=False, last_state=last_state)
            
            zdf = np.zeros((df.shape[0], 1), dtype=float)            
            df = np.hstack((zdf+branch_idx,zdf+i,df))
            tr_lst.append(df)
            
            if ev.shape[0] > 0:
                zev = np.zeros((ev.shape[0], 1), dtype=float)
                ev = np.hstack((zev+branch_idx,zev+i,ev))           
                ev_lst.append(ev)
                
            print(i, end=' ')
        print()
#        print('Trajectories calculated:', len(tr_lst))
        print('States count:', reduce(lambda a,x: a+x.shape[0], tr_lst, 0))
        
        if self.trajs is None:
            self.trajs = np.vstack(tuple(tr_lst))
        else:
            self.trajs = np.vstack((self.trajs,*tr_lst))
        
        if len(ev_lst) > 0:
            if self.evout is None:
                self.evout = np.vstack(tuple(ev_lst))
            else:
                self.evout = np.vstack((self.evout,*ev_lst))
            
        if ret_df:
            self.trajs = self.to_df(self.trajs)
            if len(ev_lst) > 0:
                self.evout = self.to_df(self.evout,
                                        columns=manifold.columns+
                                                detector.columns+
                                                detector.model.columns)
        return self.trajs, self.evout
    
    def to_df(self, arr, columns=None):#, index_col=None):
#        if index_col is None:
#            index_col = manifold.columns[0]
        if columns is None:
            columns = manifold.columns+self.model.columns
        return self.model.to_df(arr, columns)#, index_col)
    
    def split_data(self, data):
        '''
        Splits data by columns: ['br', 'tr'] and ['t', 'x', 'y' ,...]
        '''
        if isinstance(data, pd.DataFrame):
#            d = data.reset_index()
            return data[manifold.columns], data[self.model.columns]
        n = len(manifold.columns)
        return data[:,:n], data[:,n:]
        

