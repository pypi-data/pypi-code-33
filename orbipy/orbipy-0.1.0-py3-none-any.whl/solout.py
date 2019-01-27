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
    
