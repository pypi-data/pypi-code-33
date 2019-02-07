import warnings; warnings.filterwarnings("ignore") # ignore warnings
import numpy as np
import copy
import scipy.optimize
from scipy.spatial.distance import euclidean
from operator import itemgetter

from . import sobol_seq

class Minimization:
    """
    Minimization utilities
    """
    @staticmethod
    def _run_minimizer(func, x0, bounds, args, finite_grads=False):
        """
        Runs a single L-BFGS-B minimization starting from x0
        """
        if finite_grads:
            x,f,d = scipy.optimize.fmin_l_bfgs_b(
                                      func, x0, bounds=bounds, args=args,
                                      factr=1e8, pgtol=1e-4, maxfun=1e4,
                                      maxiter=1e4, maxls=15, approx_grad=True)
            return x, f, d['warnflag']==0

        else:
            x,f,d = scipy.optimize.fmin_l_bfgs_b(
                                      func, x0, bounds=bounds, args=args,
                                      factr=1e8, pgtol=1e-4, maxfun=1e4,
                                      maxiter=1e4, maxls=15)
            return x, f, d['warnflag']==0

    @staticmethod
    def minimize(func, bounds, kerntype, acqs, min_dist_acqs, accuracy=0.3,
                 args=(), lowest_min_only=True):
        """
        Tries to find global minimum of func by starting minimizers from
        accuracy*100 percentage of lowest acquisitions. func has to return both
        value and gradient given an x of same length as bounds.
        """
        acqsx = np.array(copy.deepcopy(acqs[:,:len(bounds)]))
        acqsy = np.array(copy.deepcopy(acqs[:,-1:]))

        points = []
        for i in range(len(acqsy)):
            points.append([list(acqsx[i]), float(acqsy[i])])

        points = Minimization._remove_duplicates(points, min_dist_acqs)
        points = sorted(points, key=itemgetter(1))
        X, Y = zip(*points)
        ind_last = min(len(Y)-1, max(0, round(accuracy*(len(Y)-1))))
        X = X[:ind_last+1]
        X = np.array([X[i] for i in range(len(X))])

        widebounds = bounds.copy()
        p = np.array(kerntype)=='stdp'
        l = bounds[:,1] - bounds[:,0]
        widebounds[p, 0] -= 0.1 * l[p]
        widebounds[p, 1] += 0.1 * l[p]

        minima = []
        for acq in X:
            # Run bounded minimization on bounds which have been stretched for
            # periodic dimensions, then return the minima which have been found
            # inside the bounds. This prevents minima from being falsely
            # identified at the periodic boundaries.
            x, f, s = Minimization._run_minimizer(func, acq, widebounds, args)
            if s and np.all((bounds[p, 0] <= x[p]) & (x[p] <= bounds[p, 1])):
                minima.append([list(x), float(f)])

        if len(minima) == 0:
            lo_acq = [list(acqsx[np.argmin(acqsy)]), float(np.min(acqsy))]
            minima.append(lo_acq)

        if lowest_min_only:
            globalmin = minima[0]
            for minimum in minima:
                if minimum[1] < globalmin[1]:
                    globalmin = minimum
            return globalmin
        else:
            minima = Minimization._remove_duplicates(minima, min_dist_acqs)
            return minima

    @staticmethod
    def minimize_from_sobol(func, bounds, num_pts, shift, args=(),
                 lowest_min_only=True):
        """
        Tries to find global minimum of func by starting minimizers from
        num_pts shifted sobol points. func has to return both
        value and gradient given an x of same length as bounds.
        """
        sobs = np.transpose(
            sobol_seq.i4_sobol_generate(len(bounds), num_pts, 1))

        points = []
        for i in range(len(sobs)):
            p = []
            for n in range(len(bounds)):
                bl = bounds[n][1] - bounds[n][0]
                p.append(bounds[n][0] + (sobs[i,n]*bl + shift[n]) % bl)
            points.append(p)

        minima = []
        for pnt in points:
            x, f, s = Minimization._run_minimizer(func, pnt, bounds, args)
            if s:
                minima.append([list(x), float(f)])
        if len(minima) == 0:
            err_min = [list(points[-1]),
                       float(func(points[-1], args[0], args[1])[0])]
            minima.append(err_min) # later a better solution here?

        if lowest_min_only:
            globalmin = minima[0]
            for minimum in minima:
                if minimum[1] < globalmin[1]:
                    globalmin = minimum
            return globalmin
        else:
            return minima
    
    @staticmethod
    def minimize_from_random(func, bounds, num_pts, shift, args=(),
                 lowest_min_only=True):
        """
        Tries to find global minimum of func by starting minimizers from
        num_pts random points (min 10 max 100). func has to return both
        value and gradient given an x of same length as bounds.
        """
        if num_pts < 10: num_pts = 10
        elif num_pts > 100: num_pts = 100

        rands = np.random.random([num_pts, len(bounds)])

        points = []
        for i in range(len(rands)):
            p = []
            for n in range(len(bounds)):
                bl = bounds[n][1] - bounds[n][0]
                p.append(bounds[n][0] + rands[i,n]*bl)
            points.append(p)

        minima = []
        for pnt in points:
            x, f, s = Minimization._run_minimizer(func, pnt, bounds, args)
            if s:
                minima.append([list(x), float(f)])
        if len(minima) == 0:
            err_min = [list(points[-1]),
                       float(func(points[-1], args[0], args[1])[0])]
            minima.append(err_min) # later a better solution here?

        if lowest_min_only:
            globalmin = minima[0]
            for minimum in minima:
                if minimum[1] < globalmin[1]:
                    globalmin = minimum
            return globalmin
        else:
            return minima

    @staticmethod
    def _remove_duplicates(original, min_distance):
        """
        Removes duplicates from a list of found local minima given a minimum
        distance between distinct minima.
        """
        if len(original) == 0:
            return original
        current = copy.deepcopy(original)
        next = []
        firstRef = current[0][0]
        first_encountered_times = 0
        while True:
            next = []
            ref = current[0][0]; ref_f = current[0][1]
            if ref == firstRef:
                first_encountered_times += 1
                if first_encountered_times == 2:
                    break
            for i in range(1,len(current)):
                if euclidean(current[i][0], ref) > min_distance:
                    next.append(current[i])
            next.append([ref, ref_f])
            current = next
        return current


