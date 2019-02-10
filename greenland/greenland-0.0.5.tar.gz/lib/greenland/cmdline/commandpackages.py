# * Copyright (C) 2018 M E Leypold, GPL3-or-later licensed -----------------------|
#
#     greenland.cmdline.commandpackages -- CLIs to command packages ("svn style" subcommands)
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

# *   Imports  ---------------------------------------------------------------------|

from .specification2 import Option,Flag,Required,Optional,no_variadic, Variadic, Subcommand
from greenland.conventions import UserError
from .parsers import append_to_list, add_to_set

# *   Metaclass  -------------------------------------------------------------------|

class CommandPackageMeta(type):

    @staticmethod
    def subcommand(namespace):
        def define(name,aliases=[],doc=None,usage=[]):
            def decorate(f):
                from .specification2 import SubcommandSpecification
                cli = SubcommandSpecification(usage)
                nonlocal namespace
                namespace['__subcommands__'].append(Subcommand(name,aliases,f,doc,cli.parser))
                return f
            return decorate
        return define

    @classmethod
    def __prepare__(mcls, name, bases, **kwds):
        namespace = type.__prepare__(name, name, bases, **kwds)
        namespace['__subcommands__'] = []
        namespace['subcommand'] = mcls.subcommand(namespace)
        return namespace
        
    def __init__(cls,name,bases,namespace,*more):
        super().__init__(name,bases,namespace,*more)


        try                  :  options = cls.options
        except AttributeError:  options = []
        
        try                  :  subcommands = cls.__subcommands__
        except AttributeError:  subcommands = None

        if subcommands != None:
            from .specification2 import CommandPackageSpecification
            cls.__cli__ = cli = CommandPackageSpecification(options,subcommands)
            

# *   CommandPackage  --------------------------------------------------------------|
            
class CommandPackage(object,metaclass=CommandPackageMeta):

    def __init__(self,argv=None,run=True,exit_on_error=True):
        
        import sys
        from greenland.conventions import UserError, longstr
        from .parsers import CommandLine
        
        if argv == None: argv = sys.argv
        self.__argv__    = argv
        
        try:
           with CommandLine(argv) as tokens:
               options,subcommand,args = self.__cli__.parse(tokens)

           self.__options__    = options
           self.__subcommand__ = subcommand
           self.__args__       = args

           self.set_options(**options)

           if run: self.run()

        except UserError as err:
            if exit_on_error:
                print(longstr(err))
                exit(1)
            raise

    def set_options(self,**options):
        from greenland.toolbox.structs import Struct

        try:
            name = self.option_struct
        except AttributeError:
            name = None

        if name != None:
            setattr(self,name,Struct(**options))
        else:
            self.__dict__.update(options)
        
    def run(self):
        self.__subcommand__.command(self,**self.__args__)
