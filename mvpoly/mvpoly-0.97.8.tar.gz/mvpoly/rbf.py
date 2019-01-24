# coding: utf-8
"""
Hybrid RBF-polynomial interpolation and approximation.
"""

# This code is a derived work from the file of the same name in
# the SciPy library, based closely on Matlab code by Alex Chirokov
# and
#
#   Copyright (c) 2006-2007, Robert Hetland <hetland@tamu.edu>
#   Copyright (c) 2007, John Travers <jtravs@gmail.com>
#
# with some additional alterations by Travis Oliphant.
#
# The modifications from the SciPy file are
#
#   Copyright (c) 2015-2018 J.J. Green <j.j.green@gmx.co.uk>
#
# This code retains the licence as the original: the SciPy (BSD
# style) license: http://www.scipy.org/scipylib/license.html

import math
import numpy as np
import scipy.spatial
import scipy.linalg
import scipy.sparse
import warnings

from mvpoly.cube import MVPolyCube
from mvpoly.dict import MVPolyDict
from mvpoly.util.cached_property import cached_property
from mvpoly.util.version import at_least


class RBFBase(object):
    r"""Base class for radial basis functions

    A class for radial basis function approximation/interpolation of
    `n`-dimensional scattered data.

    Parameters
    ----------
    *args : arrays
        `x`, `y`, `z`, ..., `f`, where `x`, `y`, `z`, ... are the vectors
        of the coordinates of the nodes and `f` is the array of values at
        the nodes
    smooth : float, optional
        Values greater than zero increase the smoothness of the
        approximation.  The default value of zero gives interpolation, i.e.,
        the function will always go through the nodal points.
    poly_order : non-negative integer or `None`, optional (default 1)
        The order of a (low-order) polynomial to be fitted and added to the
        input data; the default of 1 corresponds to a linear term, 0 to a
        constant, `None` for no polynomial part.
    poly_class : one of the :class:`MVPoly` polynomial classes, optional

    Notes
    -----
    The base class is not used directly, instead one uses a subclass for
    which a particular basis function is defined,

    Examples
    --------
    For a set of `n` points in 3-dimensional space with coordinates
    in the `n`-vectors `x`, `y` and `z`; and with `f` being a
    `n`-vector of the data from which to interpolate, the interpolant
    `rbf` is created with

    >>> from mvpoly.rbf import RBFGauss
    >>> x, y, z, f = np.random.rand(4, 50)
    >>> rbf = RBFGauss(x, y, z, f)
    >>> rbf.name
    Gaussian
    """

    @cached_property
    def kdtree(self):
        return scipy.spatial.cKDTree(self.xi.T)

    def _mean_nearest_neighbour(self):
        ds, _ = self.kdtree.query(self.xi.T, k=2)
        return np.mean(ds[:, 1])

    def _poly_matrix(self):
        if self.poly_order is None:
            return None
        if not self.poly_basis:
            self.poly_basis = self.poly_class.monomials(
                self.dim,
                self.poly_order,
                dtype=np.float64
            )
        K = np.vstack(
            list(
                p(*[c for c in self.xi])
                for p in self.poly_basis
            )
        )
        return K

    @property
    def N(self):
        return self.xi.shape[-1]

    @property
    def dim(self):
        return self.xi.shape[0]

    def __init__(self, *args, **kwargs):
        # the data points and the value of the function to be interpolated;
        xi_shape = (len(args) - 1, -1)
        self.xi = np.asarray(args[:-1], dtype=np.float64).reshape(xi_shape)
        self.fi = np.asarray(args[-1]).flatten()

        if not all(x.size == self.fi.size for x in self.xi):
            raise ValueError('All arrays must be equal length')

        # load options specific to subclasses
        self._subclass_options(**kwargs)

        # the smoothing parameter, if zero then the RBF will interpolate,
        # if non-zero then it will approximate.
        self.smooth = kwargs.pop('smooth', 0.0)

        # order of polynomial term ('None' for no polynomial term)
        self.poly_order = kwargs.pop('poly_order', 1)

        # polynomial class
        self.poly_class = kwargs.pop('poly_class', MVPolyDict)

        # polynomial basis (could be user defined without much effort)
        self.poly_basis = None

        # calculate the RBF and polynomial coefficients in the subclasses
        self._subclass_coefficients()

    def __call__(self, *args, **kwargs):
        """Evaluate the interpolant instance

        Parameters
        ----------
        *args : numbers or arrays
            The vectors components `x`, `y`, `z`, ... at which to evaluate
            the interpolant.  All must be the same shape.
        large : Boolean, optional (default `False`)
            Interpolation is performed iteratively rather than in a vectorised
            manner; this saves memory but is slower, use if there are a large
            number of sites on which to interpolate.

        Returns
        -------
        array
            A NumPy array which is the same shape as (each of the) input
            arguments.

        Examples
        --------
        With the interpolant `rbf` as defined in the example above, one
        can evaluate the interpolant at arbitrary points `xi`, `yi`, `zi`
        (in this case on a uniform grid) with

        >>> L = np.linspace(0, 1, 20)
        >>> xi, yi, zi = np.meshgrid(L, L, L)
        >>> fi = rbf(xi, yi, zi, large=False)
        >>> fi.shape
        (20, 20, 20)
        """
        large = kwargs.pop('large', False)
        args = [np.asarray(x, dtype=np.float64) for x in args]
        if not args:
            raise ValueError('Need at least one argument')
        if self.poly is None:
            return self.rbf(*args, large=large)
        else:
            return self.rbf(*args, large=large) + self.poly(*args)


