"""Python code reflection and inspection magic"""
__version__ = '0.0.1'

from .magics import InspectMagics

def load_ipython_extension(ipython):
    """Load the extension."""
    ipython.register_magics(InspectMagics)
