"""
Provides a command-line based front-end.

This is only a simple front end for executing basic commands from the command line - for scripting, the Python Interactive Interface provides a similar interface with more features.
(Python Interactive is invoked by calling code.interact, see :function:`pyi`). 
"""
import builtins
import warnings
from typing import Dict, List, Optional, Union
from mhelper import FindError, file_helper, string_helper, SwitchError, ArgInspector, ArgsKwargs, ArgValueCollection

import os
import os.path
import re
import shlex
import sys

from intermake.engine import EImRunMode, Controller, Theme, Command, HelpTopic, Streaming, ExitUiError
from intermake.framework import console_configuration, readline_importer
import intermake.helpers.printing as pr


def find_command( text: str, plugin_type: type = None, include_topics: bool = False ):
    """
    Finds the command with the name.
    
    :param include_topics: 
    :param text: 
    :param plugin_type: 
    :return:
    :except FindError: Find failed. 
    """
    source_list = Controller.ACTIVE.app.commands
    
    if plugin_type:
        source_list = [x for x in source_list if isinstance( x, plugin_type )]
    
    if include_topics:
        source_list = list( source_list ) + list( Controller.ACTIVE.app.help )
    
    
    def ___get_names( x: Union[Command, HelpTopic] ):
        if isinstance( x, Command ):
            return x.names
        elif isinstance( x, HelpTopic ):
            return [x.key, x.name]
        else:
            raise SwitchError( "x", x, instance = True )
    
    
    return string_helper.find( source = source_list,
                               search = text,
                               namer = ___get_names,
                               detail = "command",
                               fuzzy = True )


class CliSyntaxError( Exception ):
    """
    Syntax error of the CLI.
    """
    pass


RX_ARG_TEXT = re.compile( " *([a-zA-Z0-9_.]+) *=(.+) *" )


def __execute_command( arguments: List[str] ) -> None:
    """
    Executes a command
    
    :param arguments: See `Plugins.Commands.general_help()` for a description of what is parsed. 
    """
    # No arguments means do nothing
    if len( arguments ) == 0 or (len( arguments ) == 1 and not arguments[0]):
        return
    
    # ":" and "then" mean we will perform 2 commands, so split about the ":" and repeat
    delimiters = (":", "then")
    
    for delimiter in delimiters:
        if delimiter in arguments:
            i = arguments.index( delimiter )
            left = arguments[0:i]
            right = arguments[(i + 1):]
            __execute_command( left )
            __execute_command( right )
            return
    
    # Get the command name (first argument)
    cmd = arguments[0]
    
    arguments = arguments[1:]
    
    # Find the plugin we are going to run
    try:
        plugin: Command = find_command( cmd )
    except FindError as ex:
        raise CliSyntaxError( "The command «{}» is not recognised - use «cmdlist» to list the available commands.".format( cmd ) ) from ex
    
    # Create the parameters
    args = []  # type: List[Optional[object]]
    kwargs = { }  # type: Dict[str,Optional[object]]
    
    ui = Controller.ACTIVE
    
    for arg_text in arguments:
        # "=" means a keyword argument
        match = RX_ARG_TEXT.match( arg_text )
        if match is not None:
            k = match.group( 1 )
            v = match.group( 2 )
            
            if k in kwargs:
                raise CliSyntaxError( "The key «{0}» has been specified more than once.".format( k ) )
            
            try:
                plugin_arg: ArgInspector = string_helper.find(
                        source = plugin.args,
                        search = k,
                        namer = lambda x: [x.name],
                        detail = "argument" )
            except FindError as ex:
                raise CliSyntaxError( "{}. Command = {}.".format( ex, plugin ) ) from ex
            
            if plugin_arg is None:
                raise CliSyntaxError( "The plugin «{}» does not have an argument named «{}» or similar. The available arguments are: {}".format( plugin.name, k, ", ".join( x.name for x in plugin.args ) ) )
            
            kwargs[plugin_arg.name] = __convert_string( ui, plugin_arg, plugin, v )
        else:
            # Everything else is a positional argument
            if kwargs:
                raise CliSyntaxError( "A positional parameter (in this case «{0}») cannot be specified after named parameters.".format( arg_text ) )
            
            if len( args ) == len( plugin.args ):
                raise CliSyntaxError( "Too many arguments specified for «{}», which takes {}.".format( plugin, len( plugin.args ) ) )
            
            plugin_arg = plugin.args[len( args )]
            
            args.append( __convert_string( ui, plugin_arg, plugin, arg_text ) )
    
    ui.acquire( plugin ).run( *args, **kwargs )


