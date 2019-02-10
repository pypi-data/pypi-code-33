# *   Copyright (C) 2018 M E Leypold, GPL3-or-later licensed -----------------------|
#
#     greenland.cmdline.specification -- specification syntax for greenland.cmdline.parsers
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

"""
Module :mod:`greenland.cmdline.specification` provides means and methods
to create commandline parsers from a high-level specification. 

Function :func:`cmdline_parser` constructs parsers from a specification. The
resulting parsers can be used "standalone", that is, directly with a
list of strings, or with a :class:`CommandLine` object that provides
sufficient context for "nice" error messages (see
:class:`CommandLine`).

The specifiers available for commandline parameter specifiation are:

.. tabularcolumns:: |l|L|l|l|

============= ================================= ====================================== ===================

Specifier     What does it specifiy?            Example                                   Usage
============= ================================= ====================================== ===================
`Option`      Commandline option                :code:`Option("scale",convert=float)`  ``--scale=1.3``
`Flag`        Commandline flag                  :code:`Flag("force",aliases=['f'])`       ``--force``, ``-f``
`Required`    Required positional parameter     :code:`Required("source")`               
`Optional`    Optional positional parameter     :code:`Optional("destination")`
`Variadic`    Variadic parameter                :code:`Variadic("more_sources")`
`no_variadic` (see below)                       
============= ================================= ====================================== ===================

The resulting parsers also recognize X11 style long options, like
``-accuracy 125.3`` and classic one-letter options, like ``-f`` or
``-a 125.3`` (if those have been specified as aliases, see
:py:class:`Option` and :py:class:`Flag`).

Currently the parsers do not allow to merge flags, like in ``-vf`` as
shortcut for ``-v -f`` or ``-a125.3``. 

.. Note: This functionality would depend on greenland.cmdline.tools
   and greenland.cmdline.parsers which currently are not documented to
   the user.

`no_variadic` serves as only a separator to separate leading from
trailing position arguments, a distinction that only makes sense if
there are trailing optional parameters. For details see
`no_variadic`.

Parsers also provide a rudimentary feature to print some commandline
interface documentation with
:py:meth:`CommandLineParserBase.print_doc_page` which is inherited by
all created parsers. Implementation of this feature is currently
experimental and definitely will change in the future.

Example
-------

.. A complete but not exhaustive example for constructing a
   commandline parser can be found in test/specification.py between
   the tags 'example "parser specification"'

.. literalinclude:: test/specification.py
   :start-after:    -- begin example "parser specification"
   :end-before:     -- end example "parser specification"
   :linenos:
   :dedent:         4

When ``parser.print_docpage()`` is called, the following commandline
interface documentation will be printed:

.. literalinclude:: test/specification.py
   :start-after:    example_docpage =
   :end-before:     -- end example "docpage"
   :linenos:
   :dedent:         8

.. For more information see: specification.rst
"""

# *   Preamble ---------------------------------------------------------------------|

from   more_itertools import peekable
from   greenland.toolbox.structs import Struct
from   greenland.cmdline.tools import flag
from   greenland.cmdline.parsers import maybe_to_specmap
from   greenland.cmdline.mixins import CommandParser, SubcommandPackageParser, MergeArguments

# *   Parameter Specification ------------------------------------------------------|
# **                                                                            DOC |
#                                                                                   |
# **  Base Classes -----------------------------------------------------------------|

class Specification(object):
    
    is_option     = False
    is_posarg     = False
    is_marker     = False
    is_subcommand = False
    is_variadic   = False
    
    def __init__(self,name,doc):
        self.name = name
        self.__doc__ = doc
        self._doc = None

    @property
    def doc(self):
        if self._doc == None:
            if self.__doc__ != None:
                self._doc = dedent(self.__doc__).split("\n")
            else: self._doc = ["(undocumented)."]
            
        return self._doc
           
    @property
    def tagline(self):
        return self.doc[0]


class ParameterSpecification(Specification):
    
    def __init__(self,name,convert,doc):
        super().__init__(name,doc)
        self.convert = convert

    @property
    def doc_tableline(self):
        return str(self),self.tagline

# **  Options ----------------------------------------------------------------------|

