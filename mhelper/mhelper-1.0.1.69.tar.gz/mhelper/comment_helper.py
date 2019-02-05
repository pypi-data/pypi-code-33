# The following are decorators, they don't do anything, they're just used as comments
from inspect import isclass
from typing import TypeVar, Type, Any, cast


_T = TypeVar( "_T" )


def identity( x ):
    """
    Returns its parameter
    """
    return x


def ignore( *_, **__ ):
    """
    Ignores its parameters
    """
    pass


def protected( f ):
    return f


def sealed( f ):
    return f


def override( f ):  # means "I'm not documenting this because the documentation is in the base class"
    return f


def overrides( interface ):
    ignore( interface )
    return override


def virtual( f ):
    return f


def abstract( f ):
    if isclass( f ):
        return f
    
    
    def fn( self, *_, **__ ):
        raise NotImplementedError( "An attempt has been made to call an abstract method «{1}.{0}». The object's string representation is «{2}».".format( f.__name__, type( self ).__name__, repr( self ) ) )
    
    
    return fn


