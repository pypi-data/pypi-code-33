"""
This module holds the Intermake common command set.

All functions here are decorated with `@app.command`, which allows them to be passed as command line arguments to the application.
See `@app.command` for more details.
"""
import inspect
import os
import sys
import warnings

from os import path

from typing import Optional, Set, List, Union, Callable

from mhelper import ArgInspector, EFileMode, isFilename, LOGGERS, isOptional, file_helper, io_helper, string_helper, Documentation, markdown_helper, NOT_PROVIDED, array_helper, exception_helper

from intermake.commands import visibilities
from intermake.framework import BasicCommand, SetterCommand
from intermake.engine import Command, Result, Application, HelpTopic, ExitUiError, Controller, EImRunMode, Visibility
from intermake.framework import console_parser as command_line, app as app, console_configuration, readline_importer
import intermake.helpers.printing as pr


__folder = "CLI"
__EXT_IMK = ".imk"


@app.command( names = ["exit", "x", "quit", "q", "bye", "exit_controller"], visibility = visibilities.CLI, highlight = True, folder = __folder )
def exit_controller( force: bool = False ) -> None:
    """
    Exits the program safely.
    
    Note that pressing `CTRL+C` in the CLI will also exit the program safely.
    If a command is running, then `CTRL+C` will stop that command and return you to the CLI.
    
    :param force: Force-quits the program.  
    """
    if force:
        sys.exit( 1 )
    else:
        raise ExitUiError( "User requested exit" )


@app.command( names = ["error", "print_error"], visibility = visibilities.CLI & visibilities.ADVANCED, folder = __folder )
def print_error() -> None:
    """
    Displays the details of the previous result.
    """
    # Get the last result (that wasn't a call to this function!)
    active_ui = Controller.ACTIVE
    result: Result = None
    
    for x in reversed( active_ui.result_history ):
        if x.command is not BasicCommand.retrieve( print_error ):
            result = x
            break
    
    if result is None:
        return
    
    # Format and print the result
    r = []
    
    r.append( "LAST RESULT" )
    r.append( "    source    = {}({})".format( type( result.command ).__name__, repr( result.command.name ) ) )
    r.append( "    args      = {}".format( repr( result.args ) ) )
    r.append( "    result    = {}".format( result.state ) )
    
    if result.is_error:
        r.append( "    exception = {}".format( repr( result.exception ) ) )
        r.append( "    traceback =\n{}".format( result.traceback ) )
    else:
        r.append( "    value     = {}".format( result.result ) )
    
    pr.pr_information( "\n".join( r ) )


