import click


@click.command()
def add():
    """Add all unstaged files to stage"""
    from octohot.cli.config import repositories
    for repo in repositories:
        if repo.tainted():
            click.echo(repo.print("Add"))
            repo.add()