class RBFDense(RBFBase):

    @staticmethod
    def norm(x1, x2):
        return scipy.spatial.distance.cdist(x1.T, x2.T)

    def _rbf_matrix(self):
        A = self.radial(RBFDense.norm(self.xi, self.xi))
        if self.smooth != 0.0:
            eigidx = 0 if self.sign < 0 else self.N - 1
            eig = scipy.linalg.eigh(
                A,
                eigvals_only=True,
                eigvals=(eigidx, eigidx)
            )[0]
            A += np.eye(self.N) * self.smooth * eig
        return A

    def _set_epsilon_default(self):
        self.epsilon = self.epsilon_factor * self._mean_nearest_neighbour()

    def _epsilon_option(self, **kwargs):
        self.epsilon = kwargs.pop('epsilon', None)
        if self.epsilon is None:
            self._set_epsilon_default()

    def _subclass_options(self, **kwargs):
        pass

    def _subclass_coefficients(self):

        A = self._rbf_matrix()
        K = self._poly_matrix()

        if K is None:

            self.rbf_coefs = np.linalg.solve(A, self.fi)
            self.poly = None

        else:

            nk = K.shape[0]
            Z = np.zeros((nk, nk), dtype=np.float64)
            A = np.vstack((np.hstack((A, K.T)), np.hstack((K, Z))))
            f = np.hstack((self.fi, np.zeros((nk,), dtype=np.float64)))
            coefs = np.linalg.solve(A, f)

            # RBF coefficients
            self.rbf_coefs = coefs[:self.N]

            # the polynomial
            poly_coefs = coefs[self.N:]
            self.poly = sum(c * p for c, p in zip(poly_coefs, self.poly_basis))

    def rbf(self, *args, **kwargs):
        large = kwargs.pop('large', False)
        shp = args[0].shape
        if not all(arg.shape == shp for arg in args):
            raise ValueError('Array lengths must be equal')
        x = np.asarray([a.flatten() for a in args], dtype=np.float64)
        if large:
            L = [
                np.dot(
                    self.radial(RBFDense.norm(m[:, np.newaxis], self.xi)),
                    self.rbf_coefs
                )
                for m in x.T
            ]
            return np.asarray(L).reshape(shp)
        else:
            r = RBFDense.norm(x, self.xi)
            return np.dot(self.radial(r), self.rbf_coefs).reshape(shp)