@app.command( names = ["use", "toggle_command_set"], folder = __folder )
def toggle_command_set( category: Optional[str] = None, all: bool = False ) -> None:
    """
    Shows or hides command sets.

    :param all:      When listing the available modes, setting this flag shows all classes, even if they appear to be non-functional.
    :param category: Mode to show or hide. Leave blank to list the available modes. If this is an asterisk (`*`) then all modes are set to visible.
    """
    
    #
    # Get the set of available visibilities
    #
    available: Set[Visibility] = set()
    
    for command in Controller.ACTIVE.app.commands:
        command_visibilities = { command.visibility_class }
        
        while command_visibilities:
            available.update( command_visibilities )
            
            new_visibilities = set()
            
            for visibility in command_visibilities:
                if visibility.parents:
                    for parent in visibility.parents:
                        new_visibilities.add( parent )
            
            command_visibilities = new_visibilities
    
    #
    # Show the status of the visibilities
    #
    orig = set( cmd for cmd in Controller.ACTIVE.app.commands if cmd.is_visible )
    done = False
    
    for visibility in available:
        if category == "*":
            visibility.user_override = True
            pr.printx( "<positive>{}</positive> is now shown ".format( visibility.name ) )
            done = True
        elif visibility.name == category:
            if visibility.user_override is True:
                visibility.user_override = False
                pr.printx( "<negative>{}</negative> is now hidden ".format( visibility.name ) )
                done = True
                break
            elif visibility.user_override is False:
                visibility.user_override = None
                pr.printx( "<neutral>{}</neutral> has been reset to its default ({})".format( visibility.name, "shown" if visibility.is_visible else "hidden" ) )
                done = True
                break
            else:
                visibility.user_override = True
                pr.printx( "<positive>{}</positive> is now shown.".format( visibility.name ) )
                done = True
                break
    
    if done:
        new = set( cmd for cmd in Controller.ACTIVE.app.commands if cmd.is_visible )
        shown = new - orig
        hidden = orig - new
        
        if shown:
            pr.printx( "The following commands are now visible: {}".format( ", ".join( "<command>{}</command>".format( x ) for x in shown ) ) )
        
        if hidden:
            pr.printx( "The following commands are now hidden: {}".format( ", ".join( "<command>{}</command>".format( x ) for x in hidden ) ) )
        
        if not shown and not hidden:
            pr.printx( "No new commands available" )
        
        return
    
    r = [["Visible", "Mode", "Description"]]
    
    for visibility in sorted( available, key = lambda x: x.name ):
        if not visibility.is_useful and not all and category != "*":
            continue
        
        shown = visibility.is_visible
        r.append( ["[ yes ]" if shown else "[     ]",
                   pr.escape( visibility.name.ljust( 20 ) ),
                   pr.escape( visibility.comment )] )
    
    pr.pr_table( r, escape = False )


@app.command( names = ["cmdlist", "cl", "print_command_list"], visibility = visibilities.CLI & visibilities.ADVANCED, highlight = True, folder = __folder )
def print_command_list( all: bool = False ) -> None:
    """
    Lists the available commands.

    =============== ================================================================================
    Mode            Example
    =============== ================================================================================
    CLI             cmdlist
    Python          intermake.cmdlist()
    GUI             The GUI lists all commands in the main window, so you don't need to do this.
    =============== ================================================================================

     :param all: When `True`, all commands are shown, regardless of their visibility.
     """
    
    if all:
        print_help( "all_commands" )
    else:
        print_help( "commands" )


@app.command( names = ["eggs", "example"], visibility = visibilities.ADVANCED, folder = __folder )
def eggs( name: str = "no name", good: bool = False, repeat: int = 1 ) -> None:
    """
    Egg-sample command :)
    Prints a message.
     
    :param name:    Name of your egg-sample 
    :param good:    Is this a good egg-sample?
    :param repeat:  Number of times to repeat the egg-sample.
    """
    for _ in range( repeat ):
        pr.printx( "This is an example command. <key>{}</key> is a <value>{}</value> egg-sample.".format( name, "GOOD" if good else "BAD" ) )


@app.command( names = ["python_help", "invoke_python_help"], visibility = visibilities.ADVANCED, folder = __folder )
def invoke_python_help( thing: object = None ) -> None:
    """
    Shows Python's own help.

    :param thing: Thing to show help for, leave blank for general help.
    """
    import pydoc
    
    if thing is None:
        pydoc.help()
    else:
        pydoc.help( thing )


@app.command( names = ["print_history", "history"], visibility = visibilities.ADVANCED, folder = __folder )
def print_history( find: str = "" ):
    """
    Prints CLI history.
    :param find:    If specified, only lists lines containing this text
    """
    r = []
    for line in readline_importer.iter_history():
        if find in line:
            r.append( line )
    
    pr.pr_information( "\n".join( r ) )


in_help = False


def __get_details_text( command: Command ) -> str:
    """
    Gets the help text of the specified `Command`, formatted for display in the CLI and returned as a single string.
    """
    result = []
    __get_details( result, command )
    return "\n".join( result )


