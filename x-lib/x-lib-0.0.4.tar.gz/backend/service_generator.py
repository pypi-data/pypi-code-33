import ast
import os
from argparse import ArgumentParser

from backend.apigen import get_fields
from backend.apigen import render_template, is_function_not_exists, to_snake_case, append, ClassVisitor, get_class_name, \
    get_field_name, write
from backend.string_utils import is_not_empty
from .logger import logging

log = logging.getLogger(__name__)


def generate_service_create(input_dict=None, class_name=None, service_file=None):
    input_dict['method_name'] = to_snake_case('Add' + class_name)
    if is_function_not_exists(service_file, input_dict['method_name']):
        append(service_file, render_template('service_add.txt', input_dict))
        log.info('Successfully generated module in {}...'.format(service_file))
    else:
        log.info('function with name {}'.format(input_dict['method_name']))


def generate_service_edit(input_dict=None, class_name=None, service_file=None, filter_by='id'):
    input_dict['method_name'] = to_snake_case('Edit' + class_name)
    filter_by_list = []
    service_name = ''
    if ',' in filter_by:
        split = filter_by.split(',')
        for filter_key in split:
            if filter_key.strip() not in get_field_name(input_dict['fields']):
                print('You are not lucky, your model does not have {}'.format(filter_key.strip()))
                return
            else:
                filter_by_list.append(filter_key.strip())
                service_name = input_dict['method_name'] + '_by_' + '_and_'.join(filter_by_list)
        pass
    else:
        if filter_by not in get_field_name(input_dict['fields']):
            filter_by = ''
        else:
            service_name = input_dict['method_name'] + '_by_' + filter_by
    input_dict['filter_by'] = filter_by
    input_dict['filter_by_list'] = filter_by_list
    if is_function_not_exists(service_file, service_name):
        append(service_file, render_template('service_edit.txt', input_dict))
        log.info('Successfully generated module in {}...'.format(service_file))
    else:
        log.info('function with name {}'.format(input_dict['method_name']))


def main():
    parser = ArgumentParser()
    parser.add_argument('-m', '--model', help='Input the model file from your data storage')
    parser.add_argument('-s', '--service', help='The target service directory you want to save')
    parser.add_argument('-c', '--classname', help='The class name in the model you want to generate')
    parser.add_argument('-t', '--type', help='Type the generator you want to choose')
    try:
        args = parser.parse_args()
        buf = open(args.model, 'r')
        model_file = buf.read()
        buf.close()
        service = args.service
        class_name = args.classname
        _type = args.type
        tree = ast.parse(model_file, '')
        # Abstract Syntax Tree to parse classes as dictionary
        visitor = ClassVisitor()
        visitor.visit(tree)
        classes = visitor.get_classes

        # Start Generator
        classes_names = '\n'.join(map(str, [i[0] for i in get_class_name(classes)]))
        log.info(classes_names)
        input_dict = {
            'class_name_snake': to_snake_case(class_name),
            'class_name': class_name,
            'fields': get_fields(key=class_name, classes=classes)
        }
        service_file = '{}/{}_service.py'.format(service, input_dict['class_name_snake'])
        if not os.path.isdir(service):
            log.info("Create new directory %s", service)
            os.makedirs(service)
            write(service_file, render_template('service_base.txt', input_dict))
            write('{}/__init__.py'.format(service), '')
        else:
            log.info("Does'nt need create dictionary because it's has been exists")
        if _type.lower() == 'create':
            generate_service_create(input_dict, class_name, service_file)
        elif _type.lower() == 'edit':
            log.info('\r\n'.join(map(str, [field['name'] for field in input_dict['fields']])))
            filter_by = input('Edit By : ')
            if is_not_empty(filter_by):
                generate_service_edit(input_dict, class_name, service_file, filter_by)
            else:
                generate_service_edit(input_dict, class_name, service_file)

    except Exception as e:
        log.exception(e, exc_info=True)
