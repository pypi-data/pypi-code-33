'''
A module for computing a symbolic approximation of \
the set :math:`\mathcal M_e` consisting of all basic sums included in series \
:math:`\lambda` :eq:`lambda` described in :ref:`sect-theory_bs` of online \
documentation.

Available functions:

    - :py:func:`sums_in_Bq`: returns list of multi-indexes of basic sums \
    included in the coefficient :math:`B_q`.
    - :py:func:`sums_in_Gq`: returns list of multi-indexes of basic sums \
    included in the set :math:`G_q`.
    - :py:func:`sums_in_Gq_prime`: returns list of multi-indexes of basic sums \
    included in the set :math:`G_q'`.
    
The :py:func:`sums_in_Bq`, :py:func:`sums_in_Gq`, and :py:func:`sums_in_Bq` \
functions are equipped with methods and algorithms developed in [#Naw2016]_ \
(for the definition of :math:`B_q`, :math:`G_q`, and :math:`G_q'`  sets see \
the paper as well as :ref:`Approximation of Me and symbolic precision \
<sect-theory_Gq_prime>` section of the online documentations).

References:

    .. [#Naw2016] W. Nawalaniec, *Algorithms for computing symbolic \
    representations of basic e–sums and their application to composites*, \
    Journal of Symbolic Computation, Vol. 74, 328-345, 2016.
    
'''

import functools

@functools.lru_cache()
def sums_in_Bq(q):
    '''Return the list of multi-indexes of basic sums included in the \
    coefficient :math:`B_q` of the series :math:`\lambda` :eq:`lambda`. \
    The list is created recursively via :eq:`structure_Me` (see the online \
    :ref:`documentation <sect-theory_Gq_prime>` or [#Naw2016]_ for  \
    more details).

    Parameters:

        q : integer
            An order of basic sums, e.g. passing :math:`q=4` results in \
            returning the following list of multi-indexes: \
            `[(2, 2, 2, 2), (2, 3, 3), (3, 3, 2), (4, 4)]`.

    >>> sums_in_Bq(4)
    [(2, 2, 2, 2), (2, 3, 3), (3, 3, 2), (4, 4)]
    '''
    if q==1:
        return [(2,)]
    if q==2:
        return [(2, 2)]
    prev = sums_in_Bq(q-1)
    return [(2,) + m for m in prev] +\
               [(m[0]+1, m[1]+1) + m[2:] for m  in prev]

def _binary_search(esum, A, a, b):
    '''
    >>> A = [(2, 2, 2, 2), (2, 3, 3), (3, 3, 2), (4, 4)]
    >>> _binary_search((4, 4), A, 0, len(A)-1)
    True
    >>> _binary_search((4, 4), A, 0, len(A)-2)
    False
    >>> _binary_search((5, 5), A, 0, len(A)-1)
    False
    '''
    while a <= b:
        mid = (a+b)//2
        if A[mid] == esum:
            return True
        if esum<A[mid]:
            b = mid-1
        else:
            a = mid+1
    return False

def _reduce_mirror(Bq):
    '''Return the list of multi-indexes of independent basic sums included in\
    :math:`B_q`
    >>> B4 = [(2, 2, 2, 2), (2, 3, 3), (3, 3, 2), (4, 4)]
    >>> _reduce_mirror(B4)
    [(2, 2, 2, 2), (3, 3, 2), (4, 4)]
    '''
    return [s for i,s in enumerate(Bq)
            if not _binary_search(s[::-1], Bq, i+1, len(Bq)-1)]

@functools.lru_cache()            
def sums_in_Gq(q):
    '''Return the list of multi-indexes of independent basic sums included in\
    the coefficient :math:`B_q`. The list is created from :math:`B_q` by\
    reduction of the :ref:`mirror sums<lemma-mirror>` (see the online\
    :ref:`documentation <sect-theory_Gq_prime>` or [#Naw2016]_  for more \
    details).

    Parameters:

        q : integer
            An order of basic sums, e.g. passing :math:`q=4` results in\
            returning the following list of multi-indexes:
            `[(2, 2, 2, 2), (3, 3, 2), (4, 4)]`.
            
    >>> sums_in_Gq(4)
    [(2, 2, 2, 2), (3, 3, 2), (4, 4)]
    '''
    if q==1:
        return [(2,)]
    if q==2:
        return [(2, 2)]
    return _reduce_mirror(sums_in_Bq(q))

def sums_in_Gq_prime(q):
    '''Return the list of multi-indexes of independent basic sums included in\
    the set :math:`G_q'` considered as an approximation of the set \
    :math:`\mathcal M_e` consistsing of indexes of all basic sums included \
    in the series :math:`\lambda` :eq:`lambda` described in \
    :ref:`sect-theory_bs` of online documentation.
    
    Parameters:

        q : integer
            An order of basic sums, e.g. passing :math:`q=4` results in\
            returning the following list of multi-indexes:
            `[(2,), (2, 2), (2, 2, 2), (3, 3), (2, 2, 2, 2), (3, 3, 2), (4, 4)]`.

    >>> sums_in_Gq_prime(4)
    [(2,), (2, 2), (2, 2, 2), (3, 3), (2, 2, 2, 2), (3, 3, 2), (4, 4)]
    '''
    res = []
    for i in range(1, q+1):
        res += sums_in_Gq(i)
    return res

if __name__ =='__main__':
    import doctest
    doctest.testmod()