def __get_details( result: List[str], command: Command ) -> None:
    """
    Gets the help text of the specified `Command`, formatted for display in the CLI and returned as a list of lines.
    """
    
    name: str = command.name
    
    result.append( "<section name='COMMAND: {}'>".format( name ) )
    
    result.append( "<verbose>Command line aliases: {}</verbose>".format( ", ".join( command.names ) ) )
    
    command_name = name
    
    if isinstance( command, BasicCommand ):
        command_name = command.function.__name__
        result.append( "<verbose>Python aliases      : {}</verbose>".format( command.function.__module__ + "." + command.function.__name__ ) )
    
    args = []
    
    for arg in command.args:
        n = arg.name
        
        if args:
            n = ", " + n
        
        if arg.default is NOT_PROVIDED:
            args.append( n )
        else:
            args.append( "[" + n + "]" )
    
    arg_text = "".join( args )
    
    if len( arg_text ) > 100:
        arg_text = "&lt;arguments&gt;"
    
    result.append( "<verbose>Command line usage  : {} {} {}</verbose>".format( Controller.ACTIVE.app.name, name, arg_text.replace( "[, ", " [" ).replace( ",", "" ) ) )
    result.append( "<verbose>Python usage        : {}( {} )</verbose>".format( command_name, arg_text ) )
    result.append( "" )
    
    #
    # DESCRIPTION
    #
    desc = command.documentation
    desc = __format_doc( desc )
    result.append( desc )
    result.append( "" )
    
    #
    # ARGUMENTS
    #
    extra: str = None
    
    result.append( "<table>" )
    result.append( pr.fmt_row( ["argument", "type", "default", "description"] ) )
    
    for i, arg in enumerate( command.args ):
        arg: ArgInspector = arg
        desc = __format_doc( arg.description )
        t = arg.annotation
        
        viable_subclass_type = array_helper.first_or_none( t.get_indirect_subclass( x ) for x in __iter_enumerative_types() )
        
        if viable_subclass_type is not None:
            desc += "‡"
            for k in viable_subclass_type.__dict__.keys():
                if not k.startswith( "_" ):
                    desc += "\n" + " * <value>{}</value>".format( k )
            
            if not extra:
                extra = arg.name
        
        # Arg type
        if t.is_optional:
            v = arg.annotation.optional_value
            t = "{}/none"
        else:
            v = t.value
            t = "{}"
        
        t = t.format( v.__name__.lower() if isinstance( v, type ) and len( v.__name__ ) < 10 else "obj" )
        
        # Default
        d = arg.default
        
        if isinstance( d, str ):
            d = '"{}"'.format( d )
        elif d is NOT_PROVIDED:
            d = "-"
        else:
            d = str( d )
        
        if len( d ) > 10:
            d = "..."
        
        result.append( pr.fmt_row( [pr.escape( arg.name ),
                                    pr.escape( t ),
                                    pr.escape( d ),
                                    desc],
                                   escape = False ) )
    
    result.append( "</table>" )
    
    if extra:
        result.append( "" )
        result.append( "<verbose>"
                       "‡ Specify the argument when you call <command>help</command> "
                       "to obtain the full details for these values. E.g. “"
                       "<command>help {} {}</command>”."
                       "</verbose>".format( command.name, extra ) )
        result.append( "" )
    
    result.append( "</section>" )


def __format_doc( doc: str ) -> str:
    """
    Formats markdown.
    
    :param doc:        Restructured text.
    :return:           Formatted text.
    """
    if doc is None:
        doc = ""
    
    doc = doc.strip()
    doc = markdown_helper.markdown_to_sxs( doc )
    return doc.strip()


