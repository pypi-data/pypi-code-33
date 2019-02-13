import click


@click.command()
@click.argument('commit_name')
@click.argument('commit_description')
def commit(commit_name, commit_description):
    """Commit added changes in all repos"""
    from octohot.cli.config import repositories
    for repo in repositories:
        if repo.tainted():
            click.echo(repo.print(f'Commit {commit_name}'))
            repo.commit(commit_name, commit_description)
