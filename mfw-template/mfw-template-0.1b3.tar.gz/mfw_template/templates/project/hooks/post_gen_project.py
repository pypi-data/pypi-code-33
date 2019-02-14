import shutil

project_name = '{{ cookiecutter.project_name }}'
project_type = '{{ cookiecutter.project_type }}'

if project_type != 'morpcc':
    shutil.rmtree('%s/templates' % project_name)
