#!/usr/bin/env python
"""create stdout_logfile and stderr_logfile files"""
import click
import supervisor_logs

MODULE_NAME = "supervisor_logs.create"
PROG_NAME = 'python -m %s' % MODULE_NAME
USAGE = 'python -m %s path ...' % MODULE_NAME


@click.command()
@click.argument('paths', nargs=-1, required=True)
def _cli(paths):
    for path in paths:
        supervisor_logs.create(path)


if __name__ == '__main__':
    _cli(prog_name=PROG_NAME)
