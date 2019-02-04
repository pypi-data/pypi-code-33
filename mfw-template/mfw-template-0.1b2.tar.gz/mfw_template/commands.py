from cookiecutter.main import cookiecutter
from .cli import project
import click
from pkg_resources import resource_filename
import os
import yaml


@project.command(help='create a new MorpFW project')
def create_project():
    cookiecutter(resource_filename('mfw_template', 'templates/project'))


@project.command(help='create a new resource type')
@click.pass_context
def create_resource(ctx):
    project_name = ctx.obj['RC']['project_name']
    cookiecutter(resource_filename('mfw_template', 'templates/resource'),
                 output_dir=project_name)
