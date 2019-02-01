from argparse import ArgumentParser
from dodo_commands.framework import Dodo
import os


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    args.node_modules_dir = Dodo.get_config('/SERVER/node_modules_dir', '')
    venv_dir = Dodo.get_config('/SERVER/venv_dir', '')
    args.pip = (os.path.join(venv_dir, 'bin', 'pip') if venv_dir else '')
    args.requirements_filename = Dodo.get_config('/SERVER/pip_requirements',
                                                 '')
    args.yarn = 'yarn'
    return args


if Dodo.is_main(__name__, safe=True):
    args = _args()

    if args.requirements_filename:
        Dodo.run([args.pip, 'install', '-r', args.requirements_filename])

    if args.node_modules_dir:
        Dodo.run([args.yarn, 'install'],
                 cwd=os.path.abspath(
                     os.path.join(args.node_modules_dir, '..')))
