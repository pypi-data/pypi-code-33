# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 18:22:53 2018

@author: stasb
"""

class mapper:
    '''
    mapper class is intended for conversion between physical value designation
    (typically presented as DataFrame column name) and categories such as:
    time(T), length(L), velocity(V) and other.
    '''

    columns = ('t', 'x', 'y', 'z', 'vx', 'vy', 'vz')
    indexes = tuple(range(len(columns)))
    categories = ('T', 'L', 'V')
    
    column2category = \
            {'t': 0,
             'x': 1,
             'y': 1,
             'z': 1,
             'vx':2,
             'vy':2,
             'vz':2,
             'dv':2
             }
            
    index2category = dict(enumerate(column2category.values()))    
    column2index = dict(zip(columns, indexes))
    
    def col2cat(column):
        '''
        Convert column (physical value designation) to category.
        
        Parameters
        ----------
        
        column : str
            Column name (physical value designation)
            
        Returns
        -------
        
        category : str
            Corresponding category name
        '''
        cat = mapper.column2category.get(column, None)
#        if cat is None:
#            raise RuntimeError("Can't find category for column name: %s"%column)
        return mapper.categories[cat] if cat is not None else None
    
    def idx2cat(index):
        return mapper.categories[mapper.index2category.get(index, None)]
    
    def col2idx(column):
        return mapper.column2index.get(column, None)
    
    def idx2col(index):
        return mapper.columns[index]