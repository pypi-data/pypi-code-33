__author__ = 'anwenhu'
__date__ = '2019/1/27 15:18'
__version__ = "0.1.5"

from .zxw import Zhixuewang

VERSION = tuple(map(int, __version__.split('.')))
__all__ = [
    'man', 'utils', 'Zhixuewang', 'exam', 'grade', 'exceptions'
]
