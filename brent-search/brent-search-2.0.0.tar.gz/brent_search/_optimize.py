from __future__ import division

from ._bracket import bracket
from ._brent import brent

inf = float("inf")

_eps = 1.4902e-08


def minimize(
    f, x0=None, x1=None, a=-inf, b=+inf, gfactor=2, rtol=_eps, atol=_eps, maxiter=500
):
    r""" Function minimization.

    Applies :func:`brent_search.bracket` to find a bracketing interval, to which
    :func:`brent_search.brent` is subsequently applied to find a local minimum.

    Parameters
    ----------
    f : callable
        Function of interest.
    x0 : float, optional
        First point.
    x1 : float, optional
        Second point.
    a : float, optional
        Interval's lower limit. Defaults to ``-inf``.
    b : float, optional
        Interval's upper limit. Defaults to ``+inf``.
    gfactor : float, optional
        Growing factor.
    rtol : float, optional
        Relative tolerance. Defaults to ``1.4902e-08``.
    atol : float, optional
        Absolute tolerance. Defaults to ``1.4902e-08``.
    maxiter : int, optional
        Maximum number of iterations. Defaults to ``500``.

    Returns
    -------
    float
        Found solution (if any).
    float
        Function evaluation at that point.
    int
        The number of function evaluations.
    """

    def func(x):
        func.nfev += 1
        return f(x)

    func.nfev = 0

    r, _ = bracket(
        func,
        x0=x0,
        x1=x1,
        a=a,
        b=b,
        gfactor=gfactor,
        rtol=rtol,
        atol=atol,
        maxiter=maxiter,
    )

    x0, x1, x2, f0, f1 = r[0], r[1], r[2], r[3], r[4]
    x0, f0 = brent(func, x0, x2, x1, f1, rtol, atol, maxiter)[0:2]
    return x0, f0, func.nfev
