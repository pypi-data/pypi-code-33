import click


@click.command()
def reset():
    """Reset all repos"""
    from octohot.cli.config import repositories
    for repo in repositories:
        repo.print("Reset")
        repo.reset()
