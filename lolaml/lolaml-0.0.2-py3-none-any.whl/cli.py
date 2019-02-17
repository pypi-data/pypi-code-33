import random
from pathlib import Path

import click
import log

import lolaml as lola
from lolaml.server import app


@click.group()
def cli():
    log.init()
    """Lola - track, manage, and visualize your ML runs."""


@cli.command()
def ui_flask():
    """Start the local flask UI and in DEV mode."""
    app.run(debug=True)


@cli.command()
@click.option("-n", help="Number of runs to create.", default=10)
def mkdata(n):
    """Create lola testdata under `testdata/`."""
    path = Path("testdata")
    path.mkdir(exist_ok=True)
    print(f"# Creating (or adding) testdata. Check {path}")
    print()

    archs = ["lin_reg", "conv_net", "fully_connected", "rnn"]
    for i in range(n):
        with lola.run(path_prefix=path) as run:
            print(run.data.path)

            run.log_param("arch", random.choice(archs))
            lr = random.random()
            run.log_param("lr", lr)
            epochs = random.randint(50, 100)
            run.log_param("epochs", epochs)

            for i in range(1, epochs + 1):
                run.log_metric("train_loss", 1 / i + random.random() / i, step=i)
                run.log_metric("val_loss", 1 / i + random.random() / i, step=i)


@cli.command()
@click.argument("path")
def push(path):
    """Push all local runs to the server."""
    print("TODO not implemented yet")


if __name__ == '__main__':  # pragma: no cover
    cli()
