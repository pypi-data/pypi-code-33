'''
Created on Nov 14, 2013

@author: thocu
'''

#TODO: make an efficient deepcopy override function

from collections import Counter

def increment(x):
        return x+1

class Identifier(object):
    
    __slots__ = ['offspring_count', 'versioned_id','increment_func']
    unique_unit_dict = Counter() #FIXME: this one is not pickled and so counting restarts upon reload
    
    def __init__(self,obj, versioned_id=1, increment_func=None):
        if increment_func is None:
            increment_func = increment
        self.count_class_types(obj)
        self.parse(versioned_id)
        self.increment_func = increment_func
        self.offspring_count=0
     
    @classmethod
    def count_class_types(cls,obj):
        cls.unique_unit_dict[type(obj)] += 1 
    
    @property
    def major_id(self):    
        """
        Return the first part (highest order) of identifier.
        
        Returns
        -------
        int (or other id format)
        """
        return self.versioned_id[0]
    
    @property
    def minor_id(self):
        """
        Return version part of the identifier.
        
        Returns
        -------
        list of int (or other id format)
        """
        return self.versioned_id[1:] if len(self.versioned_id) else []
    
    def is_copy(self, identifier):
        """
        Test if identifier and self are different copies of the same
        major_id. 
        
        identifier : `Identifier`
            Identifier to compare to.
            
        Returns
        -------
        bool
        """
        return identifier.major_id == self.major_id
        
    def clear_offspring(self):    
        self.offspring_count = 0
        
    def increment_offspring(self):
        self.offspring_count = self.increment_func(self.offspring_count)
        
    def parse(self,versioned_id):
        try:
            if type(versioned_id) is list:
                self.versioned_id = [int(v) for v in versioned_id]
            else:
                self.versioned_id = [ int(i) for i in  str(versioned_id).split(".") ]
        except ValueError:
                print "invalid versioned_id initialization", versioned_id
                raise   
        return self.versioned_id
    
    def from_parent(self, parent, flat=True, pos=-1):
        """
        Set an Identifier from a parent id. 
        
        If id is incremented in a 'flat' way, the new id is the unique count of
        objects of the (parent) type that this id belongs to. Else, the id increment
        is done in a 'versioned' manner. If parent has 0 offspring ids so far, the parent
        id is simply copied and no increment is done. If parent already has > 0 offspring ids, 
        then a version element is added that indicates this id as the "n'th" offspring of the 
        parent id. E.g. if parent id is 2.3 and it has 2 offspring already: 
        from_parent(parent, flat=False) -> 2.3.2  
        
        Parameters
        ----------
        parent : object with an `Identifier` attribute
            The parent of this Identifier.
        flat : bool
            If True, set versioned id position as the total number of counted
            objects of a the type of `parent`. Else, add versioned id
            information.
        pos : int (index)
            index of the version bit to update
        """
        
        """Increments the count of objects of a specific type"""
        self.count_class_types(parent) 
        
        if flat:
            self.versioned_id[pos] = self.unique_unit_dict[type(parent)]
        elif parent.id.offspring_count > 0:
            self.versioned_id.append(parent.id.offspring_count)
        parent.id.increment_offspring()
        self.clear_offspring()
                
    def __str__(self):
        return ".".join([str(v) for v in self.versioned_id])
        