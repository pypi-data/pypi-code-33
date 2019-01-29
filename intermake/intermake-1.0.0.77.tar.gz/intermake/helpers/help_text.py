from mhelper import string_helper

from intermake.engine.help import HelpTopic
from intermake.engine.collections import HelpTopicCollection
from intermake.engine.abstract_controller import EImRunMode


def add_to( collection: HelpTopicCollection ):
    for topic in __standard_help:
        collection.add( topic )


def __cmdlist_full() -> str:
    return __cmdlist( True )


def __cmdlist( all = False ) -> str:
    result = []
    
    from intermake.engine.abstract_controller import Controller, EImRunMode
    
    
    # Print the results
    
    last_parent = ""
    for command in sorted( Controller.ACTIVE.app.commands, key = lambda x: x.folder + "/" + x.name ):
        visible = command.visibility_class.is_visible
        
        if not visible and not all:
            continue
        
        if command.folder != last_parent:
            if last_parent:
                result.append( "</section>" )
            result.append( "<section name='{}'>".format( command.folder ) )
            last_parent = command.folder
        
        line = string_helper.first_line( command.documentation.strip() )
        name = command.name
        result.append( "<command>{}</command> {}- {}".format( name, "<i>(hidden)</i> " if not visible else "", line ) )
    
    result.append( "</section>" )
    
    if Controller.ACTIVE.mode == EImRunMode.PYS:
        result.append( "" )
        result.append( "<section name='********** NOTICE **********'>" )
        result.append( "The above list shows how to call the commands from |app_name|'s command line." )
        result.append( "You are presently using |app_name| from Python." )
        result.append( "|app_name|'s Python API should be obtained using Python's `dir` command." )
        result.append( "</section>" )
    
    result = "\n".join( result )
    return result


def __topics() -> str:
    from intermake.engine.abstract_controller import Controller
    m = Controller.ACTIVE.mode
    
    if m in (EImRunMode.PYI, EImRunMode.JUP):
        fmt = 'help( "{}" )'
    elif m == EImRunMode.ARG:
        fmt = Controller.ACTIVE.app.name + ' help {}'
    elif m == EImRunMode.CLI:
        fmt = 'help {}'
    else:
        fmt = '"{}"'
    
    return "".join( '\n* {} - {}'.format( fmt.format( x.key ).ljust( 30 ), x.name ) for x in Controller.ACTIVE.app.help )


__standard_help = (
    HelpTopic( "commands", "List of commands", __cmdlist ),
    HelpTopic( "all_commands", "List of all commands", __cmdlist_full ),
    HelpTopic( "topics", "List of help topics", __topics ),
    HelpTopic( "using_arg", "Using the application by passing command line arguments", """
            Commands can be specified on |app_name|'s command line.
            Syntax and operation are identical to the command line interactive mode,
            but the application quits after parsing all commands.
            
            Example:
            
                `|app_name| cmdlist`
                
            More information on the syntax is given in the help for command line
            interactive mode.
            """, format = "rst" ),
    HelpTopic( "using_cli", "Using the application in command line interactive mode", """
            |app_name| can operate in command line interactive mode.
            Syntax and operation are identical to passing command line arguments,
            but |app_name| keeps running to allow you to issue further
            commands.
            
            To start the application in this mode, pass the `cli` argument when
            starting it:
            
                `|app_name| cli`
                
            Example:

                `|app_name|`            
                `cmdlist`
                `exit`
            
            To see the list of commands type:
            
                `cmdlist`

            To run a command just type it, e.g. for the "eggs" command:

                `eggs`
                
            (You can abbreviate all commands, so you can also type `egg`)

            You can use `?` to get help on a command:

                `eggs?`
                
            (You can also type `?eggs` or `help eggs`)

            See that "eggs" takes two arguments, "name" and "good".
            
            You can specify the arguments after the command:

                `eggs Humpty True`
                
            Note that coercion from strings (text="True") to data types
            (boolean) is automatically performed.

            You can also name the arguments:

                `eggs good=True`

            You can also use `?` to get help on the last argument:

                `eggs name?`
            
            To pass multiple commands on the same line use ` : ` (surrounded with spaces)
            
                `eggs Tweedledum : eggs Tweedledee` 

            You should use quotes to pass parameters with spaces:

                `eggs "Humpty Dumpty"`
            """ ),
    HelpTopic( "using_pyi", "Using the application in Python interactive mode", """
            |app_name| can run under a Python interactive session.
            Operation is the same as for command line interactive mode, but
            all commands are visible as Python functions.
            
            To start the application in this mode, pass the `pyi` argument when
            starting it:
            
                `|app_name| pyi`
                
            Example:

                `|app_name| pyi`            
                `cmdlist()`
                `exit()`
                
            Note:
            
                Unlike a simple `import`, this mode:
                    * wraps all commands as global variables, so you can type `cmdlist()` instead
                      of `intermake.commands.cmdlist()`.
                    * permits automatic coercion from strings, so you can type `cmdlist( "yes" )`
                      instead of `cmdlist( True )`. 
                    * allows `Ctrl`+`C` to exit the program.
            """ ),
    HelpTopic( "using_jup", "Using the application in a Jupyter notebook", """
            |app_name| can run inside a Jupyter notebook.
            
            Behaviour is the same as for your own Python programs, but if you
            wish to change the behaviour to be the same as for a Python
            interactive session, call:
            
                `import |app_name|`
                `import intermake`
                `intermake.run_jupyter()`
                
            After this call behaviour is the same as PYI mode (see: `using_pyi`).
            """ ),
    HelpTopic( "using_pys", "Using the application in your own Python programs", """
            |app_name| can also be used as library that you can import into
            your own Python programs.
            
            Unlike starting the application in Python interactive mode, commands
            will not made wrapped up into global variables and coercion from
            strings will not be performed.
            
            Example:

                `python`
                `import |app_name|`
                `import intermake`
                `intermake.commands.print_command_list()`
            """ ),
    HelpTopic( "using_gui", "Using the application in GUI mode", """
            To start the application in GUI mode pass the `gui` parameter on
            the command line:
            
                `|app_name| gui`""" )
)
