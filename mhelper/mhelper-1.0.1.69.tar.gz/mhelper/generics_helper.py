from typing import Any, Callable, Optional, Type, TypeVar, Union, cast, Sequence, Generic


# Decorator function, returns a function that takes and returns a function
DECORATOR_FUNCTION = Callable[..., Callable[[Callable], Callable]]
# Decorator - takes a function, returns a function
DECORATOR = Callable[[Callable], Callable]
DECORATED = Optional[object]

T = TypeVar( "T" )


class MGenericMeta( type ):
    """
    Base class for generics.
    For example see `MGeneric` documentation.
    
    :ivar __parameters__:   Field containing the generic parameters.
                            Empty for the non-generic base.
                            
    :remarks: Nb. Name of `__parameters__` violates PEP8 but is coherent with PEP464 implementation and signifies a meta-field. 
    """
    
    
    def __new__( mcs, name, bases, namespace, parameters = None ):
        cls = super().__new__( mcs, name, bases, namespace )
        return cls
    
    
    def __init__( cls, name, bases, namespace, parameters = None ):
        super().__init__( name, bases, namespace )
        
        if parameters is None:
            if bases:
                for base in bases:
                    if hasattr( base, "__parameters__" ):
                        if parameters is not None:
                            raise TypeError( "Cannot inherit parameters because I don't know which subclass to use." )
                        
                        parameters = base.__parameters__
            
            if parameters is None:
                parameters = tuple()
        
        cls.__parameters__ = parameters
        cls.__CACHE = { }
    
    
    def __getitem__( cls: T, parameters ) -> T:
        """
        Obtains a class with the specified generic parameters.
        Results are cached, so asking for the same parameters again yields the same class instance.
        
        If the called class itself has generic parameters, the parameters are concatenated, for instance all of:
            A = MGeneric[int, bool]
            B = MGeneric[int][bool]
            C = MGeneric[int][bool]
        Have the same generic parameters (int, bool).
        However, the instances are different, hence:
            A.__parameters__ == B.__parameters__ == C.__parameters__
            A is not B
            B is C 
        
        :param parameters: Generic parameters. 
        """
        if parameters is None:
            parameters = ()
        elif not isinstance( parameters, tuple ):
            parameters = (parameters,)
        
        if parameters in cls.__CACHE:
            return cls.__CACHE[parameters]
        
        if cls.__parameters__:
            all_parameters = cls.__parameters__ + parameters
        else:
            all_parameters = parameters
        
        result = cls.__class__( cls.__name__,
                                (cls,) + cls.__bases__,
                                dict( cls.__dict__ ),
                                parameters = all_parameters )
        
        cls.__CACHE[parameters] = result
        
        return result
    
    
    def __str__( self ):
        """
        Returns a string similar to normal Python classes, but includes the generic parameters.
        Note that this is not the same as `__name__`, which always holds only the base class name, without the generics.
        """
        if self.__parameters__:
            return "<class {}{}>".format( self.__name__, ("[" + (", ".join( str( x ) for x in self.__parameters__ ) + "]")) )
        else:
            return "<class {}>".format( self.__name__ )


class MGeneric( metaclass = MGenericMeta ):
    """
    Instantiation of class with MGenericMeta meta-class.
    
    EXAMPLE:
        
        ```
        class MyList( MGeneric ):
            def item_type(self):
                return self.__parameters__[0]
            
            def append( item ):
                assert isinstance(item, self.item_type())
                ...
        ```
    """
    pass


# noinspection PyUnusedLocal
def placeholder( type_: Type[T] ) -> T:
    """
    Always returns `None`.
    For fixing lint errors where the specified type is expected
    """
    # noinspection PyTypeChecker
    return None





class GenericStringMeta( MGenericMeta ):
    def __subclasscheck__( self, cls ):
        if cls is Any:
            return True
        if self.__parameters__ is None:
            return isinstance( cls, GenericStringMeta )
        elif isinstance( cls, GenericStringMeta ):
            return True
        elif isinstance( cls, GenericStringMeta ):
            if issubclass( cls, str ):
                return True
            return False
        else:
            return issubclass( cls, str )
    
    
    def __instancecheck__( self, obj ):
        print( "__instancecheck__ {}".format( obj ) )
        return self.__subclasscheck__( type( obj ) )


class GenericString( str, metaclass = GenericStringMeta ):
    """
    Something that is a string.
    
    This property acts as a hint to the UI, indicating the string's values are constrained.
    
    A "label" of the node or edge can be specified as a generic argument.
    Use "@" to reference the name of another function argument.
    
    
    GenericString["label"]("value")
        - OR -
    GenericString("value")
    """
    
    
    def __new__( cls: Type[T], *args, **kwargs ) -> T:
        # noinspection PyArgumentList,PyTypeChecker
        return cast( cls, str.__new__( cls, *args, **kwargs ) )
    
    
    # noinspection PyUnresolvedReferences
    @classmethod
    def type_label( cls ):
        if cls.__parameters__:
            return cls.__parameters__[0]
        else:
            return None


class NonGenericString( str ):
    """
    NonGenericString("value")
    
    This property acts as a hint to the UI, indicating the string's values are constrained.
    """
    
    
    def __new__( cls: Type[T], *args, **kwargs ) -> T:
        # noinspection PyArgumentList,PyTypeChecker
        return cast( cls, str.__new__( cls, *args, **kwargs ) )


class TypedList( MGeneric ):
    def get_list_type( self ):
        return self.__parameters__[0]
    
    
    def __init__( self, *args, **kwargs ):
        self.__list = list( *args, **kwargs )
    
    
    def __getitem__( self, item ):
        return self.__list[item]
    
    
    def __setitem__( self, key, value ):
        self.__check_instance( value )
        self.__list[key] = value
    
    
    def append( self, value ):
        self.__check_instance( value )
        self.__list.append( value )
    
    
    def __check_instance( self, value ):
        if not isinstance( value, self.__parameters__[0] ):
            raise TypeError( "Value «{}» of incorrect type «{}» added to list of «{}».".format( value, type( value ), self.get_list_type() ) )


class ByRef( Generic[T] ):
    """
    Pass value by reference.
    """
    
    
    def __init__( self, value: T ):
        self.value: T = value


def extend( type_ ):
    """
    Adds an extension method.
    :param type_:   Type to extend 
    :return: 
    """
    
    
    def ___fn( fn ):
        setattr( type_, fn.__name__, fn )
        return fn
    
    
    return ___fn
