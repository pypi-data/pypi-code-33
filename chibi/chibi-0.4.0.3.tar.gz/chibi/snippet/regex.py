import re


camelcase = re.compile( r'([A-Z][a-z]+)|([a-z]+[A-Z])' )
separate_camelcase_phase_1 = re.compile( r'(.)([A-Z][a-z]+)' )
separate_camelcase_phase_2 = re.compile( r'([a-z0-9])([A-Z])' )


def test( regex, text ):
    return bool( regex.search( text ) )


def is_camelcase( text ):
    return test( camelcase, text )
