# * Copyright (C) 2018 M E Leypold, GPL3-or-later licensed ------------------------|
#
#   greenland.cmdline.parsers -- Commandline parser primitives and combinators
#   Copyright (C) 2018 M E Leypold
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see
#   <https://www.gnu.org/licenses/>.
#

"""
Master regular expressions.
"""
# *   Imports

import re

# *   MasterRe

class MasterRe(object):
    def __init__(self,rxs):
        
        ctors = []
        partial_res = self.partial_res = []
        start_index        = []
        end_index          = []
        index = 1

        for partial_re, ctor in rxs:
            start_index.append(index)
            rx     = re.compile(partial_re)        # assert on this failing
            index += rx.groups
            end_index.append(index)
            index += 1
            partial_res.append(partial_re)
            ctors.append(ctor)

        self.ctors = { index : (ctor,start_index[i])
                       for i,ctor in enumerate(ctors)
                       for index in range(start_index[i],end_index[i]+1)
        }
                       
            
        self.re = "("+(")|(".join(partial_res))+")"
        self.rx = re.compile(self.re)

        print(self.ctors)

    def not_matched(self,string,pos):
        pass

    def construct(self,ctor,match,group_base):
        return ctor(match,group_base)
        
    def match(self,string,pos=0):
        m = self.rx.match(string,pos)
        if not m: return self.not_matched(string,pos)
        ctor,group_base = self.ctors[m.lastindex]
        return (m.end()-m.start()),self.construct(ctor,m,group_base)
        
