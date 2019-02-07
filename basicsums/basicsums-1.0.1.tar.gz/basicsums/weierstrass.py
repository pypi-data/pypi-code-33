
'''
Module for computing values of Weierstrass :math:`\wp` \
and :math:`\wp\'` functions.

Available classes:

    - :py:class:`Weierstrass`: represents functions :math:`\wp` \
    and :math:`\wp\'` for a given halfperiods.

Since the functions :math:`\wp`, :math:`\wp\'` are doubly periodic,  the \
:py:class:`Weierstrass` uses inner helper function in order to bring \
arguments to the base (0,0)th cell. This constitutes in a better convergence.
    
'''

import numpy as np

class Weierstrass:
    '''
    Represents Weierstrass :math:`\wp` function and its derivative for \
    given haflperiods hw1, hw2 (see [#AKHIEZER]_, Table X, p. 204, :ref:`sect-wp_En`
    and :ref:`sect-tutorial`).

    Parameters:

    hw1, hw2 : complex numbers
        Halfperiods of Weierstrass :math:`\wp` function.

    inf : integer (default 20)
        Number of terms of an approximation of the series expansion
        of :math:`\wp`  and :math:`\wp\'` functions
        (see [#AKHIEZER]_, Table X, p. 204 ).

    inf_eta : integer (default 10)
        Number of terms of series approximation of constant :math:`\eta`
        involved in computations (see [#AKHIEZER]_, Table X, p. 204). \
        It was observed that the default value 10 gives good approximations.
        
    References:

    .. [#AKHIEZER] N. I. Akhiezer, *Elements of the Theory of Elliptic Functions*, American Mathematical Society, 1990.
        
    '''
    def __init__(self, hw1, hw2, inf=20, inf_eta=10):
        self.w1 = hw1
        self.w2 = hw2
        self.eta, self.h2k = self._getEtaH2k(self.w1, self.w2,  inf, inf_eta)
        self._tgalpha = np.tan(np.pi/2 - np.angle(2*hw2))
        self._wx = 2*hw1
        self._wy = (2*hw2).imag

    def wp(self, u):
        ''' Return the value :math:`\wp(u)` of the Weierstrass
        :math:`\wp` function for a given complex number :math:`u`.'''
        return self._wp(self._to_cell(u),self.w1, self.w2, self.eta, self.h2k)
    
    def wpp(self, u):
        ''' Return the value :math:`\wp\'(u)` of the derivative of Weierstrass
        :math:`\wp` function for a given complex number :math:`u`.'''
        return self._wpp(self._to_cell(u),self.w1, self.w2, self.eta, self.h2k)
    
    def _getEtaH2k(self, w1, w2, inf, inf_eta):
        tau = w2/w1
        h = np.exp(np.pi * 1j * tau)
        eta = (1/(2*w1) * (np.pi**2)/6 * 
               (1 - 24 * sum(h**(2*k) / (1-h**(2*k))**2
                             for k in range(1, inf_eta+1))))
        h2k = np.array([h**(2*k) for k in range(1, inf+1)])
        return eta, h2k
    
    def _wp(self, u, w1, w2, eta, h2k):
        z = np.exp(np.pi * 1j * u/(2*w1))
        sumK = (h2k * z**-2 / (1 - h2k * z**-2)**2 + 
                h2k * z**2 / (1 - h2k * z**2)**2)
        return -eta/w1 - (np.pi/w1)**2 * (1/(z-z**(-1))**2 + sumK.sum())

    def _wpp(self, u, w1, w2, eta, h2k):
        z = np.exp(np.pi * 1j * u/(2*w1)) 
        sumK = (h2k * (h2k + z**2) / (h2k - z**2)**3 - 
                h2k * (1 + h2k * z**2) / (h2k * z**2 - 1)**3)
        return -(np.pi/w1)**3  * 1j* z * (-(1+z**(-2))/(z-z**(-1))**3
                                          + z * sumK.sum())
    
    def _to_cell(self, z):
        z = z + (self.w1 + self.w2)
        y = z.imag
        x = z.real - y * self._tgalpha
        x = x % self._wx
        y = y % self._wy
        x = x + y * self._tgalpha
        return x + y * 1j - (self.w1 + self.w2)

if __name__ == "__main__":
    import doctest
    doctest.testfile('weierstrass.doctest')
