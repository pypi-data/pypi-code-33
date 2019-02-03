"""
MIT License

Copyright (c) 2019 Andre Augusto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from enum import Enum

class ParsingError(Exception):
    class ErrCodes(Enum):
        FewArguments = 0
        TooManyArguments = 1
        PassContextError = 2
        SpecialTypeError = 3
        CommonTypeError = 4
        IterableError = 5

    ERR = ['This invocation needs more arguments',
           'You sent too much arguments',
           '{x} is not a {ann} in this context',
           '{ann} failed', '{x} is not a {ann}',
           '{x} type is not in {ann}']

    def __init__(self, code, **kwargs):
        self.code = self.ErrCodes(code)
        self.kwargs = kwargs
        if code == 2:
            kwargs['ann'] = kwargs['ann'].f
        if 'ann' in kwargs:
            if hasattr(kwargs['ann'], '__name__'):
                kwargs['ann'] = kwargs['ann'].__name__
        msg = self.ERR[code].format(**kwargs)
        super().__init__(f'{self.code}: {msg}')

class ModifierError(Exception):
    class ErrCodes(Enum):
        Concurrency = 0
        Cooldown = 1
        UseLimit = 2
        NeedPerms = 3
        NeedRoles = 4
        OwnerOnly = 5
        DmOnly = 6
        GuildOnly = 7
        NsfwOnly = 8
        SafeOnly = 9
    
    ERR = ['Another instance is already running ({level})', 
           'Wait {wait}s to use again ({level})',
           'Your uses have ended, {wait}s to reset ({level})',
           "{target} don't have {mode} of the permissions: {perms}",
           "{target} don't have {mode} of the roles: {roles}",
           "This invocation can only be used by bot owners",
           'This invocation can only be used in a direct message',
           'This invocation can only be used in a guild',
           'This invocation can only be used in a nsfw channel',
           'This invocation can only be used in a safe channel']

    LVL = ['Global', 'Per Guild', 'Per Channel', 'Per User']
    
    def __init__(self, code, **kwargs):
        self.code = self.ErrCodes(code)
        if code in [0, 1, 2]:
            kwargs['level'] = self.LVL[kwargs['level']]
            if code in [1, 2]:
                kwargs['wait'] = round(kwargs['wait'], 2)
        elif code in [3, 4]:
            kwargs['target'] = kwargs['target'] or 'You'
        msg = self.ERR[code].format(**kwargs)
        self.kwargs = kwargs
        super().__init__(f'{self.code}: {msg}')

class DependencyError(Exception):
    def __init__(self, ext):
        super().__init__(f'This extension needs {ext} to work')
