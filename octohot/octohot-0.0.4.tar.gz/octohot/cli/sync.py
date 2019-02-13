import click


@click.command()
def sync():
    """Sync: Clone, reset, delete unpushed Branches, pull"""
    from octohot.cli.config import repositories
    for repo in repositories:
        click.echo(repo.print("Sync: Clone, reset, delete unpushed Branches, "
                              "pull"))
        repo.clone()
        repo.reset()
        repo.branch(repo.default_branch())
        repo.delete_unpushed_branches()
        repo.pull()
