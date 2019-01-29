'''
A module for computing basic sums. The main part of the :py:mod:`basicsums` \
package.

Available classes:

    - :py:class:`Cell`: represents a two-periodic cell
    - :py:class:`BasicSums`: class of objects tackling computations of \
    basic sums.
                      
The :py:class:`BasicSums` class is equipped with methods and algorithms \
developed in [#NAW2017]_ . Such algorithms are build around products \
of matrices of values of :ref:`Eisenstein functions <sect-wp_En>`.

References:

    .. [#NAW2017] W.Nawalaniec, *Efficient computation of basic sums for \
    random polydispersed composites*, Computational and Applied Mathematics,\
    DOI: 10.1007/s40314-017-0449-6.
    
'''

import numpy as np
from collections import OrderedDict
from basicsums.weierstrass import Weierstrass
from basicsums.eisenstein import eisenstein_funs, lattice_sums


class Cell:
    '''
    Represents a two-priodic unit cell.
    
    For details see :ref:`sect-theory_bs`. An instance stores both lattice \
    sums :math:`S_n` and Eisentein Functions :math:`E_n` corresponding to \
    considered unit cell.

    Parameters:
        
        w1, w2 : complex numbers
            Periods of a unit cell.

        q : integer
            :ref:`Symbolic precision <symb_precision_Bq>` of considerations, \
            i.e. maximal order of Eisenstein functions :math:`E_n` used in \
            computations.

    Attributes:
        
        wp : :py:class:`Weierstrass` class object
            An instance of the :py:class:`Weierstrass` class corresponding
            to considered periodic cell.

        wp2, wpp2 : callable
            Vectorized functions :math:`\wp` and :math:`\wp\'` respectively.

        S : array of floats
            An array of lattice sums :math:`S_n`
            (:math:`n=2, 3, 4, \ldots, \max(q, 6)`) (see :ref:`sect-wp_En`).
            
        eisenstein_funs : dictionary
            Dictionary of Eisenstein functions corresponding to a cell.
            The dictionary contains pairs of the form
            {order :math:`n`: function :math:`E_n`}. Each function is \
            a function of two variables, hence in order to compute value \
            :math:`E_n` for a given :math:`z`, on should pass \
            :math:`\wp(z)` and :math:`\wp\'(z)` as arguments.
    '''
    def __init__(self, w1, w2, q):
        self.wp = Weierstrass(w1/2, w2/2)
        self.wp2 = np.vectorize(self.wp.wp)
        self.wpp2 = np.vectorize(self.wp.wpp)
        self.S = lattice_sums(w1, w2, max(q, 6))
        self.eisenstein_funs = eisenstein_funs(
            max(q, 2), self.S[2], self.S[4], self.S[6])
        self.q = q
        
    def eis_matrices(self, A, eisenstein_indexes):
        '''Return a dictionary of matrices for Eisenstein functions computed
        for a given array of centres :math:`A`.

        Parameters:

            A : NumPy array of complex numbers
                Array of centers of disks.

            eisenstein_indexes : sequence of integers
                A sequence of indexes of Eisenstein Functions required in
                computations. Note that the indexes should not exceed :math:`q`.

        Returns:

            m : dictionary
                The dictionary contains pairs of the form {order :math:`n`:
                NumPy array for a given :math:`E_n`} (see [#NAW2017]_ ).
        '''

        # matrices for $\wp$ and $\wp'$ functions
        wpm = self._wpMatr(A, self.wp2)
        wppm = self._wpMatr(A, self.wpp2, symmetry=-1)

        # generate matrices for Eisentstein functions based on $wp$, $wp'$
        mask = np.eye(len(A), dtype=np.bool)
        m = {}
        for i in eisenstein_indexes:
            m[i] = self.eisenstein_funs[i](wpm,wppm)
            m[i][mask] = self.S[i]
        return m 

    def _wpMatr(self, A, wp, symmetry=1):
        '''Return matrix for function `wp` corresponding to a sample A'''
        nx = len(A)
        matrA = np.zeros(nx**2, dtype=np.complex128).reshape(nx, nx)

        for row in range(nx-1):
            matrA[row][row+1:] = wp(A[row+1:] - A[row])
        matrA = matrA + symmetry * matrA.transpose()
        return matrA

