from .string import camel_to_snake


def keys_to_snake_case( d ):
    result = {}
    for k, v in d.items():
        if isinstance( k, str ):
            k = camel_to_snake( k )
        if isinstance( v, ( dict, list, tuple ) ):
            v = _inner_keys_to_snake_case( v )
        result[k] = v
    return result


def _inner_keys_to_snake_case( d ):
    if isinstance( d, dict ):
        return keys_to_snake_case( d )
    elif isinstance( d, list ):
        return [ _inner_keys_to_snake_case( a ) for a in d ]
    elif isinstance( d, tuple ):
        return tuple( _inner_keys_to_snake_case( a ) for a in d )
    return d
