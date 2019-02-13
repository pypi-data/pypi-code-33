#! /usr/bin/python
# -*- coding: utf-8 -*-

# from .data import FitsImage
# from .data import __all__ as alldata
from .image import Image
from .image import __all__ as allimage

__all__ = []
# __all__.extend(alldata)
__all__.extend(allimage)