"""
Contains the :class:`SimpleProxy` and its dependencies.
"""
from typing import Callable, Optional, T, cast, Type


class PropertySetInfo:
    """
    Used by `SimpleProxy.__init__.on_set_attr`
    """
    
    
    def __init__( self, proxy, target, name, value ):
        """
        :param target:  Target object 
        :param name:    Attribute name 
        :param value:   Attribute value 
        """
        self.proxy = proxy
        self.source = target
        self.name = name
        self.value = value


class SimpleProxy:
    """
    Creates a proxy object that can be used exactly like another object.
    """
    
    
    def __init__( self, source: Callable[[], object] = None, target: object = None, on_set_attr: Optional[Callable[[PropertySetInfo], None]] = None ):
        """
        Constructor.
        Either of `source` or `target` must be provided (but not both).
        
        :param source:        How to obtain the target to bind to.
        :param target:        The target to bind to. 
        :param on_set_attr:   A callback to be called when `__setattr__` is called on the target.
        """
        if source is None:
            if target is None:
                raise ValueError( "Must specify either the «source_get» or the «source» parameter." )
            
            source = (lambda x: lambda: x)( target )
        
        object.__setattr__( self, "__source", source )
        object.__setattr__( self, "__watch", on_set_attr )
    
    
    def __getattribute__( self, name: str ) -> object:
        if name == "__class__":
            # Don't fake the class name, this may seem like a good idea, but it's not:
            # e.g. a `str` is immutable -  `SimpleProxy(lambda: my_str)` isn't.
            return SimpleProxy
        
        source = object.__getattribute__( self, "__source" )
        return getattr( source(), name )
    
    
    def get_source( self ):
        """
        Retrieves the source of the proxy.
        NOTE: This must be called using `SimpleProxy.get_source(x)`, rather than `x.get_source()`, since the latter will wrap the call to the proxied object.
        """
        return object.__getattribute__( self, "__source" )()
    
    
    def __delattr__( self, name ):
        delattr( object.__getattribute__( self, "__source" )(), name )
    
    
    def __setattr__( self, name, value ):
        watch = object.__getattribute__( self, "__watch" )
        target = object.__getattribute__( self, "__source" )()
        setattr( target, name, value )
        
        if watch is not None:
            args = PropertySetInfo( self, target, name, value )
            watch( args )
    
    
    def __str__( self ) -> str:
        return str( object.__getattribute__( self, "__source" )() )
    
    
    def __repr__( self ) -> str:
        return repr( object.__getattribute__( self, "__source" )() )
    
    
    @classmethod
    def new( cls, t : Type[T], *args, **kwargs ) -> T:
        """
        Version of `SimpleProxy()` with an automatic cast annotation.
        :param t:           Type to cast to 
        :param args:        Passed to `SimpleProxy(...)`
        :param kwargs:      Passed to `SimpleProxy(...)`
        :return:            New instance 
        """
        return cast(T, cls( *args, **kwargs ))
