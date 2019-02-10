"""package chem_gm.

This package contains the basis of neural network graphmachine applied to chemical.
"""
from ..version_gm import __version__
#from .version import __version__
import os

def installFileName(path="", ext=""):
    st = "chem_gm-%s%s" % (__version__, ext)
    if len(path):
        st = os.path.join(path, st)
    return st

# def hook():
#     return "gm"