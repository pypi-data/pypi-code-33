# pylint: disable=no-self-use
import os
import pytest

from miniscule import load_config


class TestConfigLoader:
    @pytest.mark.parametrize(
        'res,stream', [(None, '!or [null]'), (1, '!or [1]'),
                       ('hello', '!or [hello]'),
                       ('hello', '!or [null, hello]'),
                       ('hello', '!or [null, hello, null]'),
                       ('hello', '!or [null, hello, 1, null]')])
    def test_or_tag_selects_first_value_that_is_not_null(self, res, stream):
        assert load_config(stream) == res

    @pytest.mark.parametrize(
        'res,value', [(5000, '5000'), (500.1, '500.1'),
                      ('localhost', 'localhost')])
    def test_env_converts_environment_value_per_yaml_rules(self, res, value):
        os.environ['PORT'] = value
        assert load_config('!env PORT') == res
        del os.environ['PORT']

    def test_env_returns_none_if_argument_not_in_environment(self):
        assert load_config('!env HOST') is None
