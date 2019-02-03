# coding=utf-8
"""Service Edit generator feature tests."""
import pytest
from nose.tools import assert_equal, assert_true
from pytest_bdd import (
    scenario,
    then,
    when,
)

from backend.logger import logging
from backend.validator_method import *

log = logging.getLogger(__name__)


@Key(['username', 'fullname'])
def success(domain):
    return domain


@Key(['username'])
def fail_input_not_dict(domain):
    return domain


@Key(['unknown'])
def fail_input_unput_unknown(domain):
    return domain


@Key(['product.names'])
def fail_input_unput_type_list(domain):
    return domain


@scenario('feature/validator_key.feature', 'Validate Key success')
def test_validate_key_success():
    """Validate Key success."""


@pytest.fixture
@when('validate key success')
def validate_key_success():
    """validate key success."""
    input_dict = {'username': 'kiditz', 'fullname': 'Rifky aditya'}
    return success(input_dict)


@then('key must be not throw validate exception')
def key_must_be_not_throw_validate_exception(validate_key_success):
    """key must be not throw validate exception."""
    assert_true(isinstance(validate_key_success, dict))
    assert_equal(validate_key_success['username'], 'kiditz')
    assert_equal(validate_key_success['fullname'], 'Rifky aditya')


@scenario('feature/validator_key.feature', 'Validate Key Fail input unknown')
def test_validate_key_fail_input_unknown():
    """Validate Key Fail input unknown."""


@pytest.fixture
@when('validate key with input test')
def validate_key_with_input_test():
    """validate key with input test."""
    try:
        fail_input_unput_unknown({'test': 'test'})
    except ValidationException as e:
        return e


@then('key must be thrown validate exception with message unknown is required')
def key_must_be_thrown_validate_exception_with_message_unknown_is_required(validate_key_with_input_test):
    """key must be thrown validate exception with message unknown is required."""
    exception = validate_key_with_input_test
    assert_true(isinstance(exception, ValidationException))
    assert_equal(exception.message,
                 MESSAGE_INPUT_INVALID_KEY.format('unknown'))
    assert_equal(exception.key, 'unknown')


@scenario('feature/validator_key.feature', 'Validate Key Fail input must be list')
def test_validate_key_fail_input_must_be_list():
    """Validate Key Fail input must be list."""


@pytest.fixture
@when('validate key failed input product.items.name')
def validate_key_failed_input_productitemsname():
    """validate key failed input product.items.name."""
    try:
        fail_input_unput_type_list({'product': [{'unkown': ''}]})
    except ValidationException as e:
        return e


@then('key must be thrown validation exception with message items name is required')
def key_must_be_thrown_validation_exception_with_message_items_name_is_required(
        validate_key_failed_input_productitemsname):
    """key must be thrown validation exception with message items name is required."""
    exception = validate_key_failed_input_productitemsname
    assert_true(isinstance(exception, ValidationException))
    log.info(exception.message)
    log.info(exception.key)
    assert_equal(exception.message, MESSAGE_INPUT_INVALID_KEY.format('names'))
    assert_equal(exception.key, 'names[0]')
