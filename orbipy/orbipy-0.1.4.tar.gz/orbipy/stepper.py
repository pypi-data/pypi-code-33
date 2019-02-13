# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 00:39:18 2018

@author: stasb
"""
    
class iteration_printer:
    def __init__(self, idx=0, show_iter=True, sep=' '):
        self.idx = idx
        self.show_iter = show_iter
        self.sep = sep
        
    def __call__(self, i, count, arg):
        if self.show_iter:
            print('[%r/%r]'%(i, count), end=self.sep)
        if hasattr(self.idx, '__iter__'):
            print(*[arg[j] for j in self.idx], sep=self.sep)
        else:
            print(arg[self.idx])

class stepper:
    '''
    Stepper class is intended as convenient object-oriented analog of
    for loop. For each iteration (a.k.a. step) it calls user function
    func ('loop body') and passes to it current argument from specified
    range and reference to history where all previous steps are stored.
    '''
    def __init__(self, func, initial, args=(), prnt=iteration_printer()):
#        if not isinstance(func, base_func):
#            raise TypeError("Func should be an instance inheritor of base_func")
        self.func = func
        self.args = args
        self.prnt = prnt
        self.reset()
        if hasattr(initial, '__iter__'):
            for s in initial:
                self.history.append(s)
        else:
            self.history.append(initial)
    
    def reset(self):
        self.history = []
            
    def next_step(self, i):
        state = self.func(i, self.history, *self.args)
        if state is None:
            return False
        self.history.append(state)
        return True
    
    def make_steps(self, steps=100, verbose=True):
        if isinstance(steps, slice):
            r = range(steps.start, steps.stop, steps.step)
        elif hasattr(steps, '__iter__'):
            r = steps
        elif steps > 0:
            r = range(0, steps, 1)
        elif steps < 0:
            r = range(0, steps, -1)
        count = len(r)
        for idx, i in enumerate(r):
            if self.next_step(i):
                if verbose:
                    self.prnt(idx, count, self.history[-1])
#                    print('[%r/%r]'%(idx,count), '%r'%i, self.history[-1])
            else:
                if verbose:
                    print('Iteration stopped by function')
                break
#        if verbose:
#            print()
        return self
