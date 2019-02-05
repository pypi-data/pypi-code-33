"""
Special string types
"""
from enum import Enum
from typing import TypeVar, Optional

# noinspection PyPackageRequirements
from flags import Flags




T = TypeVar( "T" )
TTristate = Optional[bool]

class Sentinel:
    """
    Type used for sentinel objects (things that don't do anything but whose presence indicates something).
    The Sentinel also has a `str` method equal to its name, so is appropriate for user feedback. 
    """
    
    
    def __init__( self, name: str ):
        """
        :param name:    Name, for debugging or display. 
        """
        self.__name = name
    
    
    def __str__( self ) -> str:
        return self.__name
    
    
    def __repr__( self ):
        return "Sentinel({})".format( repr( self.__name ) )


NOT_PROVIDED = Sentinel( "(Not provided)" )
"""
NOT_PROVIDED is used to distinguish between a value of `None` and a value that that isn't even provided.
"""


# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒ ENUMS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒


class MEnum( Enum ):
    """
    An enum class that presents a less useless string function
    """
    
    
    def __str__( self ):
        return self.name


class MFlags( Flags ):
    """
    A flags class that presents  less useless string function
    """
    __no_flags_name__ = "NONE"
    __all_flags_name__ = "ALL"
    
    
    def __str__( self ):
        return self.to_simple_str()



_default_filename_path = None





class ArgsKwargs:
    EMPTY: "ArgsKwargs" = None
    
    
    def __init__( self, *args, **kwargs ) -> None:
        self.args = args
        self.kwargs = kwargs
    
    
    def __bool__( self ):
        return bool( self.args ) or bool( self.kwargs )
    
    
    def __getitem__( self, item ):
        r = self.get( item[0], item[1] )
        
        if isinstance( r, NOT_PROVIDED ):
            raise KeyError( item )
        
        return r
    
    
    def get( self, index, name, default = NOT_PROVIDED ):
        if 0 <= index < len( self.args ):
            return self.args[index]
        
        if name:
            return self.kwargs.get( name, default )
        
        return default
    
    
    def __repr__( self ):
        r = []
        
        for x in self.args:
            r.append( "{}".format( x ) )
        
        for k, x in self.kwargs.items():
            r.append( "{} = {}".format( k, x ) )
        
        return ", ".join( r )


ArgsKwargs.EMPTY = ArgsKwargs()