# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 08:27:37 2018

@author: yoelr
"""
from .unit_registry import Quantity
from numpy import asarray

class UnitManager(dict):
    """Create a UnitManager object for handling units of measure of a list of dictionaries (*clients*). When an item in UnitManger changes, all dictionaries in *clients* with the same key change values accordingly.
    
    **Parameters**
    
        **clients:** [list] All dictionaries managed by UnitManager object.
        
        ***args:** Key/units pairs.
        
        ****kwargs:** Key/units pairs.
    
    **Class Attribute**
    
        **Quantity:** `pint Quantity <https://pint.readthedocs.io/en/latest/>`__ class for compatibility.
    
    **Examples**
    
        Convert units of all clients using a UnitManager.
        
            Create client dictionaries:
            
                >>> car = {'weight': 4000, 'velocity': 50}
                >>> plane = {'weight': 175000, 'velocity': 600}
                
            Create a UnitManager object:
                
                >>> um = UnitManager([car, plane], weight='lbs', velocity='mph')
                >>> um
                UnitManager:
                {'weight': 'lbs',
                 'velocity': 'mph'}
                
            Change units of clients:
                
                >>> um['weight'] = 'kg'
                >>> um['velocity'] = 'km/hr'
                >>> car
                {'weight': 1814.36948, 'velocity': 80.46719999999999}
                >>> plane
                {'weight': 79378.66475000001, 'velocity': 965.6063999999999}
                
        Quantity objects are also compatible with UnitManager objects, so long as they are set as the "Quantity" class attribute.
        
            Set "Quantity" attribute:
                
                >>> from pint import UnitRegistry
                >>> ureg = UnitRegistry()
                >>> UnitManager.Quantity = Q_ = ureg.Quantity
                
            Set a Quantity object and change units:
                
                >>> car['weight'] = Q_(4000, 'lb')
                >>> um['weight'] = 'kg'
                >>> car
                {'weight': <Quantity(1814.36948, 'kilogram')>,
                 'velocity': 80.46719999999999>}
            
    
    """
    __slots__ = ('clients',)
    
    Quantity = Quantity 
    
    def __init__(self, clients, *args, **kwargs):
        self.clients = clients
        super().__init__(*args, **kwargs)
    
    def __setitem__(self, key, new_unit):
        """Change units of all clients."""
        Q_ = self.Quantity
        old_unit = self.get(key)
        if old_unit and old_unit != new_unit:
            for client in self.clients:
                old_val = client.get(key)
                if old_val is not None:
                    if isinstance(old_val, Q_):
                        old_val.ito(new_unit)
                    else:
                        old_val = asarray(old_val, float)
                        q = Q_(old_val, old_unit); q.ito(new_unit)
                        client[key] = q.magnitude
        super().__setitem__(key, new_unit)
    
    def __repr__(self):
        Type = type(self).__name__
        if not self: return Type + ': {}'
        out = Type + ': \n{'
        for key, value in self.items():
            out += f"{repr(key)}: {repr(value)},\n "
        return out[:-3] + '}'
