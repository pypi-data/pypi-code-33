import numpy as np
from scipy.stats import multivariate_normal, rv_continuous
from scipy.special import logsumexp

from . import channels

def get_info_length(code_length, channel, channelstate):
    rate = channel_capacity(channel, channelstate)
    info_length = int(np.floor(code_length*rate))
    return info_length


def channel_capacity(channel, channelstate=None):
    if isinstance(channel, channels.Channel):
        capacity = channel.capacity()
    elif channel == "BAWGN":
        capacity = _capacity_bawgn(channelstate)
    else:
        raise NotImplementedError("Could not calculate the capacity for "
                                  "channel: %s", channel)
    return capacity


def _phi(x, sigsq):
    return 1./(np.sqrt(8*np.pi*sigsq)) * (np.exp(-(x-1)**2/(2*sigsq))+np.exp(-(x+1)**2/(2*sigsq)))

def _integrand(x, sigsq):
    return _phi(x, sigsq)*np.log2(_phi(x, sigsq))

def _capacity_bawgn(snr):
    sigsq = 1./(10**(snr/10.))
    #integral = integrate.quad(lambda x: _integrand(x, sigsq), -np.inf, np.inf)
    x = np.linspace(-1-10*np.sqrt(sigsq), 1+10*np.sqrt(sigsq), num=4000)
    y = _integrand(x, sigsq)
    integral = np.trapz(y, x)
    capacity = -integral - .5*np.log2(2*np.pi*np.e*sigsq)
    return capacity


def entropy(prob):
    """Calculate the Shannon entropy of a discrete random variable.

    Parameters
    ----------
    prob : list (float)
        List of probabilities of the random variable.

    Returns
    -------
    entr : float
        Entropy in bits.
    """
    if not sum(prob) == 1:
        raise ValueError("The probabilities have to sum up to one")
    prob = np.array(prob)
    prob = prob[prob != 0]
    entr = -np.sum(prob * np.log2(prob))
    return entr


def binary_entropy(prob):
    """Calculate the Shannon entropy of a binary random variable.

    Parameters
    ----------
    prob : float
        Probability of one event.

    Returns
    -------
    entr : float
        Entropy in bits.
    """
    if prob == 0 or prob == 1:
        return 0.
    else:
        return -prob*np.log2(prob)-(1.-prob)*np.log2(1.-prob)


def entropy_gauss_mix_lower(mu, sig, weights=None, alpha=.5):
    """Calculate a lower bound of the differential entropy of a Gaussian mixture.
    
    Calculate a lower bound of the differential entropy of a Gaussian mixture 
    using the Chernoff alpha-divergence as distance (alpha=.5 for Bhattacharyya
    distance) according to (Kolchinsky et al, 2017) (arXiv: 1706.02419).

    Parameters
    ----------
    mu : array
        Array containing the different means of the Gaussian mixture components.
        The shape is (num_components, dimensions).

    sig : array
        Covariance matrix of the components. It is the same for all components.
        If a float is provided, it is assumed as the noise variance for a scaled
        identity matrix as the covariance matrix.

    weights : list, optional
        Weights/probabilities of the individual mixture components. If None, a
        uniform distribution is used.

    alpha : float, optional
        Value used for the alpha-divergence. Default is 0.5 which uses the
        Bhattacharyya distance.

    Returns
    -------
    lower_bound_entropy : float
        Lower bound on the differential entropy of the Gaussian mixture.
    """
    if weights is None:
        weights = np.ones(len(mu), dtype=float)/len(mu)
    dim = np.shape(mu)[1]
    if isinstance(sig, (float, int)):
        sig = sig*np.eye(dim)
    outer_sum = 0
    for idx_i, c_i in enumerate(weights):
        inner_sum = 0
        for idx_j, c_j in enumerate(weights):
            _sig_alpha = 1./(alpha*(1-alpha))*np.array(sig)
            _pdf_j_alpha = multivariate_normal.pdf(mu[idx_i], mean=mu[idx_j],
                                                   cov=_sig_alpha,
                                                   allow_singular=True)
            inner_sum += c_j*_pdf_j_alpha
        outer_sum += c_i*np.log(inner_sum)
    entropy_alpha = dim/2 + dim/2*np.log(alpha*(1-alpha)) - outer_sum
    return entropy_alpha

