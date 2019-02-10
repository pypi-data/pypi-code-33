from .test_data import input_dict, expected_output
from map_dictionary_keys import map_dictionary_keys


def to_upper(string):
    return string.upper()


class TestMapDictionaryKeys(object):
    def test_valid_case(self):
        assert map_dictionary_keys.map_dictionary_keys(input_dict, to_upper) == expected_output
