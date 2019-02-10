# -*- coding: utf-8 -*-

"""Console script for appliapps."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for appliapps."""
    click.echo("collection of appliapps. This tool lists and finds appliapps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
