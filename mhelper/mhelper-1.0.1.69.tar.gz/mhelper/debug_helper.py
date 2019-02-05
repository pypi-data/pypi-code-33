def dump( _message = None, *args, **kwargs ):
    r = []
    seen = set()
    
    if _message is not None:
        r.append( _message )
    
    r.append( "(dump)" )
    
    for i, v in enumerate( args ):
        __dump_object( "[{}]".format( i ), v, r, seen )
    
    for k, v in kwargs.items():
        __dump_object( k, v, r, seen )
    
    return "\n".join( r )


def __dump_object( k, v, r, seen, i = 1 ):
    ind = ("|   " * i)
    
    r.append( ind + "{} ({}) = {}".format( k, type( v ).__name__, str_repr( v ) ) )
    
    if any( isinstance( v, x ) for x in (int, float, bool, str) ):
        return
    
    id_ = id( v )
    
    if id_ in seen:
        r.append( ind + "    - repeat" )
        return
    
    seen.add( id_ )
    
    if i > 10:
        r.append( ind + "    ..." )
        return
    
    for k2, v2 in __iter_fields( v ):
        __dump_object( k2, v2, r, seen, i + 1 )


def __iter_fields( obj ):
    if hasattr( obj, "__dict__" ):
        for k, v in obj.__dict__.items():
            if not k.startswith( "_" ):
                yield k, v
    
    from mhelper import reflection_helper
    for cls in reflection_helper.iter_hierarchy( type( obj ) ):
        if hasattr( cls, "__slots__" ):
            for slot in cls.__slots__:
                try:
                    yield "." + slot, getattr( obj, slot )
                except:
                    pass
    
    if hasattr( obj, "__iter__" ):
        try:
            for i, v2 in iter( obj ):
                yield "[{}]".format( i ), v2
        except:
            pass


def str_repr( v ):
    try:
        return repr( v )
    except Exception as ex:
        return "(cannot repr due to error: {}('{}'))".format( type( ex ).__name__, ex )


def dump_repr( obj, **kwargs ):
    if not kwargs:
        vs = __iter_fields( obj )
    else:
        vs = kwargs.items()
    
    if not isinstance( obj, str ):
        obj = type( obj ).__name__
    
    return "{}({})".format( obj, ", ".join( "{}={}".format( k, str_repr( v ) ) for k, v in vs ) )