def __convert_string( ctrl: Controller, arg: ArgInspector, command: Command, value: str ):
    value = string_helper.unescape( value )
    
    try:
        result = ctrl.coercers.coerce( arg.annotation.value, value )
        return result
    except Exception as ex:
        raise CliSyntaxError( "Value «{}» rejected for argument «{}» on command «{}» because «{}». See causing error for further details.".format( value, arg.name, command, ex ) ) from ex


def start_cli( mode: str ) -> None:
    """
    Starts the CLI frontend.
    
    This operates in two modes, the first reads the command line arguments from `sys.argv`, and the second takes user input using `input`.
    
    Generally the host will be a `ConsoleController` instance, though other hosts are tolerated.
    
    :param mode: Execution mode.
    """
    from intermake import commands
    readline_importer.initialise_readline()
    
    assert mode in (EImRunMode.ARG, EImRunMode.CLI, EImRunMode.IPYI)
    
    # Run the startup arguments
    queue = []
    
    config = console_configuration.current
    
    if mode == EImRunMode.ARG:
        for index, arg in enumerate( sys.argv[1:] ):
            if index == 0 and arg in ("--help", "-help", "/help", "-?", "/?"):
                queue.append( "help" )
            elif arg.startswith( "--" ):
                queue.append( ":" )
                queue.append( arg[2:] )
            else:
                queue.append( arg )
        
        if len( queue ) > 1:
            queue = [" ".join( '"{}"'.format( x ) if " " in x else x for x in queue )]
        
        if not queue:
            commands.start_ui( config.default_ui or EImRunMode.PYI, force = True )
            return
    
    try:
        while True:
            #
            # Reset the state of the output parser
            #
            Streaming.INSTANCE.get_target().reset()
            
            if mode == EImRunMode.ARG:
                if not queue:
                    if config.always_start_ui:
                        commands.start_ui( config.always_start_ui, force = True )
                    
                    raise ExitUiError( "All arguments parsed." )
                
                x = queue.pop( 0 )
            else:
                x = __prompt_for_input()
            
            safe_execute_text( x, mode )
    finally:
        if not queue:
            readline_importer.write_history()


def safe_execute_text( x, mode: str ):
    from intermake import commands
    config = console_configuration.current
    
    read_argv = mode == EImRunMode.ARG
    
    try:
        if mode == EImRunMode.IPYI:
            r = eval( x, _PyiCommandWrapper.get_dict( Controller.ACTIVE.app ) )
            
            if r is not None:
                print( r )
        elif mode in (EImRunMode.CLI, EImRunMode.ARG):
            execute_text( x )
        else:
            raise SwitchError( "mode", mode )
    except KeyboardInterrupt as ex:
        pr.printx( "<system>" )
        pr.printx( "<warning>KEYBOARD INTERRUPT - OUTPUT MAY BE INCOMPLETE</warning>" )
        pr.printx( "</system>" )
        
        if config.error_traceback or config.error_traceback or read_argv:
            pr.printx( "<system>" + pr.fmt_traceback( ex ) + "</system>" )
    except Exception as ex:
        pr.printx( "<system>" )
        pr.printx( "<warning>AN ERROR OCCURRED - OUTPUT MAY BE INCOMPLETE</warning>" )
        
        if config.error_traceback or config.error_traceback or read_argv:
            pr.printx( pr.fmt_traceback( ex ) )
        
        ex_msg = pr.escape( type( ex ).__name__ + ": " + str( ex ) )
        ex_msg = string_helper.highlight_quotes( ex_msg, "«", "»", "<code>", "</code>" )
        pr.printx( "<error>" + ex_msg + "</error>" )
        
        if read_argv and config.error_starts_ui:
            pr.printx( "Note: An error has occurred. Now starting {} because `error_starts_ui` is set.".format( config.error_starts_ui ) )
            commands.start_ui( config.error_starts_ui, force = True )
        else:
            pr.printx( "</system>" )


