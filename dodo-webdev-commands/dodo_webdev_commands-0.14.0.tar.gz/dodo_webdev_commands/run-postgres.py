from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()
    Dodo.run([
        "sudo",
        "-u",
        "postgres",
        "/usr/lib/postgresql/9.5/bin/postgres",
        "-D"
        "/var/lib/postgresql/9.5/main",
        "-c",
        "config_file=/etc/postgresql/9.5/main/postgresql.conf",
    ],
             cwd="/")
