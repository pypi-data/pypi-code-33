# coding=utf-8
"""Service Edit generator feature tests."""
from nose.tools import assert_equal
from pytest import fixture
from pytest_bdd import (
    scenario,
    given,
    then,
    when,
)

from backend.logger import logging
from backend.validator import *

log = logging.getLogger(__name__)


@scenario('feature/validator_length.feature', 'Validate Size success',
          example_converters=dict(minimum=int, maximum=int))
def test_validate_size_success():
    """Validate Size success."""


@given('input message and username')
def input_message_and_username():
    """input message and username."""
    return {
        'username': 'Rifky',
        'message': 'this is test roger'
    }


@fixture
@when('length of value from key dict between <minimum> and <maximum>')
def length_of_value_from_key_dict_between_minimum_and_maximum(input_message_and_username, minimum, maximum):
    """length of value from key dict between <minimum> and <maximum>."""

    class MyService(object):
        @Size(['message', 'username'], minimum=minimum, maximum=maximum)
        def success(self, domain):
            return domain

    service = MyService()
    return service.success(input_message_and_username)


@then('validate must be not thrown exception')
def validate_must_be_not_thrown_exception(length_of_value_from_key_dict_between_minimum_and_maximum,
                                          input_message_and_username):
    """validate must be not thrown exception."""
    result = length_of_value_from_key_dict_between_minimum_and_maximum
    assert_equal(result['username'], input_message_and_username['username'])
    assert_equal(result['message'], input_message_and_username['message'])


@scenario('feature/validator_length.feature', 'Validate Size min less than max')
def test_validate_size_min_less_than_max():
    """Validate Size min less than max."""


@given('input message')
def input_message():
    """input message."""
    return {
        'message': 'this is test roger'
    }


@fixture
@when('minimum is less than <minimum> and <maximum>')
def minimum_is_less_than_minimum_and_maximum(input_message, minimum, maximum):
    """minimum is less than <minimum> and <maximum>."""

    class MyService(object):
        @Size(['message'], minimum=minimum, maximum=maximum)
        def error(self, domain):
            return domain

    try:
        service = MyService()
        service.error(input_message)
    except TypeError as e:
        return e.__str__()


@then('raise validation exception with message minimum gt maximum')
def raise_validation_exception_with_message_minimum_gt_maximum(minimum_is_less_than_minimum_and_maximum):
    """raise validation exception with message minimum gt maximum."""
    assert_equal(minimum_is_less_than_minimum_and_maximum, 'min 10 greater than max 0')
