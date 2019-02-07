import numpy as np
def f(x): # You get x in the format: [[x1, x2, ...]]
    """
    Lennard-Jones function (nonperiodic)
    f(x) = \sum_{i=1}^{dim} e*( (rm/x_i)**12 -2*(rm/x_i)**6 ), 0 < x_i
    Global minimum: f(rm, rm, ... , rm) = -e * dim
    This function has only one minimum.
    """
    e = 2.0; rm = 1.0
    return sum([
                e*( (rm/x[0][i])**12. -2.*(rm/x[0][i])**6. )
                for i in range(len(x[0]))
               ])
