# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 14:11:11 2019

@author: stasb
"""

from scipy.interpolate import interp1d

class base_extrapolator:
    '''
    Class base_extrapolator is a common interface for all extrapolation
    classes.
    '''
    def __call__(self, arg, history):
        '''
        Calculate extrapolated value at arg using history of states.
        '''
        pass
    
class const_extrapolator(base_extrapolator):
    '''
    Class const_extrapolator returns previous state (last state from history).
    '''
    def __call__(self, arg, history):
        if not history:
            raise RuntimeError('History is empty')
        return history[-1]
    
class linear_extrapolator(base_extrapolator):
    '''
    Class const_extrapolator uses two last states to calculate linear
    extrapolation.
    '''
    def __init__(self, arg_index=0, value_index=1):
        '''
        Constructor
        
        Parameters
        ----------
        arg_index : int
            Index of argument within states stored in history.
            
        value_index : int
            Index of value within states stored in history. This value
            should be extrapolated.
        '''
        self.arg_index = arg_index
        self.value_index = value_index
        
    def __call__(self, arg, history):
        '''
        Calculate extrapolated value.
        
        Parameters
        ----------
        
        arg : float
            Argument where linear extrapolation should be calculated.
            
        history : reference to iterable
            States stored in history will be used for extrapolation.
        
        Returns
        -------
        value : float
            Extrapolated value. Linear extrapolation calculated
            using 2 last states stored in history. If there are
            less than 2 states in history then returns last state.
            
        See also
        --------
        scipy.interpolate.interp1d
        
        '''
        if not history:
            raise RuntimeError('History is empty')
        if len(history) < 2:
            return history[-1][self.value_index]
        intrp = interp1d([history[-2][self.arg_index], history[-1][self.arg_index]], 
                         [history[-2][self.value_index], history[-1][self.value_index]],
                         kind='linear',
                         fill_value='extrapolate')
        return intrp(arg)
    
class quadratic_extrapolator(linear_extrapolator):
    def __init__(self, arg_index=0, value_index=1, default='linear'):
        super().__init__(arg_index, value_index)
        self.default = (1 if default == 'linear' else 0)

    def __call__(self, arg, history):
        '''
        Calculate extrapolated value.
        
        Parameters
        ----------
        
        arg : float
            Argument where quadratic extrapolation should be calculated.
            
        history : reference to iterable
            States stored in history will be used for extrapolation.
        
        Returns
        -------
        value : float
            Extrapolated value. Quadratic extrapolation calculated
            using 3 last states stored in history. If there are
            less than 3 states in history then returns linear
            extrapolation (if default=='linear') or last state (else).
            
        See also
        --------
        scipy.interpolate.interp1d
        
        '''
        if not history:
            raise RuntimeError('History is empty')
        elif len(history) < 3:
            return super().__call__(arg, history)
        
        intrp = interp1d([history[-3][self.arg_index], history[-2][self.arg_index], history[-1][self.arg_index]], 
                         [history[-3][self.value_index], history[-2][self.value_index], history[-1][self.value_index]],
                         kind='quadratic',
                         fill_value='extrapolate')
        return intrp(arg)

class cubic_extrapolator(quadratic_extrapolator):
    def __init__(self, arg_index=0, value_index=1, default='quadratic'):
        super().__init__(arg_index, value_index)
        self.default = (1 if default == 'quadratic' else 0)

    def __call__(self, arg, history):
        if not history:
            raise RuntimeError('History is empty')
        elif len(history) < 4:
            return super().__call__(arg, history)
        
        intrp = interp1d([history[-4][self.arg_index], history[-3][self.arg_index], history[-2][self.arg_index], history[-1][self.arg_index]], 
                         [history[-4][self.value_index], history[-3][self.value_index], history[-2][self.value_index], history[-1][self.value_index]],
                         kind='cubic',
                         fill_value='extrapolate')
        return intrp(arg)
