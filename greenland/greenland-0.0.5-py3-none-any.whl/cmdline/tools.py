# *   Copyright (C) 2018 M E Leypold, GPL3-or-later licensed -----------------------|
#
#     greenland.cmdline.tools -- basic tools to build command line parsers
#     Copyright (C) 2018 M E Leypold
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#


# *   Preamble ---------------------------------------------------------------------|

import re
from greenland.metaprogramming.definition_order import WithDefinitionOrder
from more_itertools import peekable
from abc import abstractmethod

# *   Preprocessing ----------------------------------------------------------------|

class ArgvPreProcessor ( WithDefinitionOrder ):

    class Argument(object):
        is_separator = False
        is_error     = False
        base_group   = None     # to be patched in below ...

        def __init__(self,match,origin=None):
            self.match  = match
            self.origin = origin

        @property
        def is_option(self): return self.rxc.groups>=1
        @property
        def is_posarg(self): return (not self.is_separator) and (not self.is_option)
    
        @property
        def carries_value(self): return self.rxc.groups>=2

        @property
        def lexeme(self): return self.match.group(0+self.base_group)        
        @property
        def label(self): return self.match.group(1+self.base_group)
        @property
        def value(self): return self.match.group(2+self.base_group)

        def __repr__(self):
            s = "<{CLASSNAME} {LEXEME!r}".format(CLASSNAME=self.__class__.__name__, LEXEME=self.lexeme)
            if self.is_option:
                s += '| {LABEL!r}'.format(LABEL=self.label)
            if self.carries_value:
                s += ': {VALUE!r}'.format(VALUE=self.value)            
            s += ">"

            return s

    class Error(Argument):
        is_error      = True
        is_option     = False
        is_posarg     = False
        carries_value = False
        value         = None
        
        
    class NonOption(Argument):
        is_option = False
        
    class PositionalArgument (NonOption):
        rx = "(?:.+)|.{0,1}"

        @property
        def value(self): return self.lexeme
           
    class DoubleDash         (NonOption):
        rx = "[-][-]"; is_separator = True
    
    class Option(Argument):
        is_option = True
        
    class ClassicOption      (Option):
        rx = "[-]([^-0-9].*)"

    class ClassicAntiFlag    (Option):
        rx = "[+]([^-+])"
        carries_value = True
        value = "False"

    class AntiFlagTooLongError (Error):
        rx  = "[+]([^-+]..*)"        
        msg = "AntiFlag can only be 1 letter long"

    class AntiFlagMalformedError (Error):
        rx  = "[+]([-+=].*)"        
        msg = "malformed AntiFlag"        
        
    class GnuOption          (Option):
        rx = "[-][-]([^=]+)=(.*)"
        
    class GnuFlag            (Option):        
        rx = "[-][-]([^=]+)"
        carries_value = True
        value = "True"

    class GnuOptionMalformedError (Error):
        rx = "--([+=-].*)"
        msg = "malformed or empty GNU option"
        
    class NegatedFlag (Option):
        rx = "[-]{1,2}no-([^-].*)"
        carries_value = True
        value = "False"
        
    def __init__(self):
        
        Argument   = self.Argument
        rxs        = []
        classes    = []
        base_group = 1
        last_index = {}
        
        for name in reversed(self.__members_definition_order__):
            member = getattr(self,name)
            if isinstance(member,type) and issubclass(member,Argument) and hasattr(member,'rx'):
                classes.append(member)

        for item in classes:
                
            if not hasattr(item,'rxc'):
                item.rxc = re.compile(item.rx)
            item.base_group = base_group
            last_index[base_group] = item                
            n_groups = item.rxc.groups+1 
            base_group += n_groups
            rxs.append(item.rx)

        self.class_from_lastindex = last_index
        rx = self.rx = "(?:("+(")|(".join(rxs))+"))$"
        self.rxc = re.compile(rx)
        
    def preprocessed(self, argv):
        for i,arg in enumerate(argv):
            yield self.match(arg,i+1)

    def match(self,arg,origin=None):
        match = self.rxc.match(arg)
        tokenclass = self.class_from_lastindex[match.lastindex]
        token = tokenclass(match,origin)
        return token

def preprocessed(argv):
    return ArgvPreProcessor().preprocessed(argv)

def extract_lexemes(tokens):
    lexemes = []
    for token in tokens:
        lexemes.append(token.lexeme)
    return lexemes

# *   Error Formatting -------------------------------------------------------------|

# Note: Content of this section is not actually specific to command
# line parsing and will have to go to somewhere else (e.g. formatting)

def underline(args,underlined,maxlength=None):
    """underline items in a string list, possibly truncate result id too long.
    """

    underlines = [ (("-" if i in underlined else " ") *len(arg)) for i,arg in enumerate(args)]
    
    leading_ellipsis  = ""
    trailing_ellipsis = ""

    def current_length():
        return 0 \
            + len(leading_ellipsis) + len(trailing_ellipsis) \
            + len(args) \
            + sum( (len(arg) for arg in args) )

    def result_lines():
        return ( leading_ellipsis+(" ".join(args))+trailing_ellipsis ,
                 " "*len(leading_ellipsis)+(" ".join(underlines))+" "*len(trailing_ellipsis)
        )


    if maxlength == None: return result_lines()

    underline_start = min(underlined)
    underline_end   = max(underlined)

    if current_length() < maxlength:
        return result_lines()

    args = args[:underline_end+1]
    underlines = underlines[:underline_end+1]
    trailing_ellipsis = " ..."

    if current_length() < maxlength:
        return result_lines()

    args = args[underline_start-1:]
    underlines = underlines[underline_start-1:]
    leading_ellipsis = "... "
    underline_start -= underline_start-1
    underline_end   -= underline_end-1

    args = args[1:]
    underlines = underlines[1:]

    underline_start -= 1
    underline_end   -= 1    

    if current_length() < maxlength:
        return result_lines()

    return result_lines()    

# *   Convenient Conversions -------------------------------------------------------|

def flag (string):

    """
    Conversion function for commandline flags.
       
    Converts string literals given at the commandline as values for
    commandline flags (basically :code:`bool` valued options) to
    :obj:`bool`.

    Literals interpreted as :code:`True`: :code:`yes`, :code:`y`,
    :code:`True`, :code:`true`, :code:`on`, :code:`0`, :code:`active`.

    Literals interpreted as :code:`False`: :code:`no`, :code:`n`,
    :code:`False`, :code:`false`, :code:`off`, :code:`1`,
    :code:`inactive`.
    """
        
    if   string in ['yes','y','True','true','on','0','active']: return True
    elif string in ['no','n','False','false','off','1','inactive']: return False
    raise ValueError("cannot convert " + repr(string) + " as flag")

# *   ------------------------------------------------------------------------------|
