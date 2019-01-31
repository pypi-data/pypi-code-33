# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 23:53:02 2018

@author: stasb
"""

class base_solout:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.out = []
        
    def __call__(t, s):
        return 0
    
class default_solout(base_solout):

    def __call__(self, t, s):
        self.out.append([t, *s])
        return 0
    
class event_solout(base_solout):
    '''
    Class event_solout plays two roles:
        - solout: aggregates all states trough integration process
        - event separation: for each event calculates states right 
            before event occur.
    See also: events.py
    '''
    def __init__(self, events):
        self._events = events
        self.reset()

    @property
    def events(self):
        return self._events
    
    @events.setter
    def events(self, events):
        self._events = events

    def reset(self):
        self.out = []
        self.evout = []
        self.evvals = []
        self.counters = None

    def __call__(self, t, s):
        
        terminal = False           
        cur_evvals = [event(t, s) for event in self._events]
    
        if not self.out:
            if not self.counters:
                self.counters = [event.count for event in self._events]
            self.out.append([t, *s])
            self.evvals.append(cur_evvals)
            return 0
            
        self.out.append([t, *s])
        self.evvals.append(cur_evvals)
    
        for i, event in enumerate(self._events):            
            cur_val = cur_evvals[i]
            prev_val = self.evvals[-2][i]
    
            f1 = (prev_val < 0) and (cur_val > 0) and ((event.direction == 1) or (event.direction == 0))
            f2 = (prev_val > 0) and (cur_val < 0) and ((event.direction == -1) or (event.direction == 0))
            if (f1 or f2) and ((self.counters[i] == -1) or (self.counters[i] > 0)):
                if self.counters[i] > 0:
                    self.counters[i] -= 1
#                print(t)
                self.evout.append([i, # event index
                    (-1 if self.counters[i]==-1 else event.count-self.counters[i]), # event trigger counter
                    len(self.out)-2, # state before event
                    ])
                if event.terminal and ((self.counters[i] == -1) or (self.counters[i] == 0)):
                    terminal = True
                
        if terminal:
            return -1
        
        return 0