class OptionSpecification(ParameterSpecification):
    
    def __init__ (self,name,aliases=[],convert=str,doc=None,default=None,key=None):

        """Baseclass for option specifications"""


        assert callable(convert), "conversion function must be callable and accept a string"
        
        super().__init__(name,convert,doc)

        self.aliases = aliases

        assert hasattr(aliases,'__iter__') and not type(aliases)==str
        
        if key == None: self.key = name
        else:           self.key = key

        if default != None: self.default = default
                
    @property
    def labels(self):
        s = set(self.aliases)
        s.add(self.name)
        return s

    def __repr__(self):
        return "{CLASSNAME}(name={NAME!r}, aliases={ALIASES!r}, key={KEY!r}, convert={CONVERT}, doc={DOC})".format(
            CLASSNAME = self.__class__.__name__,
            NAME      = self.name,
            ALIASES   = self.aliases,
            KEY       = self.key,
            CONVERT   = self.convert,
            DOC       = "..."
        )

    
    
class Option (OptionSpecification):
    """
    Specifies a commandline option that requires a value.
    
    Parameters:

        name (str): Name of the option on the commandline, also used
            as default for `key`.

        aliases (:obj:`list` of :obj:`str`, optional): A list of names
            also to be understood as the same option. You can also use
            this to specify the single letter alternative forms of the
            option.

        convert (a function from :obj:`str` to the intended *target type*, optional): 
            This function is used to convert the value of the option
            given at the commandline (which is a string) to some other
            *target type* before returning it as the result of some
            parsing.

        doc (str): Documentation string explaining the option, will be
            used to generate the documentation pages. For details see
            :ref:`the section detailing the use of documentation
            strings <cmdline_specification_docstrings>`.

        default (any): The default value for this option, if not given
            at the command line. If not specified, and the option is
            not given at the commandline, no value will be stored
            under *key* as a parsing result for this option.

        key (str): The *key* used to store the converted value if the
            option is given at the command line.  What "stored"
            exactly means in this context depends on the parser
            generated: Usually results are stored in a `dict`.
    
    Example: 

        Specifiying :code:`Option("foo",['f'],float)` will result in a
        parser understanding the options :code:`--foo=`\\ *value*,
        :code:`-foo` *value* and :code:`-f` *value*, where *value*
        will be converted to a `float` during parsing and stored under
        key :code:`'foo'`.
    """
    
    is_option = True
    def __str__(self):
        return "-"+self.name+" $"+self.name.upper()

class Flag (OptionSpecification):
    """
    Specifies a commandline flag.

    Parameters:

        name (str): Name of the option on the commandline, also used
            as default for `key`.

        aliases (:obj:`list` of :obj:`str`, optional): A list of names
            also to be understood as the same option. You can also use
            this to specify the single letter alternative forms of the
            option.

        doc (str): Documentation string explaining the option, will be
            used to generate the documentation pages. For details see
            :ref:`the section detailing the use of documentation
            strings <cmdline_specification_docstrings>`.

        key (str): The key used to store the coverted value if given
            at the command line.  What "stored" exactly means in this
            context depends on the parser generated: Usually results
            are stored in a `dict`. 

    
    .. Note: The parameter documentation here should be the same as in
       class Option above. These _are_ indeed the same parameters,
       Flag is just a specialization of Option.

    The user will only be able to pass a value to a flag option at the
    commandline in GNU style and using :code:`=` as separator. For all
    other styles (X11, classic one-letter, GNU style without a value)
    the value will be taken as implied :code:`True`.

    Conversion follows the rules codified in :py:func:`flag`, meaning
    that various literals can be used as boolean values at the
    commandline: :code:`yes`, :code:`no`, :code:`on`, :code:`off`,
    etc.

    Example: 

        Specifiying :code:`Flag("compress",['c'],float)` will result
        in a parser understanding the options :code:`--compress=`\\
        *value*, :code:`--compress`, :code:`-compress`, :code:`-c`,
        :code:`-no-compress`, :code:`--no-compress` and :code:`+c`.

        *Value* can only be given with a GNU style syntax, otherwise
        the value is implied. For :code:`--compress`,
        :code:`-compress`, and :code:`-c` the implied value is
        :code:`True`, for :code:`-no-compress`, :code:`--no-compress`
        and :code:`+c` the implied value is `False`.

        If a *value* is given it will be converted to a `bool` during
        parsing and stored under the key :code:`'compress'`.

    """
    
    
    is_option     = True
    implied_value = True
    
    def __init__ (self,name,aliases=[],doc=None,key=None):
        super().__init__(name,aliases,convert=flag,doc=doc, default=False, key=key )

    def __str__(self):
        return "-"+self.name

# **  Positional Parameters --------------------------------------------------------|


