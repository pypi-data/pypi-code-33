import logging
import sys
import warnings
from typing import Union

from mhelper import ansi, string_helper


class Handler( logging.Handler ):
    target = sys.__stderr__.write
    __FG_COLOURS = [ansi.FR,
                    ansi.FG,
                    ansi.FB,
                    ansi.FC,
                    ansi.FY,
                    ansi.FM,
                    ansi.FW,
                    ansi.FK,
                    ansi.FBR,
                    ansi.FBG,
                    ansi.FBB,
                    ansi.FBC,
                    ansi.FBY,
                    ansi.FBM,
                    ansi.FBW,
                    ansi.FBK]
    __BG_COLOURS = [ansi.BR,
                    ansi.BG,
                    ansi.BB,
                    ansi.BC,
                    ansi.BY,
                    ansi.BM,
                    ansi.BW,
                    ansi.BK,
                    ansi.BBR,
                    ansi.BBG,
                    ansi.BBB,
                    ansi.BBC,
                    ansi.BBY,
                    ansi.BBM,
                    ansi.BBW,
                    ansi.BBK]
    
    
    def __init__( self, name ):
        super().__init__()
        
        sigil_1 = self.__FG_COLOURS[hash( name ) % len( self.__FG_COLOURS )]
        sigil_2 = self.__BG_COLOURS[hash( name * 2 ) % len( self.__BG_COLOURS )]
        self.sigil = sigil_1 + sigil_2 + name[0] + ansi.RESET + " " + ansi.FORE_CYAN + name
    
    
    def emit( self, x: logging.LogRecord ):
        text = x.getMessage()
        text = ansi.FORE_GREEN + string_helper.highlight_quotes( text, "«", "»", ansi.FORE_YELLOW, ansi.FORE_GREEN ) + ansi.FORE_RESET
        text = "{}: {}\n".format( self.sigil, text )
        self.target( text )


class Logger:
    """
    Logging simplified.
    
    This just wraps logging.Logger and provides an ANSI-terminal handler (`Handler`) by
    default. All messages are logged at the same level. The target terminal can be changed via
    `Logger.Handler.target`. The provided handler can be changed or removed by setting
    `Logger.handler`.
    
    Usage::
    
        log = Logger( "my logger", True )
        log( "hello {}", x )
    """
    __INDENT_SIZE = 4
    Handler = Handler
    
    
    def __init__( self,
                  name: str,
                  enabled: Union[bool, str] = False ):
        """
        CONSTRUCTOR
        :param name:    Default value to :property:`name`. 
        :param enabled:    Default value to :property:`enabled`.
        """
        self.__level = logging.INFO
        self.__true_logger = logging.getLogger( name )
        self.__indent = 0
        self.__handler = Handler( self.name )
        self.__true_logger.addHandler( self.__handler )
        
        self.enabled = enabled
    
    
    @property
    def handler( self ) -> logging.Handler:
        return self.__handler
    
    
    @handler.setter
    def handler( self, value: logging.Handler ) -> None:
        if self.__handler is not None:
            self.__true_logger.removeHandler( self.__handler )
        
        if value is not None:
            self.__true_logger.addHandler( value )
    
    
    @property
    def name( self ) -> str:
        return self.__true_logger.name
    
    
    def __bool__( self ) -> bool:
        return self.enabled
    
    
    def pause( self, *_, **__ ) -> None:
        warnings.warn( "Deprecated. No longer functional.", DeprecationWarning )
    
    
    @property
    def enabled( self ) -> bool:
        """
        Gets or sets whether the logger is enabled.
        """
        return self.__true_logger.isEnabledFor( self.__level )
    
    
    @enabled.setter
    def enabled( self, value: bool ) -> None:
        if value:
            self.__true_logger.setLevel( logging.DEBUG )
        else:
            self.__true_logger.setLevel( logging.NOTSET )
    
    
    def __call__( self, *args, **kwargs ) -> "Logger":
        if self.enabled:
            self.print( self.format( *args, *kwargs ) )
        
        return self
    
    
    def format( self, *args, **kwargs ) -> str:
        if len( args ) == 1:
            r = args[0]
        elif len( args ) > 1:
            vals = list( args[1:] )
            for i in range( len( vals ) ):
                v = vals[i]
                
                if type( v ) in (set, list, tuple, frozenset):
                    vals[i] = string_helper.array_to_string( v, **kwargs )
                
                vals[i] = "«" + str( vals[i] ) + "»"
            
            r = args[0].format( *vals )
        else:
            r = ""
        
        return " " * (self.__indent * self.__INDENT_SIZE) + r
    
    
    def print( self, message: str ) -> None:
        self.__true_logger.log( self.__level, message )
    
    
    @property
    def indent( self ) -> int:
        return self.__indent
    
    
    @indent.setter
    def indent( self, level: int ) -> None:
        assert isinstance( level, int )
        self.__indent = level
    
    
    def __enter__( self ) -> None:
        self.indent += 1
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ) -> None:
        self.indent -= 1
