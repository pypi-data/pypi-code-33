# * Copyright (C) 2018 M E Leypold, GPL3-or-later licensed ------------------------|
#
#   greenland.cmdline.mixins -- CLI mixin building blocks
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
Mix-In command line parsers and prefabricated parsers.
"""

# *  Imports  ---------------------------------------------------------------------|

from .parsers import BaseParser, OptionsAndPosArgsParser, PosArgsBinder, end_of_args, nothing, SubcommandsParser, OptionsParser

# *  Primitives -------------------------------------------------------------------|
# **  CheckEndOfArgs  -------------------------------------------------------------|

class CheckEndOfArgs(BaseParser):
    
    def __init__(self):
        super().__init__()

    def parse(self,tokens):
        end_of_args.parse(tokens)
        return []

# **  ParseOptionsAndPosArgs  -----------------------------------------------------|
    
class ParseOptionsAndPosArgs(BaseParser):
    def __init__(self):
        super().__init__()
        self.options_and_posargs_parser = OptionsAndPosArgsParser(self.options_spec)
            
    def parse(self,tokens):
        return list(self.options_and_posargs_parser.parse(tokens)) + super().parse(tokens)

# **  ParseOptions  ---------------------------------------------------------------|
    
class ParseOptions(object):
    def __init__(self):
        super().__init__()
        self.options_parser = OptionsParser(self.options_spec)        

    def parse(self,tokens):
        return [self.options_parser.parse(tokens)] + super().parse(tokens)        

# **  BindPosArgs  ----------------------------------------------------------------|
    
class BindPosArgs(BaseParser):
    def __init__(self):
        super().__init__()
        self.posargs_binder = PosArgsBinder(self.posargs_spec)

    def parse(self,tokens):
        options,posargs,*more = super().parse(tokens)
        posargs = self.posargs_binder.bind(posargs)
        # assert len(arguments.keys()&options.keys())==0,"specification error: overlapping keys" # should be able to detect earlier!
        # arguments.update(options)
        return [options,posargs] + more

# **  MergeArguments

class MergeArguments(BaseParser):
    
    def parse(self,tokens):
        options,posargs,*more = super().parse(tokens)
        arguments = {}
        assert len(posargs.keys()&options.keys())==0,"specification error: overlapping keys" # should be able to detect earlier!
        arguments.update(options)
        arguments.update(posargs)
        return [ arguments ] + more

# **  ParseSubcommand  ------------------------------------------------------------|
    
class ParseSubcommand(object):

    def __init__(self):
        super().__init__()
        self.subcommands_parser = SubcommandsParser(self.subcommands_spec)
        
    def parse(self,tokens):
        results = self.subcommands_parser.parse(tokens)        
        return list(results)+super().parse(tokens)
    
# *  CommandParser  ---------------------------------------------------------------|

class CommandParser(BindPosArgs,ParseOptionsAndPosArgs,CheckEndOfArgs):
    
    def __init__(self,options_spec,posargs_spec):
        self.options_spec = options_spec
        self.posargs_spec = posargs_spec
        super().__init__()

    
# *  SubcommandPackageParser  -----------------------------------------------------|

class SubcommandPackageParser(ParseOptions,ParseSubcommand,CheckEndOfArgs):
    def __init__(self,options_spec,subcommands_spec):
        self.options_spec     = options_spec
        self.subcommands_spec = subcommands_spec
        super().__init__()

    def parse(self,tokens):
        results = super().parse(tokens)
        assert len(results) >= 2
        return results

    
