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
