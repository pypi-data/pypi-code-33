import os, sys
from pathlib import Path
import click
import yaml

def err_log(msg, *args):
    if args:
        msg %= args
    click.echo(click.style('Error: ', fg='red', bold=True) + msg)

# Read a yaml file given a file path. Shou
def read_yml(filepath):
    target_file = Path(filepath)

    if target_file.is_file():
        with open(target_file) as yml_file:
            return yaml.load(yml_file)
    else:
        click.echo(click.style('Error: ', fg='red', bold=True) +
            'Could not read the .yml at ' +
            click.style(filepath, bold=True))
        sys.exit()

# Determines the path to files inside the
# project. (i.e. the `data` directory)
def determine_project_path():
    """Borrowed from wxglade.py"""
    try:
        root = __file__
        if os.path.islink (root):
            root = os.path.realpath (root)
        return os.path.dirname (os.path.abspath (root))
    except:
        print("I'm sorry, but something is wrong.")
        print("There is no __file__ variable. Please contact the author.")
        sys.exit ()
