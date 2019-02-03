"""
MIT License

Copyright (c) 2018 Andre Augusto

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

import re
import discord
from itertools import chain, tee
from typing import List, Iterable, Callable

class SpecialType:
    def __getitem__(self, *args, **kwargs):
        return self.__class__(*args, **kwargs)

class _PassContext(SpecialType):
    def __init__(self, f):
        self.f = f
    def __call__(self, ktx, x):
        return self.f(ktx, x)
PassContext = _PassContext(None)

class _TakeWhile(SpecialType):
    def __init__(self, ann):
        self.ann = ann
    def __call__(self, ktx, nms):
        l = []
        hargs = nms['hargs']
        while True:
            try:
                v = next(hargs)
            except StopIteration:
                break
            try:
                l.append(self.ann(v))
            except:
                nms['hargs'] = chain([v], hargs)
                break
        if l:
            return l
        else:
            raise TypeError

TakeWhile = _TakeWhile(None)

class _Unsplitted(SpecialType):
    def __call__(self, ktx, nms):
        if nms['text']:
            return ''.join(nms['text'])
        else:
            orig = ktx.message.content
            rev = orig[::-1]
            for x in list(nms['hargs'])[::-1]:
                try:
                    rev = rev[rev.index(x[::-1]) + len(x):]
                except TypeError:
                    break
            rev = rev[::-1]
            return [orig[orig.index(rev) + len(rev):]]

Unsplitted = _Unsplitted()
        
_by_mention = lambda x: lambda y: str(y.id) == ''.join([z for z in x if z.isdigit()])
_by_id = lambda x: lambda y: str(y.id) == x
_by_name = lambda x: lambda y: y.name == x
_by_nick = lambda x: lambda y: y.nick == x
_by_repr = lambda x: lambda y: str(y) == x
_by_icon = lambda x: lambda y: y.icon_url == x

_all_ch = lambda cls: lambda ktx: list(filter(lambda x: isinstance(x, cls), 
                                              ktx.bot.get_all_channels()))

_all_tc = _all_ch(discord.TextChannel)
_all_vc = _all_ch(discord.VoiceChannel)
_all_cc = _all_ch(discord.CategoryChannel)
_all_gc = _all_ch(discord.GroupChannel)
_all_dm = _all_ch(discord.DMChannel)

_basic = [_by_mention, _by_id, _by_name]

def _chained_filter(name, filters: List[Callable], where:str):
    def _type(ktx, x, filters=filters, where=where):
        x = str(x)
        where = eval(where)
        try:
            fs = []
            for f in filters:
                where, where2 = tee(where)
                fs.append(filter(f(x), where2))
            return next(chain(*fs))
        except StopIteration:
            raise TypeError
    _type.__name__ = name
    return PassContext[_type]
        
Member = _chained_filter('Member', _basic + [_by_nick, _by_repr], 
                         'ktx.guild.members')
GlobalMember = _chained_filter('GlobalMember', _basic + [_by_nick, _by_repr], 
                               'ktx.bot.get_all_members()')
User = _chained_filter('User', _basic + [_by_repr], 
                      'ktx.bot.users')
TextChannel = _chained_filter('TextChannel', _basic, 
                              'ktx.guild.channels if ktx.guild else _all_tc(ktx)')
VoiceChannel = _chained_filter('VoiceChannel', _basic, 
                               'ktx.guild.voice_channels if ktx.guild else _all_vc(ktx)')               
CategoryChannel = _chained_filter('CategoryChannel', _basic, 
                                  'ktx.guild.categories if ktx.guild else _all_cc(ktx)')
GroupChannel = _chained_filter('GroupChannel', [_by_id, _by_name, _by_icon], '_all_gc(ktx)')
DMChannel = _chained_filter('DmChannel', [_by_id], '_all_dm(ktx)')
Guild = _chained_filter('Guild', [_by_id, _by_name, _by_icon], 'ktx.bot.guilds')
Role = _chained_filter('Role', _basic, 'ktx.guild.roles')

_ce_re = re.compile(r'<(a?):([a-zA-Z0-9\_]+):([0-9]+)>$')
def _custom_emoji(ktx, x):
    emoji = ktx.bot.get_emoji(int(x.split(':')[-1][:-1]))
    if emoji:
        return emoji
    else:
        m = _ce_re.match(x)
        if m:
            return discord.PartialEmoji(animated=bool(m.group(1)),
                                        name=m.group(2),
                                        id=int(m.group(3)))
    raise TypeError

CustomEmoji = PassContext[_custom_emoji]
