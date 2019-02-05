from enum import Enum

from mhelper.mannotation.classes import MAnnotation


class EFileMode( Enum ):
    """
    Used by `FileNameAnnotation`.
    How file is written to.
    
    :cvar UNKNOWN:  Default
    :cvar READ:     Or `"r"`, open file for reading
    :cvar WRITE:    Or `"w"`, open file for writing
    :cvar OUTPUT:   Or `"o"`, open file for writing, accepts output names supported by :func:`io_helper.open_write`.
    """
    UNKNOWN = 0
    READ = 1
    WRITE = 2
    OUTPUT = 3


class FileNameAnnotation( MAnnotation ):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        mode = EFileMode.UNKNOWN
        ext = None
        
        for p in self.parameters[2:]:
            if isinstance( p, EFileMode ):
                mode = p
            elif p == "r":
                mode = EFileMode.READ
            elif p == "w":
                mode = EFileMode.WRITE
            elif isinstance( p, str ):
                ext = p
            else:
                from mhelper.exception_helper import SwitchError
                raise SwitchError( "parameter", p, instance = True )
        
        self.mode = mode
        self.extension = ext


class EnumerativeAnnotation( MAnnotation ):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        
        opts = { }
        
        for p in self.parameters:
            if isinstance( p, dict ):
                opts.update( p )
        
        self.options = opts
