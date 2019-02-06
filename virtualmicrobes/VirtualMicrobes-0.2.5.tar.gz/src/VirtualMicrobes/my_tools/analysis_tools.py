'''
Created on Dec 27, 2014

@author: thocu
'''

import itertools as it

def set_differences(sets):
    ''' Returns a measure of difference between sets in a Counter object
    
    From the counter object, the n most frequent sets are extracted. Then,
    between each set and the remaining sets differences are computed and
    expressed as number of differing items for each pair compaired (all pairs
    formed by 'it.combinations'). This number is then scaled to the maximum
    possible difference, which would be the combined number of items in both
    members of a pair.
    
    :param sets: (e.g. produced metabolites in a cell) 
    '''
    if len(sets) <2:
        return [0]
    combinations = list(it.combinations(sets, r=2))
    differences = it.imap(lambda sc: len(frozenset.symmetric_difference(*sc)), combinations )
    max_differences = it.imap(lambda com: sum( map(lambda s: float(len(s)), com) ), combinations)
    scaled_differences = it.starmap( lambda d, m: d/ m if m else 0. , 
                             zip(differences, 
                                 max_differences) ) 
    return list(scaled_differences)
        
        