import click

from mangum.__version__ import __version__


@click.group()
def cli():
    pass


@cli.command()
def version():
    """Display the current version"""
    click.echo(f"Mangum v{__version__}")


@cli.command()
@click.argument("command")
def aws(command: str) -> None:
    if command == "init":
        print("OK")


cli = click.CommandCollection(sources=[cli])


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
