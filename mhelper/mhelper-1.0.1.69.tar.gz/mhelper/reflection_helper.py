import inspect
from typing import List, Union, Callable, TypeVar, Type, Iterator, Tuple, Optional, Set
from mhelper import exception_helper, string_helper


ModuleType = type( inspect )

_T = TypeVar( "_T" )


def enfunction( target: Union[_T, Callable[[], _T]] ) -> Callable[[], _T]:
    """
    If `x` is not a function, returns a lambda returning `x`, otherwise, assumes `x` is already a
    lambda and returns `x`.
    This is the opposite of `defunction`.
    """
    if inspect.isroutine( target ):
        return target
    else:
        return (lambda x: lambda: x)( target )


def defunction( target: Union[_T, Callable[[], _T]], cast: Type[_T] = object, errors = False ) -> _T:
    """
    If `x` is a function or a method, calls `x` and returns the result.
    Otherwise, returns `x`.
    """
    if inspect.isroutine( target ):
        try:
            r = target()
        except Exception as ex:
            if errors:
                r = ex
            else:
                raise ValueError( "Failed to defunction «{}». See inner exception.".format( target ) ) from ex
        
        if cast is not object:
            exception_helper.safe_cast( "defunction.result", r, cast )
        
        return r
    else:
        return target


def iter_hierarchy( type_: Type ) -> Iterator[Type]:
    """
    Iterates UP the hierarchy, starting with the MOST DERIVED class.
    The type itself is yielded.
    """
    queue: List[Type] = []
    queue.append( type_ )
    
    while queue:
        type_ = queue.pop( 0 )
        yield type_
        queue.extend( type_.__bases__ )


def get_export_path( module: ModuleType, target: object ) -> Optional[str]:
    """
    Finds the shortest path by which a `target` object is exported from a
    package or `module`.
    """
    for export in iter_exports( module ):
        if export[-1][1] is target:
            return ".".join( x[0] for x in export )
    
    return None


def iter_exports( module: ModuleType ) -> Iterator[List[Tuple[str, object]]]:
    """
    Recursively iterates the exports of a module `root`.
    
    This is a breadth-first iterator.
    
    :param module:      Module to start searching from 
    :return:            An iterator over lists, where each list contains tuples describing the path to
                        an export. Each tuple contains the name of the exported object, and the
                        exported object itself. 
    """
    touched: Set[ModuleType] = { module }
    stack: List[List[Tuple[str, object]]] = [[(module.__name__, module)]]
    
    while stack:
        current: List[Tuple[str, object]] = stack.pop( 0 )
        source: object = current[-1][1]
        
        for k, v in source.__dict__.items():
            if not isinstance( k, str ) or k.startswith( "_" ):
                continue
            
            next_ = current + [(k, v)]
            yield next_
            
            if type( v ) is not ModuleType:
                continue
            
            if v in touched:
                continue
            
            touched.add( v )
            
            stack.append( next_ )


def describe_num_fields( x: object ) -> str:
    c = sum( not k.startswith( "_" ) for k in x.__dict__ )
    return "{}({} fields)".format( type( x ).__name__, c )


def describe_fields( x: object ) -> str:
    """
    Returns a string describing a pseudo-construction of `x` using the `__dict__` and `type`.
    """
    r = []
    
    for k, v in sorted( x.__dict__.items(), key = lambda y: y[0] ):
        if k.startswith( "_" ):
            continue
        
        r.append( "{}: {}".format( repr( k ), repr( v ) ) )
    
    return "{}({})".format( type( x ).__name__, string_helper.format_array( r ) )


def get_subclasses( class_: type ) -> Set[type]:
    """
    Gets set of subclasses (including the class itself), in no particular order.
    """
    assert isinstance( class_, type )
    
    stack = [class_]
    found = set( stack )
    
    while stack:
        cls1 = stack.pop( -1 )
        
        for cls2 in cls1.__subclasses__():
            if cls2 not in found:
                found.add( cls2 )
                stack.append( cls2 )
    
    return found