@app.command( highlight = True, names = ["help", "h", "print_help"], folder = __folder, visibility = visibilities.CLI )
def print_help( command: Optional[Union[str, Callable, Command, HelpTopic]] = None, argument: Optional[str] = None ) -> None:
    """
    Shows general help or help on a specific command.
     
    :param command:     A `Command`, `HelpTopic`, `Callable` bound to a command, or the name (`str`)
                        of a `Command` or `HelpTopic`.
                        If not specified then the list of help topics is shown.
    :param argument:    If a `Command` is specified, the name of the argument to get detailed help
                        for. If this is not specified then help for the command itself is given.
                        `argument` is unused if `command` references a `HelpTopic` rather than a
                        `Command`.
    """
    if command is None:
        command = "topics"
    
    if isinstance( command, str ):
        command_ = command_line.find_command( command, include_topics = True )
    elif inspect.isroutine( command ):
        command_ = BasicCommand.retrieve( command )
    elif isinstance( command, Command ):
        command_ = command
    elif isinstance( command, HelpTopic ):
        command_ = command
    else:
        raise exception_helper.type_error( "command", command, Optional[Union[str, Callable, Command, HelpTopic]] )
    
    if command_ is None:
        return
    
    r = []
    
    if isinstance( command_, HelpTopic ):
        r.append( "<section name='{}'>".format( command_.name ) )
        x = command_.to_html()
        x = x.replace( "|app_name|", Controller.ACTIVE.app.name )
        r.append( x )
        r.append( "</section>" )
    elif isinstance( command_, Command ):
        if not argument:
            r.append( __get_details_text( command_ ) )
        else:
            argument_: ArgInspector = string_helper.find(
                    source = command_.args,
                    namer = lambda x: [x.name],
                    search = argument,
                    detail = "argument" )
            
            t = argument_.annotation.get_indirect_subclass( object )
            
            if t is None:
                raise ValueError( "Cannot obtain type above object from «{}».".format( argument_.annotation ) )
            
            r.append( "<table>" )
            r.append( "<tr><td>{}</td><td>{}</td></tr>".format( "name", argument_.name ) )
            r.append( "<tr><td>{}</td><td>{}</td></tr>".format( "type name", t.__name__ ) )
            r.append( "<tr><td>{}</td><td>{}</td></tr>".format( "optional", argument_.annotation.is_optional ) )
            r.append( "<tr><td>{}</td><td>{}</td></tr>".format( "default", argument_.default ) )
            r.append( "<tr><td>{}</td><td>{}</td></tr>".format( "description", argument_.description ) )
            r.append( "</table>" )
            
            # Type docs
            docs = Documentation( t.__doc__ )["cvar"]
            r.append( docs.get( "", "" ) )
            
            rows = ([["value", "comments"]] +
                    [[key, value] for key, value in docs.items() if key and value])
            
            r.append( pr.fmt_table( rows ) )
    
    pr.printx( "\n".join( r ) )


@app.command( names = ["version", "print_version"], visibility = visibilities.ADVANCED & visibilities.CLI, folder = __folder )
def print_version( stdout: bool = False ) -> None:
    """
    Shows the application version.
    
    :param stdout: Print to std.out.
    """
    if stdout:
        pr.pr_information( Controller.ACTIVE.app.version )
    else:
        name = Controller.ACTIVE.app.name
        version = Controller.ACTIVE.app.version
        pr.pr_information( name + " " + version )


@app.command( names = ["cls", "clear", "clear_screen"], visibility = visibilities.ADVANCED, folder = __folder )
def clear_screen() -> None:
    """
    Clears the CLI.
    """
    io_helper.system_cls()


@app.command( names = ["gui", "start_gui"], visibility = visibilities.ADVANCED, folder = __folder )
def start_gui() -> None:
    """
    Starts the GUI. See `start_ui` for more details.
    """
    start_ui( EImRunMode.GUI )


@app.command( names = ["cli"], folder = __folder, visibility = visibilities.ADVANCED )
def start_cli() -> None:
    """
    Starts the CLI. See `start_ui` for more details.
    """
    start_ui( EImRunMode.CLI )


@app.command( names = ["pyi", "start_pyi"], visibility = visibilities.ADVANCED, folder = __folder )
def start_pyi() -> None:
    """
    Starts the Python Interactive Shell. See `start_ui` for more details.
    """
    start_ui( EImRunMode.PYI )