class RBFSparse(RBFBase):

    def _sparse_radial_matrix(self, xtree):
        D = self.kdtree.sparse_distance_matrix(
            xtree,
            self.radius,
            output_type='coo_matrix'
        )
        D.data = self.radial(D.data)
        return D.transpose()

    def _rbf_matrix(self):
        A = self._sparse_radial_matrix(self.kdtree)
        if self.smooth != 0.0:
            if self.sign > 0 :
                which = 'LA'
            else:
                which = 'SA'
            eig = scipy.sparse.linalg.eigsh(
                A,
                k=1,
                which=which,
                maxiter=1000,
                return_eigenvectors=False
            )[0]
            A = A + scipy.sparse.identity(
                self.N,
                format='dok'
            ) * self.smooth * eig
        return A

    def _subclass_coefficients(self):
        A = self._rbf_matrix()
        K = self._poly_matrix()

        # not quite sure what's going on here, if self.fi is complex then
        # we get a complaint that cast to float64 is invalid with 'safe'
        # flag, coercing the sparse matrix A to complex does not help, then
        # we get "Parameter 6 to routine ZTRSV  was incorrect", sometimes
        # "Parameter 2 ...", sometimes just a rubbish solution
        #
        # FIXME: investigate further when the rest of sparse interpolation
        # is working

        if np.iscomplexobj(self.fi):
            msg = 'complex interpolation not available for sparse RBF'
            raise ValueError(msg)

        if K is None:

            self.rbf_coefs = scipy.sparse.linalg.spsolve(A.tocsr(), self.fi)
            self.poly = None

        else:

            nk = K.shape[0]
            K = scipy.sparse.dok_matrix(K)
            Z = scipy.sparse.dok_matrix((nk, nk))
            A = scipy.sparse.vstack(
                (scipy.sparse.hstack((A, K.T)), scipy.sparse.hstack((K, Z)))
            )
            f = np.hstack((self.fi, np.zeros((nk,))))
            coefs = scipy.sparse.linalg.spsolve(A.tocsr(), f)

            # RBF coefficients
            self.rbf_coefs = coefs[:self.N]

            # the polynomial
            poly_coefs = coefs[self.N:]
            self.poly = sum(c * p for c, p in zip(poly_coefs, self.poly_basis))

    def _set_radius_default(self):
        self.radius = math.sqrt(2 * self.dim) * self._mean_nearest_neighbour()

    def _radius_option(self, **kwargs):
        self.radius = kwargs.pop('radius', None)
        if self.radius is None:
            self._set_radius_default()

    def _subclass_options(self, **kwargs):
        self._radius_option(**kwargs)

    def rbf(self, *args, **kwargs):
        if not at_least('scipy', (0, 17, 0)):
            raise NotImplementedError('SciPy 0.17.0 or later required')
        shp = args[0].shape
        if not all(arg.shape == shp for arg in args):
            raise ValueError('Array lengths must be equal')
        x = np.asarray([a.flatten() for a in args], dtype=np.float64)
        xtree = scipy.spatial.cKDTree(x.T)
        D = self._sparse_radial_matrix(xtree)
        D = D.tocsr()
        v = D.dot(self.rbf_coefs).reshape(shp)
        return v


class RBFGaussian(RBFDense):
    r"""An RBF subclass for the *Gaussian* function

    .. math::

        \phi(r) = \exp\left(-(r/\epsilon)^2\right)

    The parameters are as for the base class :class:`RBFBase`, and
    in addition

    Parameters
    ----------
    epsilon : float, optional
        Adjustable constant modifying the shape of the radial function,
        if not specified then a value will be calculated which is
        approximately twice the average distance between adjacent nodes.
    """

    name = 'Gaussian'
    sign = 1
    epsilon_factor = 2.0

    def _subclass_options(self, **kwargs):
        self._epsilon_option(**kwargs)

    def radial(self, r):
        """
        The radial function itself
        """
        return np.exp(-(r / self.epsilon)**2)


