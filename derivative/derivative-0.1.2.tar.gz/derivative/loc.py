import numpy as np

from scipy.special import comb

from .derivative import register


@register()
def finitediff(x, y, **kwargs):
    dx = x[1] - x[0]
    dy = np.zeros_like(x)
    dy[1:-1] = (y[2:] - y[:-2]) / (2.0 * dx)

    dy[0] = (-3.0 / 2 * y[0] + 2 * y[1] - y[2] / 2) / dx
    dy[-1] = (3.0 / 2 * y[-1] - 2 * y[-2] + y[-3] / 2) / dx

    return dy


@register()
def holoborodko(x, y, M=2):
    """

    https://github.com/jslavin/holoborodko_diff

    Implementation of Pavel Holoborodko's method of "Smooth noise-robust
    differentiators" see
    http://www.holoborodko.com/pavel/numerical-methods/numerical-derivative/
    smooth-low-noise-differentiators
    Creates a numerical approximation to the first derivative of a function
    defined by data points.  End point approximations are found from
    approximations of lower order.  Greater smoothing is achieved by using a
    larger value for the order parameter, M.
    Parameters
    ----------
    x : float array or scalar
        abscissa values of function or, if scalar, uniform step size
    y : float array
        ordinate values of function (same length as x if x is an array)
    M : int, optional (default = 2)
        order for the differentiator - will use surrounding 2*M + 1 points in
        creating the approximation to the derivative
    Returns
    -------
    dydx : float array
        numerical derivative of the function of same size as y
    """

    def coeffs(M):
        """
        Generate the "Smooth noise-robust differentiators" as defined in Pavel
        Holoborodko's formula for c_k
        Parameters
        ----------
        M : int
            the order of the differentiator
        c : float array of length M
            coefficents for k = 1 to M
        """
        m = (2 * M - 2) / 2
        k = np.arange(1, M + 1)
        c = 1.0 / 2.0 ** (2 * m + 1) * (comb(2 * m, m - k + 1) - comb(2 * m, m - k - 1))
        return c

    if np.isscalar(x):
        x = x * np.arange(len(y))

    N = 2 * M + 1
    m = (N - 3) / 2
    c = coeffs(M)
    df = np.zeros_like(y)
    nf = len(y)
    fk = np.zeros((M, (nf - 2 * M)))

    for i, cc in enumerate(c):
        # k runs from 1 to M
        k = i + 1
        ill = M - k
        ilr = M + k
        iul = -M - k
        # this formulation is needed for the case the k = M, where the desired
        # index is the last one -- but range must be given as [-2*M:None] to
        # include that last point
        iur = (-M + k) or None
        fk[i, :] = 2.0 * k * cc * (y[ilr:iur] - y[ill:iul]) / (x[ilr:iur] - x[ill:iul])

    df[M:-M] = fk.sum(axis=0)
    # may want to incorporate a variety of methods for getting edge values,
    # e.g. setting them to 0 or just using closest value with M of the ends.
    # For now we recursively calculate values closer to the edge with
    # progressively lower order approximations -- which is in some sense
    # ideal, though maybe not for all cases
    if M > 1:
        dflo = holoborodko(x[: 2 * M], y[: 2 * M], M=M - 1)
        dfhi = holoborodko(x[-2 * M :], y[-2 * M :], M=M - 1)
        df[:M] = dflo[:M]
        df[-M:] = dfhi[-M:]
    else:
        df[0] = (y[1] - y[0]) / (x[1] - x[0])
        df[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
    return df


# from finitediff import interpolate_by_finite_diff as ifd
#
# def finitediff(t, x, order=2, n_points=1, n_fit_ratio=10):
#     """Compute time-derivative of the data matrix X along first axis.
#     Args:
#         t : shape(n_samples)
#         x : array-like, shape (n_samples, n_features)
#             Input variables to be derived.
#     """
#
#     t_fit = np.linspace(t[0], t[-1], num=len(t) * n_fit_ratio, endpoint=True)
#
#     t_fit[0] = t_fit[0] + (t_fit[1] - t_fit[0]) / 2
#     t_fit[-1] = t_fit[-2] + (t_fit[-1] - t_fit[-2]) / 2
#     return ifd(t, x, t_fit, order, n_points, n_points)[::n_fit_ratio, ..., 1:]
