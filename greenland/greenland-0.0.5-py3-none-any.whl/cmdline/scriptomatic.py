# * Copyright (C) 2018 M E Leypold, GPL3-or-later licensed  --------------------|
#
#     greenland.cmdline.scriptomatic -- CLIs to a single module level procedure
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

# * Scriptomatic  --------------------------------------------------------------|

from .specification2 import Option,Flag,Required,Optional,no_variadic, Variadic
from greenland.conventions import UserError, longstr
from .parsers import append_to_list, add_to_set

def run_script(namespace,argv=None,exit_on_error=True):
    
    import sys
    from .parsers       import CommandLine
    from .specification2 import CommandSpecification
    from greenland.toolbox.structs import Struct
    
    if argv == None: argv = sys.argv
    
    assert 'usage' in namespace, "scriptomatic script needs to contain variable 'usage'"
    cli = CommandSpecification(namespace['usage'])
    namespace['__cli__'] = cli

    try:
            
        with CommandLine(argv) as tokens:
            options,posargs = cli.parse(tokens)

        namespace['option']      = Struct(**options)
        namespace['__argv__']    = argv
        namespace['__posargs__'] = posargs

        namespace['main'](**posargs)
        
    except UserError as err:
        if exit_on_error:
            print(longstr(err))            
            exit(1)
        raise
        
