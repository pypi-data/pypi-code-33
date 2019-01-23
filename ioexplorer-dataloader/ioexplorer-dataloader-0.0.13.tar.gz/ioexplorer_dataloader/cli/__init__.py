import click

# So that ioexplorer_dataloader.cli.dataset refers to the module,
# not to these objects.
from .database import database as _database
from .dataset import dataset as _dataset


@click.group()
def cli():
    # CLI Entrypoint
    pass  # pragma: no cover


cli.add_command(_database)
cli.add_command(_dataset)

if __name__ == "__main__":  # pragma: no cover
    cli()
