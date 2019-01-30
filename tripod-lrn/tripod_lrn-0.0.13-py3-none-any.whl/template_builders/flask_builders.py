# -*- coding: utf-8 -*-
"""
Template Builders module: 
    Functions that builds flask project templates.
"""
from invoke import task
from cookiecutter.main import cookiecutter
import os


@task
def init_flask_project(context):
    """
    Initialize project file structure in the current directory.
    """
    builder_dir = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.join(builder_dir, "templates/flask.zip")
    # Create project from the cookiecutter-pypackage/ template
    cookiecutter(template_path)

@task
def init_flask_blueprint(context, name):
    # get project installation path at run time
    builder_dir = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.join(builder_dir, "templates/flask_blueprint.zip")
    # Create project from the cookiecutter-pypackage/ template
    cookiecutter(template_path)

    # updating settings.py file
    settings_path = 'settings/settings.py'
    if not os.path.exists(settings_path):
        if not os.path.exists('settings.py'):
            raise FileNotFoundError("Could not find settings.py file.")
        settings_path = 'settings.py' \
                        ''
    settings_text = ''
    with open(settings_path, 'r') as f:
        settings_text = f.read()
    settings_text = settings_text.replace(
        'BLUE_PRINTS = [',
        'BLUE_PRINTS = ["{}", '.format(name)
    )

    with open(settings_path, 'w') as f:
        f.write(settings_text)
