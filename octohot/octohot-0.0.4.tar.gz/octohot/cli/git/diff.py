import click


@click.command()
def diff():
    """Get diff from all repos"""
    from octohot.cli.config import repositories
    for repo in repositories:
        if repo.tainted():
            click.echo(repo.print("Diff"))
            print('\n'.join(repo.diff()))
