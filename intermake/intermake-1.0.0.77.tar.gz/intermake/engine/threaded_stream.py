"""
Classes for routing std-out messages.



sys.stdout --> Streaming.INSTANCE --> *thread_local_router*

    *thread_local_router* for `ConsoleController`:
        SxsToStderr -> *messages formatted using `sxsxml`* --> sys.__stderr__
        
    *thread_local_router* for `GuiController`:
        _SxsGuiWriter -> *messages formatted using `sxsxml`* --> *Qt window*
        
    The *thread_local_router* in the main thread is the same as `ConsoleController`, which
    is in place in case any messages get printed after the redirection but before the UI is started
    (typically warnings).
    


"""

import sxsxml
import threading
import sys
import re
from mhelper import ansi_helper


class Streaming:
    """
    SINGLETON
    
    When `print` or `intermake.pr.printx` are the data is routed through this class.
    
    This ensures that messages reach the correct UI.
    
    The routing is per-thread and is set by the `Controller` when executing an `Command`, by
    calling `Streaming.INSTANCE.set_target()`.
    """
    INSTANCE: "Streaming" = None
    
    
    def __init__( self ):
        self.local = threading.local()
    
    
    def get_target( self ):
        return self.local.target
    
    
    def set_target( self, value ):
        self.local.target = value
    
    
    def write( self, *args, **kwargs ):
        try:
            self.local.target.write( *args, **kwargs )
        except AttributeError as ex:
            raise ValueError( "Cannot write to the stream because the current thread '{}' has not been setup for use with printing.".format( threading.current_thread().name ) ) from ex
    
    
    def flush( self ):
        self.local.target.flush()


class SxsToStderrWriter:
    """
    This class routes messages through the SxsXml parser and sends the output to std-err.
    
    It is used primarily by `ConsoleController` but also acts as the default router. 
    """
    RX_REMOVE_UTF = re.compile( r"[^\x00-\x7F]" )
    
    
    class Settings:
        """
        :ivar remove_ansi:             When set, ANSI colour codes are stripped from the output.
                                       This only applies to output relayed through Intermake, application specific
                                       output may not respect this setting.
        :ivar remove_utf:              When set, non-ASCII sequences are substituted in the output for this character.
                                       This only applies to output relayed through Intermake, application specific
                                       output may not respect this setting.
        :ivar format_output:           Convert the XML output into ANSI.
        """
        
        
        def __init__( self, *, format_output: bool, remove_ansi: bool, remove_utf: str ):
            self.format_output: bool = format_output
            self.remove_ansi: bool = remove_ansi
            self.remove_utf: str = remove_utf
    
    
    def __init__( self, settings: Settings ):
        self.writer = sxsxml.SxsAnsiWriter( self.__handle_message_formatted )
        self.history = []
        self.settings = settings
    
    
    def reset( self ):
        self.writer.reset()
    
    
    def write( self, message ):
        """
        Formats CLI output.
        
        .. note::
        
            Because it operates in the main thread, progress in the CLI cannot be cancelled externally.
            (However, the user can just press CTRL+C to force an error at any point, we already pick this up and handle it accordingly elsewhere.)
        """
        self.history.append( message )
        
        if self.settings.format_output:
            self.writer.write( message )  # --> self.__handle_message_formatted
        else:
            sys.__stderr__.write( message )
    
    
    def __handle_message_formatted( self, ansi ):
        if self.settings.remove_ansi:
            ansi = ansi_helper.without_ansi( ansi )
        
        if self.settings.remove_utf:
            ansi = self.RX_REMOVE_UTF.sub( self.settings.remove_utf, ansi )
        
        sys.__stderr__.write( ansi )
    
    
    def flush( self ):
        sys.__stderr__.flush()


Streaming.INSTANCE = Streaming()
Streaming.INSTANCE.set_target ( SxsToStderrWriter( SxsToStderrWriter.Settings( format_output = False, remove_ansi = True, remove_utf = "?" ) ) )
