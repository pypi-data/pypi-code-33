from argparse import ArgumentParser, REMAINDER
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    parser.add_argument('git_args', nargs=REMAINDER)
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run(
        [
            "git",
        ] + args.git_args, cwd=Dodo.get_config("/ROOT/src_dir"))
