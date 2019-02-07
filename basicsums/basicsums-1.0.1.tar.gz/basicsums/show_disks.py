'''
A module for drawing a sample of a distribution of \
disks in a given two-periodic cell

Available functions:

    - :py:func:`show_disks`: plots an illustration of a system of disks.
    
'''

import numpy as np
import matplotlib.pyplot as plt

def show_disks(disks, r, w1, w2, neighbs=True, figsize=None):
    '''
    Plots a matplotlib figure with an illustration of a set of disks \
    distributed in a two-periodic cell.
    
    Parameters:

        disks : NumPy array of complex numbers
            Array of centres of disks.
            
        r : NumPy array of floats
            Array of radii corresponding to disks.

        w1, w2 : complex numbers
            Periods of the considered cell.

        neighbs : boolean (default True)
            If ``true``, it plots the neighbouring cells with disks.
            Otherwise, only the (0,0)th cell contains disks.
                
        figsize: tuple of integers, optional, default: None
            width, height in inches. If not provided, defaults to
            ``rcParams["figure.figsize"]``
        
    '''
    if figsize is None:
        figsize=plt.rcParams['figure.figsize']
    fig, ax = plt.subplots(figsize=figsize)
    pre_walls = 1.1*(np.array([w1 + w2, w2, 0*w1, w1, w1 + w2]) - (w1 + w2)/2)
    x = np.real(pre_walls)
    y = np.imag(pre_walls)
    ax = plt.axes(xlim=(min(x), max(x)), ylim=(min(y), max(y)))
    plt.plot(x/1.1,y/1.1, 'k')
    ax.set_aspect('equal')
    
    if neighbs:
        B = [0, w1 + w2, w2, w2 - w1, -w1, -w2 - w1, -w2, w1 - w2, w1]
    else:
        B = [0]
        
    for b in B:
        for i, xi in enumerate(disks):
            circle = plt.Circle((0, 0), radius = r[i], ec='0.0', color='0.7')
            c = xi + b
            circle.center = c.real, c.imag
            ax.add_patch(circle)
    plt.show()
