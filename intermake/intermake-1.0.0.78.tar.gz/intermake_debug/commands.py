import sys
import warnings
from typing import Optional, List
from mhelper import string_helper
import intermake


def __cmd():
    return intermake.app.command( folder = "DEBUG" )


@__cmd()
def debug_error():
    """
    Tests the error handling capabilities of the host
    """
    raise ValueError( "This is an error." )


@__cmd()
def debug_echo_numeric( number: int ):
    """
    Echos a number
    """
    intermake.pr.pr_information( str( number ) )


@__cmd()
def debug_echo( text: str ):
    """
    Echos the text. Echos the text.
    :param text: Text to echo.
                 "on" or "off": turns command echoing on or off (temporarily).
    """
    if text.lower() == "on":
        intermake.console_configuration.ephemeral.force_echo = True
        intermake.pr.pr_information( "Echo is on" )
        return
    elif text.lower() == "off":
        intermake.console_configuration.ephemeral.force_echo = False
        intermake.pr.pr_information( "Echo is off" )
        return
    
    intermake.pr.pr_information( text )


@__cmd()
def debug_modules( filter: Optional[str] = None ):
    """
    Prints out the loaded modules.
    :param filter:  Filter by name.
    """
    for name, module in sys.modules.items():
        if filter is not None and not filter.lower() in module.__name__.lower():
            continue
        
        intermake.pr.printx( name )
        intermake.pr.printx( module.__name__ )
        intermake.pr.printx( "<file>{}</file>".format( module.__file__ if hasattr( module, "__file__" ) else "" ) )


@__cmd()
def debug_coercers():
    """
    Prints out the coercers in the stringcoercion library.
    """
    for coercer in intermake.Controller.ACTIVE.coercers:
        intermake.pr.pr_information( str( coercer ) )


@__cmd()
def debug_eval( command_: str ) -> None:
    """
    Evaluates a Python statement and prints the result.
    
    The same statements are available as 
    """
    from intermake.framework.console_controller import _PyiCommandWrapper
    scope = _PyiCommandWrapper.get_dict( intermake.Controller.ACTIVE.app )
    r = eval( command_, scope )
    
    if r is not None:
        intermake.pr.pr_information( "{} = {}".format( command_, str( r ) ) )


@__cmd()
def debug_which( text: str ) -> None:
    """
    Finds which command will be matched if the user types "text".
    :param text: Text to find
    """
    
    fn = intermake.console_parser.find_command( text )
    
    if fn:
        intermake.pr.printx( "<key>Result</key> = <value>{}</value>", fn.name )
    else:
        intermake.pr.printx( "<key>Result</key> = <value>(no result)</value>" )


@__cmd()
def debug_css( css: Optional[str] = None ):
    """
    Gets the Intermake CSS.
    If pyperclip is installed, the result is copied to the clipboard, otherwise it is printed to stdout.
    
    :param css: Theme
    """
    from intermake_qt.utilities import css_processing
    css = css_processing.load_css( css )
    
    try:
        import pyperclip
        pyperclip.copy( css )
        intermake.pr.pr_information( "Copied to clipboard." )
    except ImportError:
        intermake.pr.pr_information( css )
        warnings.warn( "Printed to stdout (pyperclip is not installed so not copied to clipboard)." )


class AdvSet( intermake.SetterCommand ):
    """
    Sets the console _configuration_.
    The configuration is active for this session only.
    """
    
    
    def on_get_targets( self ):
        active_ui = intermake.Controller.ACTIVE
        
        if isinstance( active_ui, intermake.ConsoleController ):
            yield "console", active_ui.console_configuration
        else:
            raise ValueError( "This operation only works for Console UIs." )


@__cmd()
def debug_system( command: List[str] ) -> None:
    """
    Invokes a system command in the current terminal.
    
    :param command: Command to execute.
    """
    intermake.run_subprocess( command )


@__cmd()
def debug_show_settings() -> None:
    """
    Shows the current console configuration.
    """
    e = intermake.console_configuration.ephemeral
    s = intermake.console_configuration.saved
    c = intermake.console_configuration.current
    
    rows = [["setting", "type", "ephemeral", "saved", "current"]]
    ml = lambda x: string_helper.max_width( repr( x ), 20 )
    
    for k in e.__dict__:
        ev = getattr( e, k )
        sv = getattr( s, k )
        cv = getattr( c, k )
        
        rows.append( [k, type( ev ).__name__, ml( ev ), ml( sv ), ml( cv )] )
    
    intermake.pr.pr_table( rows )


@__cmd()
def debug_make_boring( boring: bool = True, persist: bool = False ) -> None:
    """
    Disables colour, unicode and stream output.
    Added this after receiving complaints about the exciting default colour scheme.
    
    :param boring:  Boring status.
    :param persist: Make changes to defaults
    """
    cfg = intermake.console_configuration.saved if persist else intermake.console_configuration.ephemeral
    
    cfg.remove_utf = boring
    cfg.remove_ansi = boring
    cfg.hide_streams = boring
    
    intermake.pr.printx( "<verbose>CONSOLE SETTINGS ({})</verbose>".format( "SAVED" if persist else "EPHEMERAL" ) )
    intermake.pr.printx( "<verbose>NON-ASCII [{0}], ANSI-COLOURS [{0}], SIDEBAR [{0}]</verbose>".format( "OFF" if boring else "ON" ) )


debug_set = AdvSet( names = ["debug_set"], folder = "DEBUG" )
intermake.app.command( debug_set )
