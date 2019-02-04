# -*- coding: utf-8 -*-

"""Console script for iportal."""
import sys
import logging
import click
from .iportal import Iportal

logging.basicConfig(level=logging.WARNING)

@click.option('-r','--dssrc',help='The openbis login credentials stored in an ini-file')
@click.option('-u','--username',help='The openbis username')
@click.option('-p','--password',help='The openbis password')
@click.option('-i','--url',help='The openbis url')
@click.option('-d','--datamover_dir',help='The openbis datamover base-directory')
@click.group()
@click.pass_context
def main(ctx,dssrc,username,password,url,datamover_dir):
    if not username:
        try:
            (username,password,url,datamover_dir) = Iportal.read_dssrc(dssrc)
        except ValueError as error:
            print(str(error))
            sys.exit(0)
    ctx.obj = Iportal(username,password,url,datamover_dir,dssrc)
    return 0

@click.option('--arg1',help='arg1',default='default_arg1')
@click.command()
@click.pass_context
def write(ctx,arg1):
    """Write a workflow yaml file."""
    click.echo("Write: %s"%(arg1))
    return 0

@click.command()
@click.pass_context
def read(ctx):
    """Read a workflow yaml file."""
    click.echo("Read: %s"%(ctx.obj.username))
    return 0

main.add_command(write)
main.add_command(read)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
