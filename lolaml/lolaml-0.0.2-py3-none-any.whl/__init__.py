from pkg_resources import DistributionNotFound, get_distribution

from .core import Run, run


try:
    __version__ = get_distribution('lolaml').version
except DistributionNotFound:
    __version__ = '(local)'


__all__ = ["run", "Run"]