@app.command( names = ["debug"], folder = __folder )
def start_debug( persist: bool = False ):
    """
    This command behaves the same as `start_ui pyi`, but it first loads the
    Intermake debug and testing libraries, and ensures the error traceback is
    enabled.
    
    :param persist: Persist debug settings after application restart.
    """
    import_python_module( "intermake_debug", persist = persist )
    import_python_module( "intermake_test", persist = persist )
    console_configuration.ephemeral.error_traceback = True
    
    if persist:
        console_configuration.saved.error_traceback = True
    
    start_cli()


@app.command( names = ["ui", "start_ui"], visibility = visibilities.ADVANCED, folder = __folder )
def start_ui( mode: str = "", force: bool = False ) -> None:
    """
    Switches the user-interface mode.
    
    
    
    :param mode: UI to use.
                 Which UIs are available depends on the application.
                 The basic UIs are: 
                 * 'arg', 'cli', 'pyi', 'pys', 'gui', 'jup'
                 These UIs are usually provided by the application,
                 prefixing the names with `intermake_` uses the base version. 
    :param force:   If this command is executed as one of the command-line arguments, the designated
                    UI is started after all other command line arguments have been parsed, or if an
                    error occurs. Enabling this flag starts the UI immediately. Other commands
                    will be executed after the UI exits. This flag is meaningless if this command
                    is not executed from the command-line.
    """
    if not mode:
        pr.pr_information( "The currently active UI is {}.".format( Controller.ACTIVE ) )
        return
    
    if Controller.ACTIVE.mode != EImRunMode.ARG or force:
        Controller.ACTIVE.app.create_controller( mode ).start()
    else:
        console_configuration.ephemeral.always_start_ui = mode
        console_configuration.ephemeral.error_starts_ui = mode


class __LocalDataCommand( SetterCommand ):
    """
    Calling this command with no arguments displays the current settings.
    Passing arguments to this command modifies those settings. 

    .. note::
    
        If using Python, the data store can also be accessed directly::
    
            intermake.Controller.Active.app.local_data.bind( "console" ).error_traceback = True
            
        Please see `intermake.Application.local_data` for more information. 
    """
    
    
    def on_get_targets( self ):
        return Controller.ACTIVE.app.local_data.iter_load_all( from_file = True )
    
    
    def on_set_target( self, name: str, target: object ):
        Controller.ACTIVE.app.local_data.commit( name, target )


configure = __LocalDataCommand( names = ["configure"], visibility = visibilities.ADVANCED, folder = __folder )
Application.LAST.commands.register( configure )


@app.command( names = ["workspace"], visibility = visibilities.ADVANCED, folder = __folder )
def change_workspace( directory: Optional[str] = None ) -> None:
    """
    Gets or sets the $(APP_NAME) workspace (where settings and caches are kept)
     
    :param directory:   Directory to change workspace to. This will be created if it doesn't exist. The workspace will take effect from the next $(APP_NAME) restart. 
    """
    pr.pr_information( "WORKSPACE: " + Controller.ACTIVE.app.local_data.workspace )
    
    if directory:
        Controller.ACTIVE.app.local_data.set_redirect( directory )
        pr.pr_information( "Workspace will be changed to «{}» on next restart.".format( directory ) )


