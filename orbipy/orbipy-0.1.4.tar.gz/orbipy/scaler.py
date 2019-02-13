# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 19:49:32 2018

@author: stasb
"""

#import numpy as np
import pandas as pd
from itertools import product
from .models import nondimensional_model
from .mapper import mapper

default_units_mapper = \
         {'T': { 's':1.,
                 'm':60.,
                 'h':60*60.,
                 'd':24*60*60.,
                 'w':7*24*60*60.,
                 'M':30*24*60*60.,
                 'Y':365*24*60*60.
               },

          'L': { 'mm':1e-6,
                 'cm':1e-5, 
                 'm' :1e-3,
                 'km':1.,
                 'Mm':1e3,
                 'Gm':1e6,
                 'au':149597870.700}
          }
          
class scaler:
    '''
    Class scaler is intended for conversion between physical units of several
    categories such as: time, length, velocity and other.
    By default it uses default_units_mapper defined in scaler.py module.
    '''
    def __init__(self, 
                 time_units=('s','s'),
                 length_units=('km','km'),
                 velocity_units=('km/s','km/s'),
                 units_mapper=default_units_mapper.copy()):
        '''
        Initializes scaler instance using specified mapper and units.
        
        Parameters
        ----------
        time_units, length_units, velocity_units : tuple(str, str)
            Default units used for data conversion in convert_data method by default.
            
        units_mapper : dict(str, dict(str, float))
            Mapping dict for each category and unit in category consists of
            coefficients used to convert values between physical units.
        
        Example
        -------
        import orbipy as op
        import numpy as np
        
        scale = op.scaler()
        
        # convert 10 mm to cm
        print(scale(10,'mm-cm'), 'cm')
        
        # convert 0,10,...,90 seconds to minutes
        print(*scale(np.arange(10)*10, 's-m'), sep=' m\n', end=' m\n')
        
        model = op.crtbp3_model()
        scale = op.scaler.from_model(model)
        
        # convert 2*pi nondimensional time units to days
        # for Sun-Earth system (365.0)
        print(scale(2*np.pi,'nd-d'))
        
        See also
        --------
        default_units_mapper from scaler module.
        
        '''
        self.units_mapper = units_mapper
        v_keys = ['%s/%s'%(l,t) for l, t in product(self.units_mapper['L'].keys(),  self.units_mapper['T'].keys())]
        v_vals = [          l/t for l, t in product(self.units_mapper['L'].values(),self.units_mapper['T'].values())]
        self.units_mapper['V'] = dict(zip(v_keys,v_vals))
        self.units = dict(zip(mapper.categories, (time_units, length_units, velocity_units)))
        for cat in self.units:
            if self.get_category(self.units[cat][0], self.units[cat][1]) is None:
                raise ValueError("Can't convert [%s] to [%s] units from [%s] category"%(*self.units[cat], cat))
    
    def get_category(self, from_units, to_units):
        '''
        Tries to get category of units which contains both: from_units and to_units.
        
        Parameters
        ----------
        from_units, to_units : str
            Physical units, like 'm', 'km/s', 'd', 'nd'.

        Return
        ------
        category : str or None
            Category of units (key from units_mapper dict) if both of specified units
            can be located in such category. None, otherwise.
        '''
        for c in self.units_mapper:
            if (from_units in self.units_mapper[c]) and (to_units in self.units_mapper[c]):
                return c
        return None
    
    @classmethod
    def from_model(cls, model,
                   time_units=('nd','d'),
                   length_units=('nd','km'),
                   velocity_units=('nd/nd','km/s'),
                   nondim='nd'):
        '''
        Constructor from_model initializes scaler class instance with additional
        nondimensional units gathered from model.
        
        Parameters
        ----------
        model : nondimensional_model instance
            Model from which nondimensional coefficients will be used.
            
        nondim : str
            Symbol for nondimensional units.
            
        rest : parameters
            See __init__.
        '''
        if not isinstance(model, nondimensional_model):
            raise TypeError('Only nondimensional models supported')
        umapper = default_units_mapper.copy()
        nd_coefs = model.get_nd_coefs()
        umapper['T'][nondim] = nd_coefs['T']
        umapper['L'][nondim] = nd_coefs['L']
        return cls(time_units, length_units, velocity_units, units_mapper=umapper)
        
    def get_coef(self, from_units='km', to_units='m'):
        '''
        Calculate conversion coefficient to convert value from from_units to to_units.
        
        Parameters
        ----------
        from_units, to_units : str
            Physical units, like 'm', 'km/s', 'd', 'nd'.
            
        Return
        ------
        coef : float
            Conversion coefficient.
        '''
        category = self.get_category(from_units, to_units)
        if not category:
            raise ValueError("Can't convert [%s] to [%s]"%(from_units, to_units))
        cat = self.units_mapper[category]
        return cat[from_units] / cat[to_units]
    
    def convert(self, value, from_units='km', to_units='m'):
        '''
        Converts value from from_units to to_units.
        
        Parameters
        ----------
        value : float
            Value specified in from_units physical units.
            
        from_units, to_units : str
            Physical units, like 'm', 'km/s', 'd', 'nd'.
            
        Return
        ------
        new_value : float
            Converted value.        
        '''
        return value * self.get_coef(from_units, to_units)
    
    def __call__(self, value, from_to='km-m'):
        '''
        Converts value from one physical units to another.
        Short version of convert method.
        
        Parameters
        ----------
        
        from_to : str
            Physical units for convertation in format: 'unit_from-unit_to'.
        '''
        return value * self.get_coef(*from_to.split('-'))
    
    def convert_data(self, data,
                     time_units=None,
                     length_units=None,
                     velocity_units=None):
        '''
        Converts data using specified or default units.
        
        Parameters
        ----------
        data : numpy.ndarray or pandas.DataFrame
            Data consists of columns that intended for conversion according to
            specified units.
            
        time_units, length_units, velocity_units : tuple(str, str)
            Units used for columns conversion. Each column corresponds to
            category of units (time, length, velocity) and will be converted
            from category_units[0] to category_units[1]. If specified units is
            None then default units will be used (self.units).
            
        Return
        ------
        new_data : same type as data
            Converted data.      
        '''
        if time_units is None:
            time_units = self.units['T']
        if length_units is None:
            length_units = self.units['L']
        if velocity_units is None:
            velocity_units = self.units['V']
        units = dict(zip(mapper.categories, (time_units, length_units, velocity_units)))
        df = data.copy()
        if isinstance(data, pd.DataFrame):
            for col in df.columns:
                cat = mapper.col2cat(col)
                if cat is not None:
                    u = units[cat]
                    df[col] = self.convert(df[col], from_units=u[0], to_units=u[1])
#            df.index = self.convert(df.index,
#                                    from_units=time_units[0],
#                                    to_units=time_units[1])
        else:
            for i in range(df.shape[1]):
                if i in mapper.indexes:
                    u = units[mapper.idx2cat(i)]
                    df[:,i] = self.convert(df[:,i], from_units=u[0], to_units=u[1])
            
        return df