class PositionalParameterSpecification(ParameterSpecification):    
    is_variadic = False
    is_posarg   = True
    is_optional = False
    
    def __init__(self,name,convert=str,doc=None):

        assert callable(convert), "conversion function must be callable and accept a string"
        
        super().__init__(name,convert,doc)
        self.key  = name

    def __repr__(self):
        return "{CLASSNAME}(name={NAME!r}, convert={CONVERT}, doc={DOC})".format(
            CLASSNAME = self.__class__.__name__,
            NAME      = self.name,
            CONVERT   = self.convert,
            DOC       = "..."
        )

    def __str__(self):
        return "$"+self.name.upper()
        
class Required(PositionalParameterSpecification):
    is_optional = False

class Optional(PositionalParameterSpecification):
    is_optional = True

    def __str__(self): return "["+super().__str__()+"]"
    
class Variadic(PositionalParameterSpecification):
    is_variadic = True
    is_optional = True

    @property
    def unlimited_allowed(self): return self.max_allowed == None

    def __init__(self,name,convert=str,doc=None,min_required=0,max_allowed=None):
        super().__init__(name,convert,doc)
        self.min_required = min_required
        self.max_allowed  = max_allowed
    
    def __str__(self): return super().__str__()+"..."


    

# **  Sub-Commands -----------------------------------------------------------------|

class Subcommand(Specification):
    is_subcommand = True

    def __init__(self,name,aliases=[],command=None,doc = None,parser=None):

        super().__init__(name,doc) # Maybe need to split the base class: No convert!

        self.aliases = aliases
        self.command = command if command != None else name
        self.parser  = parser


    @property
    def commands(self):
        s = set(self.aliases)
        s.add(self.name)
        return s
        
    @property
    def doc_tableline(self):
        return str(self),self.tagline

    def __str__(self): return self.name
    
# **  Syntactic Markers (separators) -----------------------------------------------|

class Marker(Specification):
    is_marker = True
    def __init__(self,name): self.name=name

no_variadic = Marker('no_variadic')
"""
Use this marker if you don't have a variadic parameter, but want
trailing or trailing optional parameters.
"""

# **                                                                           TODO |
# *   Parser Specification
# **  Base Classes

class CommandLineSpecificationBase(object):
            
    @staticmethod
    def get_option_specs(specs):
        options = []
        for spec in specs:
            if spec.is_option:
                options.append(spec)
            else:
                assert spec.is_marker or spec.is_posarg or spec.is_subcommand
                specs.prepend(spec)
                break
        return options

    @staticmethod
    def get_subcommand_specs(specs):
        subcommands = []
        for spec in specs:
            if spec.is_subcommand:
                subcommands.append(spec)
            else:
                assert False, "client error: subcommands should be last in list"
        return subcommands

    @staticmethod
    def map_from_specs(specs,keys = lambda obj: obj.keys):

        map = {}

        for spec in specs:
            spec_keys = keys(spec)
            for key in spec_keys:
                assert not key in map, "duplicate key {KEY!r} from spec {SPEC!r}\nspecs => {SPECS}".format(KEY=key,SPEC=spec,SPECS=specs)
                map[key] = spec
        return map

    @classmethod
    def map_from_option_specs(cls,specs): return cls.map_from_specs(specs,(lambda obj: obj.labels))

    @classmethod
    def map_from_subcommand_specs(cls,specs): return cls.map_from_specs(specs,(lambda obj: obj.commands))    

    @classmethod
    def get_posarg_specs(cls,specs):
        leading           = []
        leading_optional  = []
        variadic          = None
        trailing_optional = []
        trailing          = []

        def collect(into,predicate):
            for spec in specs:
                if predicate(spec):
                    into.append(spec)
                else:
                    specs.prepend(spec)
                    break

        collect( leading,          lambda spec: spec.is_posarg and not spec.is_optional and not spec.is_variadic)
        collect( leading_optional, lambda spec: spec.is_posarg and spec.is_optional and not spec.is_variadic)

        variadics = []
        collect(variadics, lambda spec: spec.is_variadic or spec.is_marker )
        assert len(variadics) <= 1, "maximal one variadic spec allowed here, got: "+str(variadics)
        if len(variadics) == 0:
            variadic = None
        else:
            variadic = variadics[0]

            if variadic == no_variadic:
                variadic = None
            else:
                assert variadic.is_variadic, "only variadic or no_variadic marker allowed here"
        
        collect( trailing_optional, lambda spec: spec.is_posarg and spec.is_optional and not spec.is_variadic)
        collect( trailing,          lambda spec: spec.is_posarg and not spec.is_optional and not spec.is_variadic)

        return Struct(
            leading           = leading,
            leading_optional  = leading_optional,
            variadic          = variadic,
            trailing_optional = trailing_optional,
            trailing          = trailing
        )

    def parse(self,tokens):
        return self.parser.parse(tokens)