@app.command( names = ["import"], visibility = visibilities.ADVANCED, folder = __folder )
def import_python_module( name: str, persist: bool = False, remove: bool = False ) -> None:
    """
    Wraps the python `import` command, allowing external sets of commands to be imported.
    
    :param name:    Name of the package to import.
    :param persist: Always import this command when the application starts.
    :param remove:  Undoes a `persist`. 
    """
    if remove:
        Controller.ACTIVE.app._environment_settings.startup.remove( name )
        Controller.ACTIVE.app.local_data.commit( Controller.ACTIVE._environment_settings )
        pr.printx( "<verbose><code>{}</code> will <em>not</em> be loaded at startup.</verbose>".format( name ) )
        return
    
    old_count = set( Controller.ACTIVE.app.commands )
    __import__( name )
    new_count = set( Controller.ACTIVE.app.commands )
    
    pr.printx( "<verbose>Import <code>{}</code> OK.</verbose>".format( name ) )
    
    if old_count != new_count:
        diff = new_count - old_count
        pr.printx( "<verbose>{} new commands: {}</verbose>".format( len( diff ), ", ".join( x.name for x in diff ) ) )
    
    if persist:
        Controller.ACTIVE.app._environment_settings.startup.add( name )
        Controller.ACTIVE.app.local_data.commit( Controller.ACTIVE.app._environment_settings )
        pr.printx( "<verbose><code>{}</code> will be loaded at startup.<verbose>".format( name ) )


@app.command( names = ["messages"], visibility = visibilities.ADVANCED, folder = __folder )
def print_messages( file: isOptional[isFilename[EFileMode.WRITE]] = None ) -> None:
    """
    Repeats the last output messages.
    
    :param file:    See `file_write_help`.
    """
    if not Controller.ACTIVE.result_history:
        warnings.warn( "No last result to print." )
        return
    
    last_result = Controller.ACTIVE.result_history[-1]
    
    with io_helper.open_write( file ) as file_out:
        for message in last_result.messages:
            file_out.write( message + "\n" )


@app.command( names = ["log"], visibility = visibilities.ADVANCED, folder = __folder )
def toggle_logging( name: Optional[str] = None ) -> None:
    """
    Enables, disables, or displays loggers.
    
    :param name:    Logger to enable or disable, or `None` to list all.
    """
    for logger in LOGGERS:
        if name == logger.name:
            if logger.enabled is False:
                logger.enabled = True
            elif logger.enabled is True:
                logger.enabled = False
            else:
                pr.pr_information( "Cannot change status because this logger has been bound to another destination." )
        
        pr.printx( "<key>{}</key> = <value>{}</value>", logger.name, logger.enabled )


@app.command( names = ["setwd", "chdir"], visibility = visibilities.ADVANCED, folder = __folder )
def change_working_directory( path: Optional[str] = None ) -> None:
    """
    Displays or sets the working directory.
    This is not the same as the `cd` command, which navigates |app_name|'s virtual object hierarchy.
    
    :param path:    Path to set.
    """
    if path:
        os.chdir( path )
    
    pr.pr_information( os.getcwd() )


@app.command( names = ["source"], visibility = visibilities.ADVANCED, folder = __folder )
def execute_cli_text( file_name: Union[str, isFilename[EFileMode.READ, __EXT_IMK]] ) -> None:
    """
    Executes a file using the command line interpreter.
    
    .. note::
        
        Writing a Python script is a better solution. 
    
    :param file_name:   File to execute.
    """
    if not path.isfile( file_name ):
        command_line.execute_text( file_name )
    else:
        for line in file_helper.read_all_lines( file_name ):
            command_line.execute_text( line )


def __show_help_formatting_types() -> str:
    """
    Displays help on formatting items
    """
    r = ["Use the following guide to determine how to specify various objects from the command line.",
         "In Python Interactive mode, these formats are also applicable, if you specify the parameter as a string.",
         ""]
    
    for coercer in Controller.ACTIVE.coercers:
        if coercer.__doc__:
            r.append( "* " + str( coercer.__doc__ ).strip() )
    
    return __format_doc( "\n".join( r ) )


app.help.add( "format", "How to specify various objects from the command line", __show_help_formatting_types )


# noinspection PyUnresolvedReferences
# noinspection PyPackageRequirements
def __iter_enumerative_types():
    try:
        from flags import Flags
        yield Flags
    except ImportError:
        pass
    
    try:
        from enum import Enum
        yield Enum
    except ImportError:
        pass
