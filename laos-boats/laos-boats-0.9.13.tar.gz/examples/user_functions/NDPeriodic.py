import numpy as np
def f(x): # You get x in the format: [[x1, x2, ...]]
    """
    N dimensional test function: Periodic correlated function
    f(x) = \prod_{i=1}^d sin[(x_i - 1)*2*pi + 1] + 1, -0.5 < x < 0.5
    Global minimum: f((-0.409,-0.409, ... ,-0.409)) = -1
    This function has a single minimum only.
    """
    prod = 1.
    for i in range(len(x[0])):
        prod *= np.sin((x[0][i]-1)*2*np.pi + 1)
    return prod
