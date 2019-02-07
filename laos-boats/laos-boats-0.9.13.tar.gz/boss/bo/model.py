import GPy
import numpy as np

from ..utils import Minimization

class Model(GPy.core.gp.GP):
    """
    Functionality for creating, refitting and optimizing a GP model
    """
    def __init__(self, X, Y, bounds, min_dist_acqs,
                 minzacc, kerntype, kernel, dim, noise):
        """
        Initializes the Model class.
        """
        self.bounds = bounds
        self.min_dist_acqs = min_dist_acqs
        self.minzacc = minzacc
        self.kerntype = kerntype
        self.kernel = kernel
        self.dim = dim
        super().__init__(
          X.copy(),
          Y.copy(),
          self.kernel,
          likelihood = GPy.likelihoods.Gaussian(),
          inference_method =
            GPy.inference.latent_function_inference.ExactGaussianInference()
        )
        self.likelihood.fix(noise)

    def add_data(self, newX, newY):
        """
        Updates the model evidence (observations) dataset appending.
        """
        X = np.vstack([self.X, np.atleast_2d(newX)])
        Y = np.vstack([self.Y, newY])
        self.set_XY(X.copy(), Y.copy())

    def redefine_data(self, X, Y):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        self.set_XY(np.atleast_2d(X.copy()), np.atleast_2d(Y.copy()))

    def optimize_controlrstr(self, restarts=1):
        """
        Updates the model hyperparameters by maximizing marginal likelihood.
        """
        self.optimization_runs = []
        if restarts == 1:
            super().optimize()
        else:
            super().optimize_restarts(
                num_restarts=restarts, verbose=False, messages=False)

    def get_unfixed_params(self):
        """
        Returns the unfixed parameters of the model in an array where
        the first element is the variance and the rest are lenghtscales.
        Note that this function assumes that only variances and lengthscales
        are free hyperparameters.
        """
        return np.array(self.unfixed_param_array.copy()).astype(float)

    def get_all_params(self):
        """
        Returns the parameters of the model in format:
        noise, variance, lengthscales, periods
        where the last two are 1D lists. There exists a period only for those
        dimensions which are using a periodic kernel.
        """
        pars = self.param_array
        noise = float(pars[-1])
        sigma = float(pars[0])
        ls_and_per = pars[0:-1]
        lss = []; pers = []
        pbc_dims = list(np.where(np.array(self.kerntype) == 'stdp')[0])
        ind = 0
        for i in range(self.dim):
            if i in pbc_dims:
                pers.append(float(ls_and_per[ind])); ind += 1
            lss.append(float(ls_and_per[ind])); ind += 1
        return noise, sigma, lss, pers

    def set_unfixed_params(self, params):
        """
        Sets the unfixed parameters of the model (variance, lengthscales) to
        given values.
        """
        self['.*kern.variance'] = params[0]
        lss = self['.*lengthscale*']
        for i in range(self.dim):
            lss[i] = params[i+1]
        self.trigger_update()

    def min_prediction(self):
        """
        Find and returns the model global minimum prediction xhat
        and the model mean (muhat) and variance (nuhat) at that point.
        """
        gmin = Minimization.minimize(
                        self.mu_with_grad,
                        self.bounds,
                        self.kerntype,
                        np.hstack([self.X.copy(), self.Y.copy()]),
                        self.min_dist_acqs,
                        accuracy=self.minzacc,
        )
        xhat = np.array(gmin[0])
        muhat, nuhat = self.predict(np.atleast_2d(xhat))
        return xhat, muhat[0][0], nuhat[0][0]

    def mu(self, x):
        """
        Returns model prediction mean at point x.
        """
        m, v = self.predict(np.atleast_2d(x))
        return m

    def nu(self, x):
        """
        Returns model prediction variance at point x, taking into account the
        model variance (noise).
        """
        m, v = self.predict(np.atleast_2d(x))
        v = np.clip(v, 1e-12, np.inf)
        return np.sqrt(v)

    def mu_with_grad(self, x):
        """
        Returns model mean and its gradient at point x.
        """
        m, v = self.predict(np.atleast_2d(x))
        dmdx, dvdx = self.predictive_gradients(np.atleast_2d(x))
        scipygradient = np.asmatrix(dmdx).transpose()
        return m, scipygradient

    def get_bestxy(self):
        """
        Returns the lowest energy acquisition (x, y). Note that this does not
        account for the model mean shift introduced by the BoMain class.
        """
        xbest = np.array(self.X[np.argmin(self.Y)])
        ybest = np.min(self.Y)
        return xbest, ybest

    def predictive_m_s_grad(self, x):
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, taking into account the model variance (noise).
        """
        m, v = self.predict(np.atleast_2d(x))
        v = np.clip(v, 1e-12, np.inf)
        dmdx, dvdx = self.predictive_gradients(np.atleast_2d(x))
        dmdx = dmdx[:,:,0]
        dsdx = dvdx / (2*np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

