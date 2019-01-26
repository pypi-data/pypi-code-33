import argparse
from dodo_commands.framework import Dodo
from dodo_commands.framework.util import remove_trailing_dashes


def _args():
    parser = argparse.ArgumentParser()
    parser.add_argument('runserver_args', nargs=argparse.REMAINDER)
    args = Dodo.parse_args(parser)
    args.port = Dodo.get_config("/DJANGO/port", "8000")
    args.python = Dodo.get_config("/DJANGO/python")
    args.cwd = Dodo.get_config("/DJANGO/src_dir")
    args.runserver_args.extend(Dodo.get_config("/DJANGO/runserver_args", []))
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(
        [
            args.python,
            "manage.py",
            "runserver",
            "0.0.0.0:%s" % args.port,
        ] + remove_trailing_dashes(args.runserver_args),
        cwd=args.cwd)
