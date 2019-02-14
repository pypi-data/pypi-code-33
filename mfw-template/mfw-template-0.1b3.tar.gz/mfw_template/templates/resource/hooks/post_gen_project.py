import shutil
import os

project_name = '{{ cookiecutter.project_name }}'
project_type = '{{ cookiecutter.project_type }}'
module_name = '{{ cookiecutter.module_name }}'

if project_type != 'morpcc':
    os.unlink('modelui.py')
