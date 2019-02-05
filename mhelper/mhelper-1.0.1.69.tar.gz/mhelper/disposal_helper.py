from typing import Optional, Callable, Generic, TypeVar


T = TypeVar( "T" )


class ManagedWith( Generic[T] ):
    """
    Wraps a (presumably pooled) object.
    
    Usage:

        ```
        with ManagedWith(...):
            ...
        ```
        
    Example (database provider):

        ```    
        def open_connection():
            return ManagedWith(pool.pop(), pool.push)
        ```
        
        ```
        with open_connection() as db:
            db.execute("RETURN 1")
        ```
    """
    
    
    def YOURE_USING_THE_WRONG_THING( self ):
        """
        Message to an IDE user telling them they're using the wrong thing!
        (They should be using `with x as y` and not `with x`.)
        """
        pass
    
    
    def __init__( self,
                  target: Optional[T] = None,
                  on_exit: Callable[[Optional[T]], None] = None,
                  on_enter: Callable[[Optional[T]], None] = None,
                  on_get_target: Callable[[], T] = None ):
        """
        :param target:          The object to be returned as the `as` clause of the `with` statement.
        :param on_exit:         Called when the `with` block is closed. The single parameter is the target. The result is ignored.
        :param on_enter:        Called when the `with` block is opened. The single parameter is the target. The result is ignored.
        :param on_get_target:   Called when the `with` block is opened. There are no parameters. The result is used as the target.  
        """
        self.__target = target
        self.__on_exit = on_exit
        self.__on_enter = on_enter
        self.__on_get_target = on_get_target
        
        if self.__on_get_target is not None and self.__target is not None:
            raise ValueError( "Cannot specify both 'on_get_target' and 'target' parameters." )
    
    
    def __enter__( self ) -> T:
        if self.__on_get_target is not None:
            self.__target = self.__on_get_target()
        
        if self.__on_enter is not None:
            self.__on_enter( self.__target )
        
        return self.__target
    
    
    def __exit__( self, exc_type, exc_val, exc_tb ):
        if self.__on_exit is not None:
            self.__on_exit( self.__target )
        
        if self.__on_get_target is not None:
            self.__target = None
