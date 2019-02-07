'''
A module providing simple functions that can be used to prepare data for application \
of basic sums.

Available functions:

    - :py:func:`regularized_radii`: returns abstract radii for a given \
    system of centres (points).
    - :py:func:`normalize_data`: returns scaled data bounded by a unit \
    rectangle.
    - :py:func:`normalize_cell_periods`: returns scaled periods forming \
    unit cell.
    - :py:func:`real_array_to_complex`: returns complex number representation \
    of 2D real coordinates.
    
'''

import numpy as np

def regularized_radii(A, w1, w2):
    '''Returns radii :math:`r` for a given sequence of points :math:`A`.
    The radii :math:`r_j` for a given point :math:`a_j` is computed as
    the half of the minimum of distances from :math:`a_j` to the remaining
    points and the points from neighboring cells (i.e. distance in
    torous topology is considered).

    >>> w1, w2 = 1, 1j # rectangular cell 1x1
    >>> A = np.array([-0.3+0.5j, 0.3+0.5j])
    >>> R = regularized_radii(A, w1, w2)
    >>> np.all(np.isclose(R, np.array([0.2, 0.2])))
    True
    '''
    N = len(A)
    B = np.array([0, w1, w1+w2, w2, -w1+w2, -w1, -w1-w2, -w2, w1-w2])
    r = np.zeros(N)
    for i, ai in enumerate(A):
        imask = np.ones(N, dtype=bool)
        imask[i] =  False
        r[i] = abs(A[imask] + B[:, np.newaxis] - ai).min() / 2
    return r

def normalize_data(data, W=None, H=None, return_factor=None):
    '''Returns scaled data so that the resulting data is bounded by a unit rectangle.

    Parameters:

        data : NumPy array of complex numbers
            Array of centers of disks.
            
        W, H : floats
            Numbers representing, respectively, the width and the height of
            the original box bounding the data. If not provided, they are
            computed based on extremal values of real and imaginary parts of
            data points.

        return_factor: boolean
            If ``true``, returns scale factor as fourth element of resulting
            tuple.

    >>> import numpy as np
    >>> data = 5*np.random.random(100000) + 3j*np.random.random(100000)
    >>> w1, w2, data = normalize_data(data, 5, 3)
    >>> np.isclose(w1*(w2.imag), 1)
    True
    >>> min(data.real) >= -w1/2, max(data.real) <= w1/2
    (True, True)
    >>> min(data.imag) >= -w2.imag/2, max(data.imag) <= w2.imag/2
    (True, True)
    '''
    minx = min(data.real)
    miny = min(data.imag)
    maxx = max(data.real)
    maxy = max(data.imag)
    if W is None or H is None:
        # compute W, H based on the data extremal coordinates
        W = maxx - minx
        H = maxy - miny
        shift = -(minx+miny*1j) - 0.5*(W + H*1j)
    else:
        offsetx = (W - (maxx - minx))/2
        offsety = (H - (maxy - miny))/2
        shift = -( minx-offsetx + (miny-offsety)*1j ) - 0.5*(W + H*1j)
    w1, w2, a = normalize_cell_periods(W, H*1j)
    #print(a)
    if return_factor is None:
        return w1, w2, (data + shift)*a
    return w1, w2, (data + shift)*a, a

def normalize_cell_periods(w1, w2):
    '''Returns scaled periods forming unit parallelogram \
    and the corresponding scale factor ``a``.
    
    Parameters:
        
        w1, w2 : complex numbers
            Periods of considered non-unit cell.

    >>> from cmath import isclose, exp, pi, sqrt
    >>> w1, w2 = 2, 1j # rectangular cell 2x1
    >>> w1, w2, a = normalize_cell_periods(w1, w2)
    >>> area = w1*w2.imag # the area of the parallelogram
    >>> isclose(area, 1)
    True
    >>> w1, w2 = 1, 1*exp(1j*pi/3) # non-unit hexagonal cell
    >>> w1_temp = w1
    >>> w1, w2, a = normalize_cell_periods(w1, w2)
    >>> isclose(w1, sqrt(2)/(3**(1/4)))
    True
    >>> isclose(w2, w1*exp(1j*pi/3))
    True
    >>> isclose(a*w1_temp, w1)
    True
    '''
    a = 1/np.sqrt(w1*w2.imag)
    return a*w1, a*w2, a

def real_array_to_complex(arr):
    '''Returns array of complex numbers of the form :math:`x+iy` being\
    a represantation of real 2D coordinates :math:`(x, y)`

    >>> data = np.array([[-1, 1], [2, -2]])
    >>> real_array_to_complex(data)
    array([-1.+1.j,  2.-2.j])
    '''
    return arr.dot(np.array([1, 1j]))

if __name__ =='__main__':
    import doctest
    doctest.testmod()
