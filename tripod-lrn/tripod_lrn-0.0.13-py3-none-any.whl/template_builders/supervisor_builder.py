# -*- coding: utf-8 -*-
"""
Template Builders module: 
    Functions that builds supervisor project templates.
"""
from invoke import task
from cookiecutter.main import cookiecutter
import os


@task
def init_supervisor_project(context):
    """
    Initialize project file structure in the current directory.
    """
    builder_dir = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.join(builder_dir, "templates/supervisor.zip")
    # Create project from the cookiecutter-pypackage/ template
    cookiecutter(template_path)

@task
def init_rq_worker(context):
    """
    Initialize project file structure in the current directory.
    """
    builder_dir = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.join(builder_dir, "templates/rq-worker.zip")
    # Create project from the cookiecutter-pypackage/ template
    cookiecutter(template_path)
