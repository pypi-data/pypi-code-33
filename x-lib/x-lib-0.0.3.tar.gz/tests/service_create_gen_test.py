"""Service create generator feature tests."""

import ast
import logging
import os

from nose.tools import assert_is_instance, assert_equal, assert_true
from pytest import fixture
from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from backend.apigen import to_snake_case, get_class_name, write, render_template, get_fields, is_function_exists
from backend.visitor import ClassVisitor
from backend.service_generator import generate_service_create
log = logging.getLogger(__name__)


@scenario('feature/service_create_gen.feature', 'visit file model from models.py')
def test_visit_file_model_from_modelspy():
    """visit file model from models.py."""


@fixture
@given('file user file models')
def file_user_file_models():
    """file user file models."""
    buf = open('entity/models.py', 'r')
    model_file = buf.read()
    buf.close()
    assert_is_instance(model_file, str)
    return model_file


@fixture
@when('user model found read entity classes')
def user_model_found_read_entity_classes(file_user_file_models):
    """user model found read entity classes."""
    tree = ast.parse(file_user_file_models, )
    visitor = ClassVisitor()
    visitor.visit(tree)
    classes = visitor.get_classes
    assert_is_instance(classes, list)
    assert_equal(len(classes), 1)
    return classes


@then('service must be generated as user_service.py with method create')
def service_must_be_generated_as_user_servicepy_with_method_create(user_model_found_read_entity_classes):
    """service must be generated as user_service.py with method create."""
    classes = user_model_found_read_entity_classes
    classes_names = '\n'.join(map(str, [i[0] for i in get_class_name(classes)]))
    log.info('Classes %s', classes)
    class_name = 'User'
    input_dict = {'class_name_snake': to_snake_case(classes_names), 'class_name': class_name}
    log.info('Input : %s', input_dict)
    service_dir = 'service'
    service_file = '{}/{}_service.py'.format(service_dir, input_dict['class_name_snake'])
    if not os.path.isdir(service_dir):
        os.makedirs(service_dir)
        write(service_file, render_template('service_base.txt', input_dict))
        #write('{}/__init__.py'.format(service_dir), '')
    assert_true(os.path.isdir(service_dir))
    assert_true(os.path.isfile(service_file))
    input_dict['fields'] = get_fields(key=class_name, classes=classes)
    generate_service_create(input_dict, class_name, service_file)
    assert_equal(is_function_exists(service_file, 'add_user'), True)
    # os.remove(service_file)
    # os.removedirs(service_dir)

