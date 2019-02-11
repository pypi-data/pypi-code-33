from functools import wraps
from warnings import warn

__author__ = "Sebastian Tilders"
__version__ = "0.2.0"

def deprecated(func):
	""" Decorator which designates functions as deprecated """
	@wraps(func)
	def closure(*args, **kwargs):
		warn("Python 2.7 support my be dropped in the future", PendingDeprecationWarning, stacklevel=2)
		func(*args, **kwargs);
	closure.__doc__ = '@deprecated\r\n' + func.__doc__
	return closure
