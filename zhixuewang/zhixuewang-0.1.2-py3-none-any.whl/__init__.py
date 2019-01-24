__author__ = 'anwenhu'
__date__ = '2019/1/24 18:15'
__version__ = '0.1.2'

from .zxw import Zhixuewang

VERSION = tuple(map(int, __version__.split('.')))
__all__ = [
    'man', 'utils', 'Zhixuewang', 'exam', 'grade', 'exceptions'
]
