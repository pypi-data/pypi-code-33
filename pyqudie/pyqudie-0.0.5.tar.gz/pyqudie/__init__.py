'''Kqudie python edition'''

import __main__

if __main__.__doc__ != 'setup.py':
    from . import Mongo
    from . import MongoExceptions

__version__ = "0.0.5"
__author__ = "evi0s<wc810267705@163.com>"
__name__ = "pyqudie"
__doc__ = "kqudie python edition"
__all__ = ['Mongo', 'MongoExceptions']
