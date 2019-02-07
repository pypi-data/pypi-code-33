'''
A module for computing symbolic forms and numerical values of the Eisenstein \
functions :math:`E_n` and the Eisenstein lattice sums :math:`S_n`.

Available functions:

    - :py:func:`E`: computes a symbolic representation of Eisenstein \
    function :math:`E_n`.
    - :py:func:`E_numeric`: produces the Eisenstein function :math:`E_n` \
    suitable for numerical computations.
    - :py:func:`lattice_sums`: returns an array of lattice sums :math:`S_n`.
    - :py:func:`eisenstein_funs`: returns a dictionary of Eisenstein functions.

The definition of the Eisenstein functions :math:`E_n` is built on the \
Weierstrass :math:`\wp` function and its derivative.
For more details on theory, see :ref:`sect-theory_lattice_sums` and \
:ref:`sect-wp_En`.
    
'''

from math import factorial
from fractions import Fraction
import numpy as np
from sympy import Symbol, Function, lambdify

#from .weierstrass import Weierstrass
from basicsums.weierstrass import Weierstrass

P  = Function('P')   # Weierstrass P symbol
Pp = Function("P'")  # Weierstrass P prime symbol
S  = Function('S')   # Eisenstein lattice sum symbol
z  = Symbol('z')     # complex argument symbol


def E(n):
    '''Compute a symbolic representation of Eisenstein function of order \
    :math:`n`.

    The function requires the :py:mod:`sympy` package in order to perform \
    symbolic manipulations. For numerical calculations use \
    :py:func:`E_numeric` instead.

    Parameters:

        n : integer (:math:`n \geq 2`)
            The order :math:`n` of the Eisenstein function :math:`E_n`.
    '''
    rule1 = P(z).diff(z, 2), 6*P(z)**2 - 30 * S(4)
    rule2 = P(z).diff(z), Pp(z)
    derivatives = {1: P(z).diff(z)}
    
    def der(n):
        nonlocal derivatives
        if n not in derivatives:
            derivatives[n] = der(n-1).diff(z).subs([rule1])
        return derivatives[n]
    
    if n == 2:
        result = P(z) + S(2)
    else:
        result = ( Fraction((-1)**n, factorial(n-1))
                   * der(n-2).subs([rule2]) )
    return result.factor()

def E_numeric(n, w1, w2):
    '''Return numeric Eisenstein function :math:`E_n` for a given periods \
    `w1`, `w2`.

    0ne can directly compute the value :math:`E_n`(z) for a givrn :math:`z`.
    
    Parameters:

        n : integer (:math:`n \geq 2`)
            The order :math:`n` of the Eisenstein function :math:`E_n`.
        w1, w2 : complex numbers
            The periods of Eisenstein function :math:`E_n`.

    Examples:
    
    >>> E2 = E_numeric(2, 1, 1j) # square unit cell
    >>> np.isclose(E2(0), np.pi)
    True
    '''
    
    wp = Weierstrass(w1/2, w2/2)
    S = lattice_sums(w1, w2, n)
    fun = _eisenstein_fun(E(n), S[2], S[4], S[6])

    S = lattice_sums(w1, w2, n, inf=100)

    
    
    return lambda z: S[n] if np.isclose(z, 0) else fun(wp.wp(z), wp.wpp(z))

def lattice_sums(w1, w2, qmax, inf=100):
    '''Return an array of Eisenstein_Rayleigh lattice sums :math:`S_n` \
    up to :math:`S_{qmax}`.

    Parameters:

        w1, w2 : complex numbers
            The periods of Eisenstein function :math:`E_n`.
            
        qmax : integer
            Maximal order of considered sums.

        inf : integer (default 100)
            Number of terms of partial sums approximating infinite sums \
            :math:`S_n`, see :ref:`sect-theory_lattice_sums`.
    '''
    tau = w2/w1
    q = np.exp(np.pi * 1j * tau)

    S = np.zeros(max(qmax+1, 7), dtype=np.complex128)
    S2sum = sum(np.array([(m*q**(2*m))/(1 - q**(2*m)) 
                         for m in range(1, inf + 1)]))
    gx2 = sum(np.array([(m**3*q**(2*m))/(1-q**(2*m)) 
                        for m in range(1, inf + 1)]))
    gx3 = sum(np.array([(m**5*q**(2*m))/(1-q**(2*m)) 
                        for m in range(1, inf + 1)]))
    g2 = (np.pi/w1)**4 * (4/3 + 320 * gx2)
    g3 = (np.pi/w1)**6 * (8/27 - 448/3 * gx3)
    
    S[2] = (np.pi/w1)**2 * (1/3 - 8 * S2sum)

    S[4] = g2 / 60
    S[6] = g3 / 140
    for k in range(4, int(qmax/2) +1):
        sx = sum(np.array([(2*n-1) * (2*k-2*n-1) * S[2*n] * S[2*k-2*n]
                           for n in range(2, k-1)]))#k-2
        S[2*k] = 3/((2*k+1)*(2*k-1)*(k-3)) * sx

    return np.real(S)

def _eisenstein_fun(Efun, S2, S4, S6):
    fun = lambdify((P(z), Pp(z)),
                   Efun.subs({S(2): S2, S(4): S4, S(6): S6}), "numpy")
    return fun

def eisenstein_funs(nmax, S2, S4, S6):
    '''Return a dictionary with first `nmax` vectorized Eisenstein functions. \
    The procedure is used by objects of :py:mod:`basic_sums` \
    module.

    The dictionary contains pairs of the form
    {order :math:`n`: function :math:`E_n`}. Each function is \
    a function of two variables, hence in order to compute value \
    :math:`E_n` for a given :math:`z`, one should pass, respectively, \
    :math:`\wp(z)` and :math:`\wp\'(z)` as arguments.

    Parameters:

        nmax : integer
            Maximal value of the order of considered Eisenstein functions \
            :math:`E_n`.

        S2, S4, S6 : real numbers
            The Eisenstein lattice sums for a given periodic cell. The sums \
            can be calculated via :py:func:`lattice_sums` function.
             
    '''
    return {k: _eisenstein_fun(E(k), S2, S4, S6) for k in range(2, nmax+1)}

if __name__ =='__main__':
    import doctest
    doctest.testmod()
