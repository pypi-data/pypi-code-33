import numpy as np
import warnings

from . import sobol_seq

class InitManager:

    def __init__(self, inittype, dim, bounds, initpts):
        """
        Creates initial points which can be queried with the get_x and get_all
        methods. Available types of initial points (parameter inittype) are:
            sobol
            random
            grid
        """
        self.init_data = None
        if inittype.lower() == 'sobol':
            self._sobol(dim, bounds, initpts)
        elif inittype.lower() == 'random':
            self._random(dim, bounds, initpts)
        elif inittype.lower() == 'grid':
            npts = int(np.power(initpts, 1./dim))
            if initpts != npts**dim:
                initpts = npts**dim
                warnings.warn("Grid based initial point creation modifies" \
                        + " initpts so that nth root of it is an integer"\
                        + " , where n in the number of dimensions.")
            self._grid(dim, bounds, npts)
        else:
            raise TypeError("Unknown option set to keyword inittype. "
                            + "Unable to determine initial data.")

    def get_x(self, i):
        """
        Returns the i:th initial point
        """
        return self.init_data[i, :]

    def get_all(self):
        """
        Returns all generated initial points
        """
        return self.init_data

    def _sobol(self, dim, bounds, npts):
        """
        Initial points with the quasi-random Sobol sequence
        """
        self.init_data = np.array([])
        if npts < 1: return ### STOP here if npts < 1
        sobs = np.transpose(sobol_seq.i4_sobol_generate(dim, npts, 1))
        pts = np.array([]).reshape(0, dim)
        for p in range(npts):
            point = np.array([])
            for d in range(dim):
                a = sobs[p,d]*(bounds[d][1]-bounds[d][0]) + bounds[d][0]
                point = np.append(point, a)
            pts = np.append(pts, [point], axis=0)
        self.init_data = pts

    def _random(self, dim, bounds, npts):
        """
        Initial points randomly
        """
        pts = []
        for p in range(npts):
            point = []
            for d in range(dim):
                point.append(
                    np.random.rand()*(bounds[d][1]-bounds[d][0]) + bounds[d][0]
                            )
            pts.append(point)
        self.init_data = np.array(pts).astype(float)

    def _grid(self, dim, bounds, npts):
        """
        Initial points in a grid. Total number of points returned is npts^dim.
        """
        pts = []; coords = bounds[:,0].copy()
        pts.append(coords.copy())
        for i in range((npts**dim) - 1):
            self._change_dim(coords, dim-1, bounds, npts)
            pts.append(coords.copy())
        self.init_data = np.array(pts).astype(float)


    def _change_dim(self, coords, dim, bounds, npts):
        d = (bounds[dim,1]-bounds[dim,0])/(float(npts))
        if abs(coords[dim] - (bounds[dim,1] - d)) < 0.000001:
            coords[dim] = bounds[dim,0]
            if dim > 0:
                self._change_dim(coords, dim-1,bounds,npts)
        else:
            coords[dim] += d