class BasicSums:
    '''
    Represents an object tackling computations of basic sums for a given \
    centers of disks.
    
    Parameters:

        A : NumPy array of complex numbers
            Array of centers of disks.
            
        cell : :py:class:`Cell` object
            An object corresponging to considered cell.

        r : NumPy array of floats (optional)
            Array of radii corresponding to disks. If provided, the centers \
            of A are considered to be the centers of disks of different \
            radii, therwise the equal disks are assumed.

        eisenstein_indexes : sequence of integers (default None)
            A sequence of indexes of Eisenstein Functions required in
            computations. Note that the indexes should not exceed :math:`q`.
            If not provided, the default range is `(2, 3, ..., cell.q)`.

    Attributes:

        eis : dictionary
            A dictionary of matrices computed for Eisenstein functions, based \
            on an array of centers :math:`A`. Matrices are computed for \
            considered indexes of Eisenstein functions.

    Examples:

    >>> w1, w2 = 1, 1j
    >>> cell = Cell(w1, w2, q=3)
    >>> A = np.random.rand(10, 2).dot(np.array([1, 1j]))-(w1+w2)/2
    >>> bso = BasicSums(A, cell)
    >>> e2 = bso.esum(2)
    >>> # Compare the value of e2 with the naive approach:
    >>> from basicsums.eisenstein import E_numeric
    >>> E2 = E_numeric(2, w1, w2)
    >>> e2naive = 1/len(A)**2 * sum(E2(ak0-ak1) for ak0 in A for ak1 in A)
    >>> np.isclose(e2, e2naive)
    True
    '''
    def __init__(self, A, cell, r=None, eisenstein_indexes=None):
        self.A = A
        if r is None or np.all((r-r[0])==0.0): # equal radii -> isclose()
            self.v = None
        else:
            self.v = (r/r.max())**2
        if eisenstein_indexes is None:
            eisenstein_indexes = range(2, max(cell.q + 1, 3))
        self.eis = cell.eis_matrices(A, eisenstein_indexes)
        self._cache = None

    def esum(self, *tup):
        '''Return single basic sum for multi-index given as arguments, e.g.
        :math:`\mathbf{esum}(p_1, p_2,p_3)` computes :math:`e_{p_1, p_2,p_3}`.
        '''

        if self.v is None: # equal radii
            res = np.ones(len(self.A))
            for i,k in enumerate(tup, 1):
                if i%2 == 0:
                    res = np.conjugate(self.eis[k]).dot(res)
                else:
                    res = self.eis[k].dot(res)
            return res.sum() / len(self.A)**(sum(tup)/2 + 1)
        else: # different radii
            tq = tup[0] - 1
            res = (self.v**tq * self.eis[tup[0]].dot(self.v))
            for i,k in enumerate(tup[1:]):
                tq = k - tq
                if i%2 == 0:
                    res = self.v**tq * (np.conjugate(self.eis[k]).dot(res))
                else:
                    res = self.v**tq * (self.eis[k].dot(res))
            return res.sum() / sum(self.v)**(sum(tup)/2 + 1)

    def esums(self, multi_indexes, dict_output=False, maxsize=None,
              cache_only=None, nonlocal_cache=False):
        '''Return basic sums for a given indexes from `multi-indexes`.

        Parameters:

            multi_indexes : sequence
                A sequence of sequences representing multi-indexes, e.g. passing
                following list of tuples `[(2, 2), (3, 3, 2), (4, 4)]` results in
                computing list of sums
                :math:`e_{2, 2}`, :math:`e_{3, 3, 2}`, :math:`e_{4, 4}`.

            dict_output : boolean (default False)
                If `False`, return corresponding values of sums as NumPy \
                array, otherwise as `OrderedDict`, where the tuples are \
                associated with values of basic sums.

            maxsize : integer (default None)
                Determines maximal number of vector representations of \
                intermediate sums cached during computations. By default \
                all intermediate results are cached or only those provided \
                by `cache_only` argument.

            cache_only : sequence (default None)
                A sequence of sequences representing multi-indexes of sums \
                which should only be cached during computations. By default \
                all intermediate results are cached. For more details see \
                :ref:`documentation <sect-memory>`.

            nonlocal_cache : boolean (default False)
                By the default, the cache is built as a local variable hence \
                it exists oly during a function call. If `True`, the cache \
                is maintained as a object's attribute and persists between \
                independent method calls. Takes no effect if nonlocal cache \
                is built already. For more details see \
                :ref:`documentation <sect-memory>`.
        '''
        if self._cache is None:         # there is no nonlocal cache
            res = OrderedDict()
            if nonlocal_cache:          # build a nonlocal cache
                self._cache = res
        else:
            res = self._cache           # use an existing nonlocal cache
        
        required = set() if cache_only is None else set(cache_only)

        def e(tup):
            
            L=len(tup)
                            
            if tup in res:
                return res[tup]

            if self.v is None:
                
                if L==1:
                    t = self.eis[tup[0]].dot(np.ones(len(self.A)))
                else:
                    if L%2==0:
                        t = np.conjugate(self.eis[tup[-1]]).dot(e(tup[:-1]))
                    else:
                        t = self.eis[tup[-1]].dot(e(tup[:-1]))
            else:
            
                if L==1:
                    t = self.v**(tup[0]-1) * (self.eis[tup[0]].dot(self.v))
                else:
                    tq = 1
                    for p in tup:
                        tq = p-tq
                    if L%2==0:
                        t = self.v**tq * (np.conjugate(self.eis[tup[-1]]).dot(e(tup[:-1])))
                    else:
                        t = self.v**tq * (self.eis[tup[-1]].dot(e(tup[:-1])))

            if not required or tup in required:
                res[tup] = t
            if maxsize is not None and len(res) > maxsize:
                res.popitem(last=False)
                
            return t

        # compute and return sums
        
        factor = len(self.A) if self.v is None else sum(self.v)

        # ordered dict output
        if dict_output:
            results = OrderedDict(
                (tup, e(tup).sum()/factor**(sum(tup)/2 + 1)) # pair
                    for tup in multi_indexes)
        # default numpy array output
        else:
            results = np.array([e(tup).sum()/factor**(sum(tup)/2 + 1)
                    for tup in multi_indexes])

        return results

    def clear_cache(self):
        '''Clears the dictionary with cached vector representations of sums.

        It takes effect only if a nonlocal cache is applied, see \
        `nonlocal_cache` argument of :py:func:`esums`.'''
        self._cache = None

if __name__ =='__main__':
    import doctest
    doctest.testmod()
