import ast

import pytest
from nose.tools import assert_true, assert_equal
from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from backend.visitor import ClassVisitor


@scenario('feature/ast_model_visitor.feature', 'visit models from file')
def test_visit_models_from_file():
    """visit models from file."""


@pytest.fixture
@given('models from file')
def models_from_file():
    """models from file."""
    buf = open('entity/models.py', 'r')
    model_file = buf.read()
    buf.close()
    return model_file


@pytest.fixture
@when('user model found')
def user_model_found(models_from_file, ):
    """user model found."""
    assert_true(models_from_file, )
    tree = ast.parse(models_from_file, )
    visitor = ClassVisitor()
    visitor.visit(tree)
    classes = visitor.get_classes
    return classes


@then('field name must be found')
def field_name_must_be_found(user_model_found):
    """field name must be found."""
    assert_true(user_model_found)
    for cls in user_model_found:
        fields = cls['User']['fields']
        assert_equal(fields[0]['name'], 'id')
        assert_equal(fields[0]['type'], 'Long')
        assert_equal(fields[1]['name'], 'phone_number')
        assert_equal(fields[1]['type'], 'String')
        assert_equal(fields[2]['name'], 'username')
        assert_equal(fields[2]['type'], 'String')
        assert_equal(fields[3]['name'], 'fullname')
        assert_equal(fields[3]['type'], 'String')
        assert_equal(fields[4]['name'], 'business_name')
        assert_equal(fields[4]['type'], 'String')
    pass
