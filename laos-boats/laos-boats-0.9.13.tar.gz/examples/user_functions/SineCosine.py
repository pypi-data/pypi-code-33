import numpy as np
def f(x): # You get x in the format: [[x1, x2, ...]]
    """
    Sinusoidal 1D function (periodic)
    f(x) = sin(2\pi*x) + cos(2\pi*x /1.5), -1.5 < x < 1.5
    Global minimum: f() = 
    This function has two local minima and one global minimum.
    """
    return np.sin(2*np.pi*x[0][0]) + np.cos(2*np.pi*x[0][0]/1.5)
