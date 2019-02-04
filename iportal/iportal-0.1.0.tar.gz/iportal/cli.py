# -*- coding: utf-8 -*-

"""Console script for iportal."""
import sys
import logging
import click
from .iportal import Iportal

logging.basicConfig(level=logging.WARNING)

#@click.option('-r','--dssrc',help='The openbis login credentials stored in an ini-file')
#@click.option('-u','--username',help='The openbis username')
#@click.option('-p','--password',help='The openbis password')
#@click.option('-i','--url',help='The openbis url')
#@click.option('-d','--datamover_dir',default='/datamover',help='The openbis datamover base-directory')
@click.group()
@click.argument('connection',envvar="IPORTAL_CONNECTION")
@click.pass_context
def main(ctx,connection): # dssrc,username,password,url,datamover_dir
    try:
        (username,url,password) = Iportal.parse_connection(connection)
    except ValueError as error:
        print(str(error))
        sys.exit(0)
    ctx.obj = Iportal(username,password,url)
    return 0

@click.option('--arg1',help='arg1',default='default_arg1')
@click.command()
@click.pass_context
def write(ctx,arg1):
    """Write a workflow yaml file."""
    ctx.obj.write(arg1=arg1)
    return 0
main.add_command(write)

@click.command()
@click.pass_context
def read(ctx):
    """Read a workflow yaml file."""
    ctx.obj.read()
    return 0
main.add_command(read)

@click.command()
@click.pass_context
def adduser(ctx):
    """Add a user."""
    ctx.obj.adduser()
    return 0
main.add_command(adduser)

@click.command()
@click.pass_context
def configure(ctx):
    """Configure iportal."""
    ctx.obj.configure()
    return 0
main.add_command(configure)

@click.command()
@click.pass_context
def status(ctx):
    """list available workflows."""
    ctx.obj.status()
    return 0
main.add_command(status)

@click.command()
@click.pass_context
def start(ctx):
    """Start iPortal."""
    ctx.obj.start()
    return 0
main.add_command(start)

@click.command()
@click.pass_context
def stop(ctx):
    """Stop iPortal."""
    ctx.obj.stop()
    return 0
main.add_command(stop)

@click.command()
@click.pass_context
def addcron(ctx):
    """Add iPortal crontab entry."""
    ctx.obj.addcron()
    return 0
main.add_command(addcron)

@click.command()
@click.pass_context
def build(ctx):
    """Build singularity container."""
    ctx.obj.build()
    return 0
main.add_command(build)

@click.command()
@click.pass_context
def cp(ctx):
    """Copy dataset."""
    ctx.obj.cp()
    return 0
main.add_command(cp)

@click.command()
@click.pass_context
def test(ctx):
    """Test workflow."""
    ctx.obj.test()
    return 0
main.add_command(test)

@click.command()
@click.pass_context
def submit(ctx):
    """List workflows."""
    ctx.obj.submit()
    return 0
main.add_command(submit)

@click.command()
@click.pass_context
def ls(ctx):
    """List workflows."""
    ctx.obj.ls()
    return 0
main.add_command(ls)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
