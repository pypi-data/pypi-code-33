from typing import Generic, TypeVar, Set, Callable


T = TypeVar( "T" )
DAction = Callable[[], None]


class Event( Generic[T] ):
    """
    Multiple dispatch event delegate.
    
    `+=` or `subscribe` can be used to assign delegates, and `-=` or `unsubscribe` removes them.
    (the operator versions require the property be writable)
    
    `()` is used to raise the event.

    Usage:
        Create:
            ```
            event = Event()
            ```
        
        Add:
            ```
            event += handler_1
            ```
        
        Remove:
            ```
            event -= handler_2
            ```
        
        Call:
            ```
            event()
            ```
    """
    
    
    def __init__( self ) -> None:
        self.targets: Set[T] = set()
    
    
    def subscribe( self, other: T ) -> None:
        self.targets.add( other )
    
    
    def unsubscribe( self, other: T ) -> None:
        self.targets.remove( other )
    
    
    def __iadd__( self, other: T ) -> "Event":
        """
        `event += callback`
        """
        self.subscribe( other )
        return self
    
    
    def __isub__( self, other: T ) -> "Event":
        """
        `event -= callback`
        """
        self.unsubscribe( other )
        return self
    
    
    def __call__( self, *args, **kwargs ) -> None:
        """
        ```event()```
        
        :param args:        Arguments to pass. 
        :param kwargs:      Arguments to pass.
        :return:            Nothing is returned. 
        """
        for target in self.targets:
            # noinspection PyCallingNonCallable
            target( *args, **kwargs )
