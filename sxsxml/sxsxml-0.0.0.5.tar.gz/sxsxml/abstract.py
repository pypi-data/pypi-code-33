import sys
from typing import cast
from html.parser import HTMLParser

from mhelper import ansi_format_helper, Logger
from sxsxml.support import XsElement, XsStack


LOG = Logger( "SXS", False )


class XsWriter:
    """
    ABSTRACT
    
    Base class for `XsParser` output targets.
    
    The derived class should implement the abstract functions.
    
    .. note::
    
        `XsNestedOutput` may provide a more usable class in certain circumstances.
    """
    
    
    def __init__( self ) -> None:
        super().__init__()
        self.__stack = []
        self.__parser = _InternalParser( self )
    
    
    def on_text( self, x: str ) -> None:
        """
        Handles text written to stream.
        """
        raise NotImplementedError( "abstract" )
    
    
    def on_enter( self, e: XsElement ) -> None:
        """
        Handles entering an element.
        """
        raise NotImplementedError( "abstract" )
    
    
    def on_exit( self, e: XsElement ) -> None:
        """
        Handles exiting an element.
        """
        raise NotImplementedError( "abstract" )
    
    
    def on_error( self, ex: Exception ) -> bool:
        """
        Called to process any parser error.
         
        :param ex:  Error 
        :return:    Returning a false-like value or `None` ignores the error.
        """
        cast( None, ex )
        return True
    
    
    def on_flush( self ) -> None:
        """
        Called to perform a flush.
        """
        pass
    
    
    def flush( self ):
        self.on_flush()
    
    
    def reset( self ):
        """
        Reset to initial state.
        """
        self.on_reset()
        assert not self.__stack, "Derived class did not call base on_reset in '{}'".format( self )
    
    
    def on_reset( self ) -> None:
        """
        Reset to initial state.
        Derived class should call back to base class.
        """
        self.__parser.reset()
        self.__stack = []
    
    
    def write( self, data ):
        try:
            self.__parser.feed( data )
        except Exception as ex:
            sys.__stderr__.write( "FULL TEXT BEGINS\n" )
            sys.__stderr__.write( data )
            sys.__stderr__.write( "\nFULL TEXT ENDS\n" )
            sys.__stderr__.write( ansi_format_helper.format_traceback( ex ) )
            sys.__stderr__.write( "\n" )
            sys.__stderr__.write( "FULL TEXT PRECEDES ERROR MESSAGE\n" )
            self.__parser.reset()
            self.on_text( "(PARSER ERROR: SEE STDERR FOR DETAILS)\n" )
    
    
    def print( self, text: str, *, end: str = "\n" ) -> None:
        self.__parser.feed( text )
        
        if end:
            self.__parser.feed( end )


class _InternalParser( HTMLParser ):
    def __init__( self, owner: XsWriter ):
        super().__init__()
        self.__stack = []
        self.__owner = owner
    
    
    def handle_starttag( self, tag, attrs ):
        e = XsElement( "", tag, dict( attrs ) )
        self.__stack.append( e )
        self.__owner.on_enter( e )
    
    
    def handle_endtag( self, tag ):
        e = self.__stack.pop( -1 )
        
        if e.name != tag:
            self.error( "Entering tag is '{}' but closing tag is '{}'".format( e.name, tag ) )
        
        self.__owner.on_exit( e )
    
    
    def handle_data( self, data ):
        self.__owner.on_text( data )
    
    
    def error( self, message ):
        try:
            raise ValueError( "Error from HTML parser: " + message )
        except ValueError as ex:
            if self.__owner.on_error( ex ):
                raise


class XsStackedWriter( XsWriter ):
    """
    ABSTRACT
    
    Finds methods `enter_` and `exit_` in the derived class and uses these to format the output.
    
    The enter methods can call `push` and the exit methods `pop` to retrieve element text. 
    """
    
    
    def __init__( self, out = sys.stdout.write ):
        super().__init__()
        
        self.__enter_map = { }
        self.__exit_map = { }
        self.__stack = XsStack( out )
        self.element: XsElement = None
    
    
    def map( self, tags, enter, exit ):
        for tag in tags:
            if enter is not None:
                self.__enter_map[tag] = enter
            
            if exit is not None:
                self.__exit_map[tag] = exit
    
    
    def on_reset( self ):
        super().on_reset()
        self.__stack.reset()
    
    
    def get( self, key, default = "" ) -> str:
        return self.element.get( key, default )
    
    
    def on_enter( self, e: XsElement ):
        self.element = e
        fn = self.__enter_map.get( e.name, self._enter_default )
        LOG( "Entering {}", e, fn )
        fn()
        self.element = None
    
    
    def on_exit( self, e: XsElement ):
        self.element = e
        fn = self.__exit_map.get( e.name, self._exit_default )
        LOG( "Exiting {} {}", e, fn )
        fn()
        self.element = None
    
    
    def push( self ):
        LOG( "Pushing {}", self.element )
        self.__stack.push( self.element )
    
    
    def pop( self ) -> str:
        LOG( "Popping {}", self.element )
        return self.__stack.pop( self.element )
    
    
    def _enter_default( self ):
        self.push()
    
    
    def _exit_default( self ):
        self.pop()
    
    
    def on_text( self, x: str ) -> None:
        self.__stack.write( x )
    
    
    def on_error( self, ex: Exception ):
        self.__stack.reset()
        return True