class RBFMultiQuadric(RBFDense):
    r"""An RBF subclass for the *multiquadric* function

    .. math::

        \phi(r) = \sqrt{(r/\epsilon)^2 + 1}.

    The parameters are as for the base class :class:`RBFBase`, and
    in addition

    Parameters
    ----------
    epsilon : float, optional
        Adjustable constant modifying the shape of the radial function,
        if not specified then a value will be calculated which is
        approximately the average distance between adjacent nodes.
    """

    name = 'multiquadric'
    sign = -1
    epsilon_factor = 1.0

    def _subclass_options(self, **kwargs):
        self._epsilon_option(**kwargs)

    def radial(self, r):
        """
        The radial function itself
        """
        return np.sqrt((r / self.epsilon)**2 + 1)


class RBFInverseMultiQuadric(RBFDense):
    r"""An RBF subclass for the *inverse multiquadric*

    .. math::

        \phi(r) = \frac{1}{\sqrt{(r/\epsilon)^2 + 1}}.

    The parameters are as for the base class :class:`RBFBase`, and
    in addition

    Parameters
    ----------
    epsilon : float, optional
        Adjustable constant modifying the shape of the radial function,
        if not specified then a value will be calculated which is
        approximately the average distance between adjacent nodes.
    """

    name = 'inverse multiquadric'
    sign = 1
    epsilon_factor = 1.0

    def _subclass_options(self, **kwargs):
        self._epsilon_option(**kwargs)

    def radial(self, r):
        """
        The radial function itself
        """
        return 1.0 / np.sqrt((r / self.epsilon)**2 + 1)


class RBFThinPlateSpline(RBFDense):
    r"""An RBF subclass for the *thin-plate spline*

    .. math::

        \phi(r) = r^2 \log(r).

    The parameters are as for the base class :class:`RBFBase`.
    """

    name = 'thin-plate spline'
    sign = 1
    epsilon_factor = 1.0

    @staticmethod
    def radial(r):
        """
        The radial function itself
        """
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            result = r**2 * np.log(r)
        result[r == 0] = 0
        return result


class RBFWendland(RBFSparse):
    r"""An RBF subclass for the *Wendland* function, a compactly
    supported basis function whose radial is parametersed by the
    optional non-negative integer keyword argument *n*. The form
    of the polynomial depends on *n* and the dimension of the RBF;
    the larger the value of *n*, the smoother the interpolant. As
    an example, the radial function for *n=2* and RBF dimension
    one is

    .. math::

        \phi_{1, 2}(r) \propto (8r^2 + 5r + 1)(1 - r)^5
        \qquad
        (0 \leq r \leq 1)

    The parameters are as for the base class :class:`RBFBase`, and in
    addition

    Parameters
    ----------

    n : integer, optional
        A parameter controlling the order of the radial function,
        and the smoothness of the resulting interpolant (to be
        precise, the latter will be *2n*-times continuously
        differentiable.  If not specified a default value of 2
        will be used.

    radius : float, optional
        A scaling factor for the basis function, the radius of the
        support of the function. If not specified then a value will
        be calculated which is a small factor times the average
        distance between neigbouring nodes.

    Notes
    -----

    This class requires features of SciPy introduced in version 0.17.0,
    earlier versions will cause an error to be raised.

    See also :func:`mvpoly.cube.MVPolyCube.wendland`.
    """

    def __init__(self, *args, **kwargs):
        self.n = kwargs.pop('n', 2)
        super(RBFWendland, self).__init__(*args, **kwargs)

    name = 'Wendland'
    sign = 1

    @cached_property
    def wendland(self):
        return MVPolyCube.wendland(self.dim, self.n)

    def radial(self, r):
        """
        The radial function itself
        """
        r0 = np.where(r < self.radius, r, self.radius)
        return self.wendland(r0 / self.radius)
