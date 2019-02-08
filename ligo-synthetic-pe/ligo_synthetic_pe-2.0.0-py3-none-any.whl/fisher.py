class Fisher(object):
    def __init__(
            self,
            x_max, covar, inv_covar,
            n_points=None,
            grid_points=None, grid_lnL=None, lstsq_results=None,
            radius=None, parameter_ranges=None,
            in_domain=None,
            scale_factor=None,
        ):
        import scipy.special

        self.x_max = x_max
        self.covar = covar
        self.inv_covar = inv_covar

        self.radius = radius
        self.parameter_ranges = parameter_ranges
        self.n_points = n_points

        self.grid_points = grid_points
        self.grid_lnL = grid_lnL
        self.lstsq_results = lstsq_results

        self.in_domain = in_domain
        self.scale_factor = scale_factor

        if radius is not None:
            self.n_dim = len(radius)
        elif parameter_ranges is not None:
            self.n_dim = len(parameter_ranges)
        else:
            raise ValueError(
                "Must either provide a value for 'radius' or 'parameter_ranges'"
            )

        # Number of terms is (n_dim+2 choose 2).
        self.n_terms = scipy.special.comb(self.n_dim+2, 2, exact=True)

        try:
            self.distribution = scipy.stats.multivariate_normal(
                self.x_max, self.covar,
            )
            self.converged = True
        except ValueError:
            # Covariance matrix isn't positive semi-definite
            self.distribution = None
            self.converged = False


    def save(self, filename, mode=None, **hdf5_options):
        import h5py

        with h5py.File(filename, mode=mode, **hdf5_options) as f:
            f.create_dataset("x_max", data=self.x_max)
            f.create_dataset("covar", data=self.covar)
            f.create_dataset("inv_covar", data=self.inv_covar)

            if self.radius is not None:
                f.create_dataset("radius", data=self.radius)
            elif self.parameter_ranges is not None:
                f.create_dataset("parameter_ranges", data=self.parameter_ranges)

            if self.scale_factor is not None:
                f.attrs["scale_factor"] = self.scale_factor


    @staticmethod
    def load(filename, **hdf5_options):
        import h5py

        with h5py.File(filename, mode="r", **hdf5_options) as f:
            x_max = f["x_max"].value
            covar = f["covar"].value
            inv_covar = f["inv_covar"].value

            radius = (
                f["radius"].value if "radius" in f else None
            )
            parameter_ranges = (
                f["parameter_ranges"].value if "parameter_ranges" in f else None
            )
            scale_factor = (
                f.attrs["scale_factor"] if "scale_factor" in f.attrs else None
            )

            return Fisher(
                f["x_max"].value,
                f["covar"].value, f["inv_covar"].value,
                radius=radius, parameter_ranges=parameter_ranges,
                scale_factor=scale_factor,
            )


    @staticmethod
    def compute(
            lnL, x_max, n_points,
            radius=None, parameter_ranges=None,
            prior_inv_covar=None,
            above_threshold=None,
            in_domain=None, scale_factor=None,
        ):
        import itertools
        import numpy
        import scipy.stats
        import scipy.special

        if (radius is None) and (parameter_ranges is None):
            raise ValueError(
                "Must either provide a value for 'radius' or 'parameter_ranges'"
            )

        if radius is not None:
            grids_1d = [
                numpy.linspace(xi-ri, xi+ri, ni)
                for xi, ri, ni in zip(x_max, radius, n_points)
            ]
            n_dim = len(radius)
        elif parameter_ranges is not None:
            grids_1d = [
                numpy.linspace(lo, hi, ni)
                for (lo, hi), ni in zip(parameter_ranges, n_points)
            ]
            n_dim = len(parameter_ranges)

        # Number of terms is (n_dim+2 choose 2).
        n_terms = scipy.special.comb(n_dim+2, 2, exact=True)

        grid_points = []
        lnL_values = []

        for x in itertools.product(*grids_1d):
            # Skip if point is outside domain
            if in_domain is not None:
                if not in_domain(x):
                    continue

            lnL_value = lnL(x)
            if above_threshold is not None:
                if lnL_value < above_threshold:
                    continue

            grid_points.append(numpy.subtract(x, x_max))
            lnL_values.append(lnL_value)

        grid_points = numpy.array(grid_points)
        grid_lnL = numpy.asarray(lnL_values)

        n_grid_points = len(grid_points)

        b = grid_lnL

        A = numpy.empty((n_grid_points, n_terms), dtype=numpy.float64)
        # Fill in the constant column.
        A[:,0] = 1.0
        # Fill in the linear columns
        A[:,1:n_dim+1] = grid_points
        # Fill in the product terms
        k = n_dim + 1
        for i in range(n_dim):
            xi = A[:,i+1]
            A[:,k] = numpy.square(xi)
            k += 1
            for j in range(i+1, n_dim):
                xj = A[:,j+1]
                A[:,k] = numpy.multiply(xi, xj)
                k += 1

        coeffs, residuals, rank, singular_values = numpy.linalg.lstsq(A, b)
        lstsq_results = {
            "coeffs" : coeffs,
            "residuals" : residuals,
            "rank" : rank,
            "singular_values" : singular_values,
        }

        inv_covar = numpy.empty(
            (n_dim, n_dim),
            dtype=numpy.float64,
        )
        # Populate the inverse covariance matrix.
        k = n_dim + 1
        for i in range(n_dim):
            # Store the diagonal terms.
            inv_covar[i,i] = -2.0 * coeffs[k]
            k += 1

            # Store the cross-terms.
            for j in range(i+1, n_dim):
                inv_covar[i,j] = inv_covar[j,i] = -coeffs[k]
                k += 1

        if prior_inv_covar is not None:
            inv_covar += prior_inv_covar

        if scale_factor is not None:
            inv_covar *= scale_factor

        covar = numpy.linalg.inv(inv_covar)

        return Fisher(
            x_max, covar, inv_covar,
            n_points,
            grid_points, grid_lnL, lstsq_results,
            radius=radius, parameter_ranges=parameter_ranges,
            in_domain=in_domain,
            scale_factor=scale_factor,
        )


    def sample(self, n_samples, *args, **kwargs):
        return self.distribution.rvs(n_samples, *args, **kwargs)

    def pdf(self, x, *args, **kwargs):
        return self.distribution.pdf(x, *args, **kwargs)

    def logpdf(self, x, *args, **kwargs):
        return self.distribution.logpdf(x, *args, **kwargs)