# **  Plain Command

class CommandSpecification(CommandLineSpecificationBase):

    ParserType = CommandParser
    
    def __init__(self,specs):
        self.specs = specs   # use local only
        specs = peekable(specs) 
        self.options = self.get_option_specs(specs)

        spec = specs.peek(None)
        
        if spec == None:
            self.posargs = Struct(leading=[],leading_optional=[],variadic=None,trailing=[],trailing_optional=[])
        else:
            assert spec.is_posarg, "options not followed by positional parameters"
            self.posargs = self.get_posarg_specs(specs)
            assert specs.peek(None) == None, "positional parameters followed by other stuff, expected list end here"

        self.parser = self.ParserType(self.options,self.posargs)


# **  Command Package

class CommandPackageSpecification(CommandLineSpecificationBase):

    def __init__(self,options_spec, subcommands_spec):
        
        self.options     = maybe_to_specmap(options_spec)
        self.subcommands = maybe_to_specmap(subcommands_spec)
        
        self.parser = SubcommandPackageParser(self.options,self.subcommands)


class SubcommandParser( MergeArguments, CommandParser ):
    pass

class SubcommandSpecification(CommandSpecification):
    ParserType = SubcommandParser
        
# ** ---

class CommandLineSpecificationUNUSED(object):

    contains_subcommands = False
    
    
    def __init__(self,specs):
        self.specs = specs   # use local only
        specs = peekable(specs) 

        self.options = self.get_option_specs(specs)

        spec = specs.peek(None)

        if spec != None:
            if spec.is_posarg:
                self.posargs = self.get_posarg_specs(specs)
            else:            
                assert spec.is_subcommand, "client error: subcommand or posarg expected after options"            
                self.contains_subcommands = True
                self.subcommands = self.get_subcommand_specs(specs)
        else:
            self.posargs = [[],[],None,[],[]]

        assert specs.peek(None) == None, "trailing specifications after posargs or subcommands"
            
    @staticmethod
    def get_option_specs(specs):
        options = []
        for spec in specs:
            if spec.is_option:
                options.append(spec)
            else:
                assert spec.is_marker or spec.is_posarg or spec.is_subcommand
                specs.prepend(spec)
                break
        return options

    @staticmethod
    def get_subcommand_specs(specs):
        subcommands = []
        for spec in specs:
            if spec.is_subcommand:
                subcommands.append(spec)
            else:
                assert False, "client error: subcommands should be last in list"
        return subcommands

    @staticmethod
    def map_from_specs(specs,keys = lambda obj: obj.keys):

        map = {}

        for spec in specs:
            spec_keys = keys(spec)
            for key in spec_keys:
                assert not key in map, "duplicate key {KEY!r} from spec {SPEC!r}\nspecs => {SPECS}".format(KEY=key,SPEC=spec,SPECS=specs)
                map[key] = spec
        return map

    @classmethod
    def map_from_option_specs(cls,specs): return cls.map_from_specs(specs,(lambda obj: obj.labels))

    @classmethod
    def map_from_subcommand_specs(cls,specs): return cls.map_from_specs(specs,(lambda obj: obj.commands))    

    @classmethod
    def get_posarg_specs(cls,specs):
        leading           = []
        leading_optional  = []
        variadic          = None
        trailing_optional = []
        trailing          = []

        def collect(into,predicate):
            for spec in specs:
                if predicate(spec):
                    into.append(spec)
                else:
                    specs.prepend(spec)
                    break

        collect( leading,          lambda spec: spec.is_posarg and not spec.is_optional and not spec.is_variadic)
        collect( leading_optional, lambda spec: spec.is_posarg and spec.is_optional and not spec.is_variadic)

        variadics = []
        collect(variadics, lambda spec: spec.is_variadic or spec.is_marker )
        assert len(variadics) <= 1, "maximal one variadic spec allowed here, got: "+str(variadics)
        if len(variadics) == 0:
            variadic = None
        else:
            variadic = variadics[0]

            if variadic == no_variadic:
                variadic = None
            else:
                assert variadic.is_variadic, "only variadic or no_variadic marker allowed here"
        
        collect( trailing_optional, lambda spec: spec.is_posarg and spec.is_optional and not spec.is_variadic)
        collect( trailing,          lambda spec: spec.is_posarg and not spec.is_optional and not spec.is_variadic)

        return leading,leading_optional,variadic,trailing_optional,trailing



