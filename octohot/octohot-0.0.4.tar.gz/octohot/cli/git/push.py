import click


@click.command()
@click.argument('branch_name')
def push(branch_name):
    """Push all repos"""
    from octohot.cli.config import repositories
    for repo in repositories:
        if repo.branch_has_diff_from_master(branch_name):
            click.echo(repo.print(f"Push {branch_name}"))
            repo.push(branch_name)
