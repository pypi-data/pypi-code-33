# * Copyright (C) 2018 M E Leypold, GPL3-or-later licensed -----------------------|
#
#     greenland.cmdline.shellcommands -- CLIs to single procedures
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

from .specification2 import Option,Flag,Required,Optional,no_variadic, Variadic
from greenland.conventions import UserError
from .parsers import append_to_list, add_to_set

# *   Metaclass  -------------------------------------------------------------------|

class ShellCommandMeta(type):
        
    def __init__(cls,name,bases,namespace,*more):
        super().__init__(name,bases,namespace,*more)
        if 'usage' in namespace:
            from .specification2 import CommandSpecification
            cls.__cli__ = cli = CommandSpecification(namespace['usage'])
            

# *   ShellCommand  ----------------------------------------------------------------|
            
class ShellCommand(object,metaclass=ShellCommandMeta):

    def __init__(self,argv=None,run=True,exit_on_error=True):
        
        import sys
        from greenland.conventions import UserError, longstr
        from .parsers import CommandLine
        
        if argv == None: argv = sys.argv

        try:
            with CommandLine(argv) as tokens:
                options,posargs  = self.__cli__.parse(tokens)
                
            self.__argv__    = argv
            self.__posargs__ = posargs
                
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
        
        self.main(**self.__posargs__)