def entropy_gauss_mix_upper(mu, sig, weights=None):
    """Calculate an upper bound of the differential entropy of a Gaussian mixture.
    
    Calculate an upper bound of the differential entropy of Gaussian mixture
    using the KL-divergence as distance according to (Kolchinsky et al, 2017)
    (arXiv: 1706.02419).

    Parameters
    ----------
    mu : array
        Array containing the different means of the Gaussian mixture components.
        The shape is (num_components, dimensions).

    sig : array or float
        Covariance matrix of the components. It is the same for all components.
        If a float is provided, it is assumed as the noise variance for a scaled
        identity matrix as the covariance matrix.

    weights : list, optional
        Weights/probabilities of the individual mixture components. If None, a
        uniform distribution is used.

    Returns
    -------
    upper_bound_entropy : float
        Upper bound on the differential entropy of the Gaussian mixture.
    """
    if weights is None:
        weights = np.ones(len(mu), dtype=float)/len(mu)
    dim = np.shape(mu)[1]
    if isinstance(sig, (float, int)):
        sig = sig*np.eye(dim)
    outer_sum = 0
    for idx_i, c_i in enumerate(weights):
        inner_sum = 0
        for idx_j, c_j in enumerate(weights):
            _pdf_j = multivariate_normal.pdf(mu[idx_i], mean=mu[idx_j], cov=sig, allow_singular=True)
            inner_sum += c_j*_pdf_j
        outer_sum += c_i*np.log(inner_sum)
    entropy_kl = dim/2 - outer_sum
    return entropy_kl


class GaussianMixtureRv(object):  # TODO: Change to support scipy rv interface
    """Gaussian mixture random variable.

    This class allows building Gaussian mixture random variables, where all 
    components have the same covariance matrix.

    Parameters
    ----------
    mu : array
        List of the means of the individual Gaussian components. The shape
        therefore is (num_components, dimension).

    sigma : array or float, optional
        Covariance matrix. If only a float is provided, it is used for a
        scaled identity matrix as covariance matrix.

    weights : list, optional
        Weights/probabilities of the individual components. If None, a uniform
        distribution is used.
    """
    def __init__(self, mu, sigma=1., weights=None):#, *args, **kwargs):
        self.mu = np.array(mu)
        self.sigma = sigma*np.eye(np.shape(mu)[1]) if isinstance(sigma, (float, int)) else np.array(sigma)
        self.weights = np.ones(len(mu))/len(mu) if weights is None else np.array(weights)
        #super(GaussianMixtureRv, self).__init__(*args, **kwargs)

    def __len__(self):
        return len(self.mu)

    def dim(self):
        """Return the dimension of the distribution

        Returns
        -------
        dimension : int
            Dimension of the distribution.
        """
        return np.shape(self.mu)[1]

    def logpdf(self, x):
        _logpdf = [np.log(_w) + multivariate_normal.logpdf(
                    x, mean=_m, cov=self.sigma, allow_singular=True)
                   for _w, _m in zip(self.weights, self.mu)]
        return logsumexp(_logpdf, axis=0)

    def pdf(self, x):
        _pdf = [_w*multivariate_normal.pdf(x, mean=_m, cov=self.sigma,
                                           allow_singular=True)
                for _w, _m in zip(self.weights, self.mu)]
        return sum(_pdf)

    def rvs(self, N=1):
        x = np.empty((N, np.shape(self.mu)[1]))
        for row in range(N):
            _component = np.random.choice(range(len(self.mu)),  p=self.weights)
            _mu = self.mu[_component]
            x[row] = multivariate_normal.rvs(mean=_mu, cov=self.sigma)
        return x
