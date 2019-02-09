# coding=utf-8
'''provide class Path of type `str`.'''

import os

class Path(str):
    '''
    convenient to join file path in a chain manner:
    s = Path('.')
    s = s.join('a', 'b').join('..')
    '''
    def join(self, *args, **kw):
        return Path(os.path.normpath(os.path.join(self, *args, **kw)))
