import click


@click.command()
@click.argument('branch_name')
def branch(branch_name):
    """Create/Change branch in all repos"""
    from octohot.cli.config import repositories
    for repo in repositories:
        click.echo(repo.pprint('Branch %s' % branch_name))
        repo.branch(branch_name)
