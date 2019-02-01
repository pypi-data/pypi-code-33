from argparse import ArgumentParser
from dodo_commands.framework import Dodo


def _args():
    parser = ArgumentParser()
    args = Dodo.parse_args(parser)
    return args


if Dodo.is_main(__name__):
    args = _args()

    Dodo.run([
        "/bin/bash", "-c",
        "sudo -u postgres " + "psql -U wagtail " + "-d wagtail " +
        "-h $PG_PORT_5432_TCP_ADDR --port=$PG_PORT_5432_TCP_PORT"
    ])
