import os
import sys
import click
import importscan
import mfw_template
import yaml

@click.group()
@click.pass_context
def project(ctx=None):
    """Cookiecutter templates for Morp Framework"""
    localrc = os.path.join(os.getcwd(), '.mfwtemplaterc')
    c = {}
    if os.path.exists(localrc):
        with open(localrc, 'r') as f:
            c = yaml.load(f)

    ctx.ensure_object(dict)
    ctx.obj['RC'] = c


def cli():
    importscan.scan(mfw_template)
    project()
