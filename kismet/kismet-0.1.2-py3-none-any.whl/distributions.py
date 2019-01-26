from numbers import Number

from pyro import distributions
import torch
from torch.distributions import constraints
from torch.distributions.utils import broadcast_all

# Adapted from pytorch/torch/distributions/uniform.py
class DiscreteUniform(distributions.TorchDistribution):
    r"""
    Generates discrete uniformly distributed random samples from the interval
    ``[low, high]``.
    Example::
        >>> m = DiscreteUniform(torch.tensor([0.0]), torch.tensor([5.0]))
        >>> m.sample()  # uniformly distributed in the range [0.0, 5.0)
        tensor([ 2.3418])
    Args:
        low (float or Tensor): lower range (inclusive).
        high (float or Tensor): upper range (exclusive).
    """
    # TODO allow (loc,scale) parameterization to allow independent constraints.
    arg_constraints = {"low": constraints.dependent, "high": constraints.dependent}
    has_rsample = True

    @property
    def mean(self):
        return (self.high + self.low) / 2

    @property
    def stddev(self):
        return (self.high - self.low - 1) / 12 ** 0.5

    @property
    def variance(self):
        return (self.high - self.low + 1).pow(2) / 12

    def __init__(self, low, high, validate_args=None):
        self.low, self.high = broadcast_all(low, high)

        if isinstance(low, Number) and isinstance(high, Number):
            batch_shape = torch.Size()
        else:
            batch_shape = self.low.size()
        super(DiscreteUniform, self).__init__(batch_shape, validate_args=validate_args)

        if self._validate_args and not torch.lt(self.low, self.high).all():
            raise ValueError("DiscreteUniform is not defined when low>= high")

    def expand(self, batch_shape, _instance=None):
        new = self._get_checked_instance(DiscreteUniform, _instance)
        batch_shape = torch.Size(batch_shape)
        new.low = self.low.expand(batch_shape)
        new.high = self.high.expand(batch_shape)
        super(DiscreteUniform, new).__init__(batch_shape, validate_args=False)
        new._validate_args = self._validate_args
        return new

    @constraints.dependent_property
    def support(self):
        return constraints.interval(self.low, self.high)

    def rsample(self, sample_shape=torch.Size()):
        shape = self._extended_shape(sample_shape)
        rand = torch.rand(shape, dtype=self.low.dtype, device=self.low.device)
        return torch.floor(self.low + rand * (self.high - self.low + 1)).type(torch.LongTensor)

    def log_prob(self, value):
        # TODO verify
        if self._validate_args:
            self._validate_sample(value)
        lb = value.ge(self.low).type_as(self.low)
        ub = value.lt(self.high).type_as(self.low)
        return torch.log(lb.mul(ub)) - torch.log(self.high - self.low + 1)

    def cdf(self, value):
        if self._validate_args:
            self._validate_sample(value)
        result = (value - self.low + 1) / (self.high - self.low + 1)
        return result.clamp(min=0, max=1)

    def icdf(self, value):
        if self._validate_args:
            self._validate_sample(value)
        result = value * (self.high - self.low + 1) + self.low - 1
        return result

    def entropy(self):
        return torch.log(self.high - self.low + 1)
