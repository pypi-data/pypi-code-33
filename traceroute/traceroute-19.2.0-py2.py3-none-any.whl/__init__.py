"""
Cross-Platform traceroute for python.
"""
from __future__ import division
import sys

from .__version__ import __version__
from ._data import Traceroute, Hop, Route
from ._traceroute import _traceroute
from ._tracert import _tracert


def traceroute(target, **kwargs):
    """
    Get traceroute information.
    
    Args:   
        target (str): Name of traceroute target.

    Returns:
        Traceroute data object.
    """
    _traceroute = _get_platform_traceroute()
    return _traceroute(target, **kwargs)


def _get_platform_traceroute():
    """
    Get the traceroute implementation for the current platform.
    
    Returns:
        function: A traceroute function.
    """

    platform_map = {
        "linux2": _traceroute,
        "darwin": _traceroute,
        "win32": _tracert,
    }
    return platform_map[sys.platform]
