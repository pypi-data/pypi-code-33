'''
A module for computing the effective conductivity of \
random composite materials modelled by non-overlapping disks.

Available functions:

    - :py:func:`coefficient_B`: produces a coefficient :math:`B_q`.
    - :py:func:`effective_conductivity`: produces approximation of the series \
    :math:`\lambda`.

The module is suitable for both symbolic and numeric computations, as well as \
for mixed symbolic-numerical results. For more details on theory, see \
:ref:`sect-theory_bs`.
    
'''

import numpy as np
from sympy import symbols, Function, Symbol
from .multi_indexes import sums_in_Bq
from fractions import Fraction

#rho = symbols('\u03C1')
#rho = symbols('g')
#nus = symbols('\u03BD')
#e = Function('e')
#pi = symbols('\u03C0')

def _indexes_to_sum(t, rho=1, results=None):
    p = list(t)
    c = 1
    for i in range(len(p)-1):
        while p[i]>2:
            #c *= -(p[i+1]-1)/(p[i]-2)
            c *= -Fraction(p[i+1]-1, p[i]-2)
            p[i] -= 1
            p[i+1] -= 1
    if results is None:
        return c * rho**len(p) * Symbol(
            'e('+(','.join(str(pn) for pn in t))+')') #  e(*t)
    try:
        bsum = results[t]
    except KeyError:
        if len(t) % 2 == 0:
            bsum = np.conjugate(results[t[::-1]])
        else:
            bsum = results[t[::-1]]
    return c * rho**len(p) * bsum

def coefficient_B(q, rho, results=None):
    '''
    Return a coefficient :math:`B_q` of series :math:`\lambda`

    Parameters:

        q: integer
            An order :math:`q` of the coefficient :math:`B_q`.

        rho: number or symbol
            Represents constant parameter :math:`\\rho`.

        results: None or a dictionary (default None)
            Dictionary of pairs: tuple representing multi-index with \
            corresponding numerical value of basic sum. \
            The dictionary should provide pairs for every basic sums involved \
            in :math:`B_q`. When the default value is used, basic sums \
            are exoressed symbolically. 
    '''
    return sum(_indexes_to_sum(bsum, rho, results) for bsum in sums_in_Bq(q))

def effective_conductivity(nu, q, rho, results=None, pi=np.pi):
    '''
    Return approximation of the effective conductivity series :math:`\lambda`.

    Parameters:

        nu: number or symbol
            Represents concentration of disks.

        q: integer
            An order :math:`q` of the coefficient :math:`B_q`.

        rho: number or symbol
            Represents constant parameter :math:`\\rho`. \
            Can be given in a symbolic form.

        results: None or dictionary (default None)
            Dictionary of pairs: tuple representing multi-index and \
            the corresponding numerical value of basic sum. \
            The dictionary should provide pairs for every basic sums involved \
            in :math:`B_q`. When the default value is used, basic sums \
            are expressed symbolically.

        pi: number or symbol (default numerical value of :math:`\pi`)
            Represents :math:`\pi`. Can be given in a symbolic form.
    '''
    res = 1 + 2*rho*nu
    for q in range(1, q+1):
        res += 2*rho*nu * coefficient_B(q, rho, results) * nu**q / pi**q
    return res
