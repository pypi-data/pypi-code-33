from .regex import separate_camelcase_phase_1, separate_camelcase_phase_2
from .__string import codepoint, replacement
from collections import defaultdict


__all__ = [ 'camel_to_snake' ]


def camel_to_snake( s ):
    result = separate_camelcase_phase_1.sub( r'\1_\2', s )
    result = separate_camelcase_phase_2.sub( r'\1_\2', result ).lower()
    return result


def fold_to_ascii( s ):
    if s is None:
        raise NotImplementedError
    if not isinstance( s, str ):
        raise NotImplementedError

    def none_factory():
        return None
    translate_table = codepoint + replacement
    default_translate_table = defaultdict( none_factory, translate_table )

    return s.translate( default_translate_table )
