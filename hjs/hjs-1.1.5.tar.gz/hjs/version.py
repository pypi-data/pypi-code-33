# coding: utf-8
from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution('hjs').version
except DistributionNotFound:
    __version__ = '#UNRELEASED#'
