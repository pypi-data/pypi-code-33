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
Commandline parser primitives and combinators.
"""

# *  Preamble ---------------------------------------------------------------------|

from abc import abstractmethod
from more_itertools import peekable
from greenland.cmdline.tools import preprocessed, underline, flag

# *  Tools ------------------------------------------------------------------------|

def maybe_to_specmap(data):
    if hasattr(data,'get'): return data
    d = {}
    for item in data:
        d[item.name] = item
        for key in item.aliases:
            d[key] = item
    return d

def append_to_list(values,new_value):
    if values==None: return [ new_value ]
    values.append(new_value)
    return values

def add_to_set(values,new_value):
    if values==None: return { new_value }
    values.add(new_value)
    return values

# *  CommandLine context ----------------------------------------------------------|

from greenland.conventions import UserError

class CommandLine(peekable):

    """
    Providing tokens as iterator and rewrites commandline referencing exceptions
    """
    
    def __init__(self,cmdline,start=1,program=None):

        super().__init__(preprocessed(cmdline[start:]))
        self.start = start
        self.cmdline  = cmdline
        self.program  = cmdline[0] if program == None else program

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == self.Error:
            raise self.ErrorInContext(error=exc_value,cmdline=self)
        return False

    class ErrorBase(UserError):

        start = 1
        
        def range_string(self):

            tokens = self.tokens

            assert len(tokens) > 0

            if len(tokens) == 1:
                range = tokens[0].origin + self.start - 1
            else:
                range = "{FROM}..{TO}".format(FROM=tokens[0].origin + start - 1 ,TO=tokens[-1].origin + start - 1 )

            return range

        def lexemes(self):
            return [token.lexeme for token in self.tokens]

    class Error(ErrorBase):
        def __init__(self,message,tokens):
            self.message = message
            self.tokens  = tokens

        def __str__(self):

            lexemes = self.lexemes()        
            if len(lexemes) == 0: return self.message

            range = self.range_string()

            return ( "{MSG}: ${RANGE} = {TOKENS!r}" .format(
                MSG    = self.message,
                TOKENS = lexemes,
                RANGE  = self.range_string()
            ))

        
    class ErrorInContext(Error):
        
        def __init__(self,error,cmdline):
            self.error   = error
            self.cmdline = cmdline

        @property
        def args(self): return self.cmdline.cmdline

        @property
        def program(self): return self.cmdline.program        

        @property
        def start(self): return self.cmdline.start        

        @property
        def tokens(self): return self.error.tokens        

        @property
        def message(self): return self.error.message

        def __str__(self):
            return "\n\n" + self.__longstr__()

        def get_error_context(self,tokens):
            args       = self.args    
            if tokens != None: 
                underlined = set((token.origin+self.start-1 for token in tokens))
            else:
                underlined = set((len(args),))
                args = list(args) + [ "   " ]            
            return underline(args,underlined)

        def __longstr__(self):
            return "\n".join([ self.program + ": " + self.__class__.__qualname__ + ":",
                               "    " + "\n    ".join(self.get_error_context(self.tokens)),
                               "    " + self.message+"."
            ])


# *  BaseParser -------------------------------------------------------------------|

class BaseParser(object):

    @abstractmethod
    def parse(self,tokens): pass

    def raise_error(self,message,tokens):
        raise CommandLine.Error(message,tokens)

# *  OptionsProcessor -------------------------------------------------------------|
    
class OptionsProcessor(BaseParser):

        
    def __init__(self, specs):
        self.specs = maybe_to_specmap(specs)
    
    class Argument  (object):

        is_kwarg     = False
        is_posarg    = False        
        is_separator = False
        
        def __init__(self,tokens):
            self.tokens = tokens
            
        @abstractmethod
        def store(self,container): pass
            
        @property
        def preprocessed_token(self):
            assert len(self.tokens) == 1
            return self.tokens[0]
    
    class KwArg     (Argument):

        is_kwarg  = True
        
        def __init__(self,tokens,key,value,merge=(lambda values,new_value: new_value)):
            super().__init__(tokens)
            self.key = key
            self.value = value
            self.merge = merge
            
        def __repr__(self):
            return "<KwArg {KEY}: {VALUE!r} {TOKS!r}>".format(TOKS=self.tokens,VALUE=self.value,KEY=self.key)
            
        def store(self,container):
            values = container[self.key] if self.key in container else None
            container[self.key] = self.merge(values,self.value)


    class PosArg    (Argument):

        is_posarg = True
        
        def __init__(self,tokens,index,value):
            super().__init__(tokens)
            assert len(self.tokens) == 1, "internal error: PosArg can only hold one token"
            self.index = index
            self.value = value
        
        def __repr__(self):
            return "<PosArg {INDEX} => {VALUE!r} {TOKS!r}>".format(TOKS=self.tokens,INDEX=self.index,VALUE=self.value)

        def store(self,container):
            
            index = self.index
            
            if isinstance(container,list):
                while not index<len(container):
                    container.append(None)

            container[index] = self.value

                
    class Separator (Argument):

        is_separator = True
        
        def __repr__(self):
            return "<Separator {SEP!r}>".format(SEP=self.tokens)

    def conversion(self,spec):
        if hasattr(spec,'convert'):
            return spec.convert
        else:
            return lambda x:x # leave untouched
        
    def convert(self,spec,arg):

        conversion = self.conversion(spec)
        stringval  = arg.value
        try:
            converted = conversion(stringval)
        except ValueError:
            self.raise_error("cannot convert option argument with "+repr(conversion),[arg])

        return converted

    def merge_method(self,spec):
        if hasattr(spec,'merge') and spec.merge != None: return spec.merge
        else: return (lambda values,new_value: new_value)

    def apply_defaults(self,options):
        for alias,spec in self.specs.items():
            key = spec.key
            if key in options: continue
            try:
                options[key] = spec.default
            except AttributeError:
                pass

    def process(self,args):
        return peekable(self._process(args))
    
    def _process(self,args):
        
        assert hasattr(args,'__next__'), "client error: argument to process() needs to be an iterator"

        def convert(spec,arg): return self.convert(spec,arg)
                             
        n_posargs = 0
        
        for arg in args:
            
            if arg.is_error: self.raise_error("malformed option or posarg (syntax error): " + arg.msg,[arg])
            
            if arg.is_option:
                label = arg.label
                if not label in self.specs: self.raise_error("unknown option",[arg])
                
                spec = self.specs[label]

                if arg.carries_value:

                    # Note: --alpha 1 passes here (and must fail for typing reasons only),
                    # since --alpha=Foo and --alpha and --alpha=True cannot be
                    # distinguished. That is as it should be.

                    yield(self.KwArg([arg],spec.key, convert(spec,arg), self.merge_method(spec)))
                          
                                        
                else:
                    if hasattr(spec,'implied_value'):
                        yield(self.KwArg([arg],spec.key,spec.implied_value, self.merge_method(spec)))
                        # note: we never convert the implied value. Guess why. (?)
                    else:
                        try:
                            arg2 = next(args)
                        except StopIteration:
                            self.raise_error("expected argument after option",None)
                        if not arg2.is_posarg:
                            self.raise_error("argument to option is not a positional argument (syntactically)",[arg,arg2])
                            
                        yield(self.KwArg([arg,arg2],spec.key,convert(spec,arg2),self.merge_method(spec)))

            elif arg.is_separator:
                yield(self.Separator([arg]))                
            else:
                assert arg.is_posarg, "internal error: expected posarg after handling other known types"
                    
                yield(self.PosArg([arg],n_posargs,arg.lexeme))
                n_posargs += 1

        
# *  OptionsParser  ---------------------------------------------------------------|

class OptionsParser(OptionsProcessor):

    def parse(self,args):
        options = {}
        for item in self.process(args):
            if item.is_kwarg:
                item.store(options)
            else:
                assert item.is_posarg or item.is_separator, "internal error: unexpected item type"
                args.prepend(item.preprocessed_token) # push it back
                break
        self.apply_defaults(options)
        return options


# *  OptionsAndPosArgsParser  -----------------------------------------------------|

class OptionsAndPosArgsParser(OptionsProcessor):

    def parse(self,args):

        options = {}
        posargs = []

        for item in self.process(args):
            if item.is_posarg:
                posargs.append(item.preprocessed_token)
            elif item.is_kwarg:
                item.store(options)
            else:
                assert item.is_separator, "internal logic error: token must be posarg, kwarg or separator"
                args.prepend(item.preprocessed_token) # push it back                
                break
            
        self.apply_defaults(options)
        return options,posargs
        

# *  PosArgsCollector  ------------------------------------------------------------| 

class PosArgsCollector(BaseParser):
    
    def parse(self,tokens):

        pargs = []
        
        for token in tokens:
            if token.is_posarg:
                pargs.append(token)
            else:
                tokens.prepend(token)
                break

        return pargs
            
posargs_collector = PosArgsCollector()

# *  PosArgsBinder  ---------------------------------------------------------------|

class PosArgsBinder(BaseParser):
    
    def __init__( self, slots):

        super().__init__()
        
        self.leading    = slots.leading
        self.trailing   = slots.trailing

        self.leading_optional  = slots.leading_optional
        self.trailing_optional = slots.trailing_optional

        self.variadic = slots.variadic


    @property
    def have_variadic(self): return self.variadic != None

    @property
    def variadic_min_required(self):
        return 0 if not self.have_variadic else self.variadic.min_required

    @property
    def variadic_max_allowed(self):
        return 0 if not self.have_variadic else (None if self.variadic.unlimited_allowed else self.variadic.max_allowed)

    @property
    def variadic_unlimited_allowed(self):
        return self.have_variadic and self.variadic.unlimited_allowed
        
    @property
    def unlimited_allowed(self): 
        return self.variadic_unlimited_allowed

    
    @property
    def min_required(self):
        return (
            len(self.leading)
            +  self.variadic_min_required
            +  len(self.trailing)
        )
    
    @property
    def max_allowed(self):
        if self.unlimited_allowed: return None
        return (
            len(self.leading) + len(self.leading_optional)
            +  self.variadic_max_allowed    
            +  len(self.trailing) + len(self.trailing_optional)
        )

    @classmethod
    def conversion(cls,spec):
        if hasattr(spec,'convert'): return spec.convert
        else                      : return (lambda x:x)

               
    @classmethod
    def bind_sequence(cls,specs,args,result, optional = False ):
        assert optional or len(specs) == len (args), "internal error of PosArgsBinder (this is a bug)"
        
        for i,spec in enumerate(specs[:len(args)]):
            result[spec.key] = cls.conversion(spec)(args[i].lexeme)
    
    @classmethod
    def bind_variadic(cls,spec,args,result):
        assert len(args)>= spec.min_required, "not enough arguments"
        assert spec.unlimited_allowed or len(args) <= spec.max_allowed, "too many arguments"

        result[spec.key]=[ (cls.conversion(spec)(arg.lexeme)) for arg in args ]
    
    def bind(self,args):

        if len(args) < self.min_required:
            self.raise_error("not enough arguments",None)

        if not self.unlimited_allowed and len(args)>self.max_allowed:
            extra_args = args[self.max_allowed:]
            self.raise_error("too many arguments",extra_args)
            
        result = {}

        b1 = len(self.leading)
        b2 = len(self.trailing)
        self.bind_sequence(self.leading,args[0:b1],result)
        if b2>0: self.bind_sequence(self.trailing,args[-b2:],result)

        args0 = args
        args  = args[b1:len(args)-b2]
        assert len(args) + b1 + b2 == len(args0), "internal error, remaining (option) args part calculated incorrectly"

        b1 = min(len(self.leading_optional),len(args))
        assert b1 <= len(args), "internal error: leading optional args count calculated incorrectly"
        
        b2 = (0 if b1 == len(args) else min(len(args)-b1,len(self.trailing_optional)))
        assert b1 + b2 <= len(args), "internal error: trailing optional args calculated incorrectly"
        
        self.bind_sequence(self.leading_optional,args[0:b1],result,optional=True)
        if b2>0: self.bind_sequence(list(reversed(self.trailing_optional)),list(reversed(args[-b2:])),result,optional=True)

        args0 = args
        args  = args[b1:len(args)-b2]
        assert len(args) + b1 + b2 == len(args0), "internal error: variadic args part calculated incorrectly"
        
        if self.have_variadic: self.bind_variadic(self.variadic,args,result)

        return result



# *  PosArgsCollectorAndBinder  ---------------------------------------------------|

class PosArgsCollectorAndBinder(PosArgsBinder,PosArgsCollector):
    
    def __init__(self,slots):
        PosArgsBinder.__init__(self,slots)
        PosArgsCollector.__init__(self)

    def parse(self,tokens):
        posargs = super().parse(tokens)
        mapping = self.bind(posargs)
        return mapping

# *  Delimiters  ------------------------------------------------------------------|

class OptionalSeparator(BaseParser):
    
    def parse(self,tokens):
        token = tokens.peek(None)
        if token == None: return 0
        if token.is_separator:
            next(tokens)
            return 1
        return 0

optional_separator = OptionalSeparator()

class EndOfArgs(BaseParser):
    
    def parse(self,tokens):
        token = tokens.peek(None)
        if token == None: return True
        self.raise_error("expected end of arguments here",[token])

end_of_args = EndOfArgs()

class Nothing(BaseParser):
    
    def parse(self,tokens):
        return None

nothing = Nothing()

# *  SubcommandsSwitch ------------------------------------------------------------|

class SubcommandsSwitch(BaseParser):

    def __init__(self, subcommands_spec):
        self.subcommands_spec = maybe_to_specmap(subcommands_spec)

    def parse(self,tokens):
        token = tokens.peek(None)
        command = token.lexeme if token != None else None        
        if command != None:
            if token.is_separator:
                command = None
            else:
                if not token.is_posarg:
                    self.raise_error("expected subcommand here",[token])
        if command in self.subcommands_spec:        
            if command != None:
                next(tokens)                
            return self.subcommands_spec[command]
        else:
            if token != None:
                self.raise_error("unknown subcommand",[token])
            else:
                self.raise_error("subcommand expected",[token])

# *  SubcommandsParser ------------------------------------------------------------|

class SubcommandsParser(SubcommandsSwitch):

    def parse(self,tokens):
        subcommand = super().parse(tokens)
        subparser  = subcommand.parser

        if subparser !=None: more = subparser.parse(tokens)
        else               : more = None

        if more == None       : more = ()
        elif type(more)==list : more = tuple(more)
        elif type(more)!=tuple: more = (more,)

        return (subcommand,)+more

# *  Sequence combinator ----------------------------------------------------------|

class Sequence(BaseParser):
    
    def __init__(self,*parsers,convert=(lambda *results: results)):
        self.parsers     = parsers
        self.__convert__ = (lambda *results: results) if convert==None else convert
        assert hasattr(convert,'__call__'), "might have been be calling Sequence(parsers) instead of Sequence(*parsers)"

    def convert(self,*results): return self.__convert__(*results)

    def parse(self,tokens):
        return self.convert(*[parser.parse(tokens) for parser in self.parsers ])


# *  OptionsThenPosArgsParser  ----------------------------------------------------|

class OptionsThenPosArgsParser(Sequence):
    def __init__(self,options_spec,convert=None):
        options_parser = OptionsParser(options_spec)
        posargs_parser = PosArgsCollector()
        super().__init__(options_parser,posargs_parser,convert=convert)