def __prompt_for_input():
    # Redirect STDOUT to __STDOUT__, this is required for `readline` to function
    
    try:
        # Write the prompt
        sys.__stderr__.write( Theme.PROMPT )
        prompt = str( INTERMAKE_PROMPT )
        
        # Read the input (we handle this differently on Windows)
        if file_helper.is_windows():
            sys.__stderr__.write( prompt )
            return input()
        else:
            return input( prompt )
    except ValueError as ex:
        # Another end of file
        raise ExitUiError( str( ex ) )
    except EOFError:
        # End of file
        raise ExitUiError( "End of standard input" )
    except KeyboardInterrupt:
        # User quits
        sys.__stderr__.write( "(Keyboard quit)\n" )
        raise ExitUiError( "Keyboard quit" )
    finally:
        # Restore the style and stdout
        sys.__stderr__.write( Theme.RESET )
        sys.__stderr__.flush()


def execute_text( x ) -> None:
    if x.startswith( "#" ):
        return
    
    if "\033" in x:
        raise ValueError( "Refusing to process a command containing an escape sequence." )
    
    # Environment variable replacement
    for k, v in os.environ.items():
        x = x.replace( "$(" + k + ")", v )
    
    # Quick help
    if x.startswith( "?" ) or x.endswith( "?" ):
        x = x.strip( "? \t" )
        
        user_commands = shlex.split( x )
        cmds = ["help"]
        
        if len( user_commands ) >= 1:
            cmds += [user_commands[0]]
        
        if len( user_commands ) >= 2:
            cmds += [user_commands[-1]]
    else:
        try:
            cmds = shlex.split( x )
        except Exception as ex:
            raise SyntaxError( "Not processing this because it isn't valid command string: {}".format( x ) ) from ex
    
    __execute_command( cmds )


class _IntermakePrompt:
    def __str__( self ):
        return repr( self )
    
    
    def __repr__( self ):
        from intermake.framework.console_controller import ConsoleController
        active_ui = Controller.ACTIVE
        
        if isinstance( active_ui, ConsoleController ):
            return active_ui.get_prompt()
        else:
            return "$" + str( active_ui ) + "$"


INTERMAKE_PROMPT: _IntermakePrompt = _IntermakePrompt()


class _PyiCommandWrapper:
    """
    ************************************************************************************************************
    ************************************************************************************************************
    ***                                                                                                      ***
    *** This wrapper item calls a pre-specified function and executes it using the current user interface.   ***
    ***                                                                                                      ***
    *** It also coerces any string arguments into types actually expected by the function.                   ***
    ***                                                                                                      ***
    *** For more help on the specific function that this instance calls, use the `.help()` method.           ***
    ***                                                                                                      ***
    ************************************************************************************************************
    ************************************************************************************************************
    """
    
    
    @classmethod
    def get_dict( cls, app ) -> Dict[str, object]:
        """
        Returns a dictionary of the commands wrapped in "_PyiCommandWrapper" instances.
        """
        from intermake.engine.abstract_command import Command
        
        r: Dict[str, _PyiCommandWrapper] = { }
        
        #
        # Names to avoid overriding, we don't want to override `exit` but we do want to
        # override `help`.
        #
        avoid = [x for x in dir( builtins ) if not x.startswith( "_" )]
        avoid.remove( "help" )
        nwarn = ["help", "exit", "quit"]
        
        for command in app.commands:
            assert isinstance( command, Command )
            
            for n in command.names:
                if n in avoid:
                    on = n
                    n = app.name.lower() + "_" + n
                    if on not in nwarn:
                        warnings.warn( "The application command '{}' conflicts with a Python builtin of the same name. The application command has been renamed '{}'."
                                       .format( on, n ) )
                
                r[n] = _PyiCommandWrapper( command )
        
        return r
    
    
    def __init__( self, command: Command ):
        """
        Constructs a bew wrapper for the specified command. 
        """
        self.command = command
    
    
    def __call__( self, *args, **kwargs ):
        """
        Calls through to the command.
        """
        avc: ArgsKwargs = ArgValueCollection( self.command.args, read = ArgsKwargs( *args, **kwargs ), coerce = self.__coerce ).to_argskwargs()
        Controller.ACTIVE.acquire( self.command ).run( *avc.args, **avc.kwargs )
    
    
    def __coerce( self, arg: ArgInspector, value: object ) -> object:
        if isinstance( value, str ):
            import stringcoercion
            value = stringcoercion.coerce( arg.annotation.value, value )
        
        return value
    
    
    def __repr__( self ):
        """
        The string representation of this object is help describing how to call it. 
        """
        return "( This is a command named '{0}'. Please type '{0}()' to execute this command, or type '{0}.help()' for more information. )".format( self.command.name )
    
    
    def help( self ):
        """
        Shows help on the command.
        """
        from intermake import commands
        commands.print_help( self.command.name )
