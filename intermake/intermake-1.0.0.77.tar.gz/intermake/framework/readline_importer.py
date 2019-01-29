"""
Manages `readline`.

.. note::

    Readline is the thing that allows a UNIX terminal to accept things besides basic text.
    It doesn't work on Windows, or even some UNIX some platforms, which is why its got to be quarantined here.
"""
from typing import Iterator, List, Optional

import warnings
import os
import os.path

import intermake.helpers.printing as pr
from intermake.engine import Controller, constants


__has_initialised: bool = False


def initialise_readline() -> None:
    """
    Starts readline.
    """
    global __has_initialised
    
    if __has_initialised:
        return
    
    __has_initialised = True
    
    try:
        import readline
    except:
        return
    
    history_file = __get_history_file()
    
    if history_file:
        if os.path.isfile( history_file ):
            try:
                readline.read_history_file( history_file )
            except Exception:
                warnings.warn( "Error using history file «{}». This may be a version incompatibility. History not loaded and the file will be overwritten.".format( history_file ) )
    
    completer = __Completer()
    readline.set_completer( completer.complete )
    readline.parse_and_bind( "tab: complete" )
    # readline.parse_and_bind( 'set show-all-if-ambiguous on' )
    # readline.set_completion_display_matches_hook( completer.show )
    # readline.set_completer_delims( " " )


def iter_history() -> Iterator[str]:
    try:
        import readline
    except:
        return ()
    
    for i in range( readline.get_current_history_length() ):
        yield readline.get_history_item( i + 1 )


def write_history() -> None:
    try:
        import readline
    except:
        return
    
    history_file = __get_history_file()
    
    if history_file:
        try:
            readline.write_history_file( history_file )
        except Exception as ex:
            raise IOError( "Failed to write the history file to «{}».".format( history_file ) ) from ex


def __get_history_file() -> str:
    return os.path.join( Controller.ACTIVE.app.local_data.local_folder( constants.FOLDER_SETTINGS ), "command-history.txt" )


class __Completer:
    """
    Used by readline to manage autocompletion of the command line.
    """
    
    
    def __init__( self ):
        """
        Constructor.
        """
        self.matches = []
    
    
    def complete( self, text: str, state: int ) -> Optional[str]:
        """
        See readline.set_completer.
        """
        if state == 0:
            self.matches = [x.name for x in Controller.ACTIVE.app.commands if text in x.name]
        
        if state < 0 or state >= len( self.matches ):
            return None
        else:
            return self.matches[state]
    
    
    # noinspection PyUnusedLocal
    def show( self, substitution: str, matches: List[str], longest_match_length: int ) -> None:
        """
        See readline.set_completion_display_matches_hook.
        """
        active_ui = Controller.ACTIVE
        pr.printx( "<system>" )
        pr.printx( "<value>" + str( len( matches ) ) + "</value> matches for <key>" + substitution + "</key>:" )
        
        if len( self.matches ) > 10:
            pr.printx( "Maybe you meant something a little less ambiguous..." )
        else:
            for x in self.matches:
                pr.printx( "Command <key>" + str( x ) + "</key>" )
        
        pr.printx( "</system>" )
