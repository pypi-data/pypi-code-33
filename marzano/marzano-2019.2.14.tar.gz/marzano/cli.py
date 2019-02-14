# -*- coding: future_fstrings -*-

"""Console script for marzano."""
import sys
import click
from marzano import powerlaw


@click.command()
def main(args=None):
    """Console script for marzano."""
    click.echo("Marzano Power Law Calculator")
    click.echo("Enter the first score")
    grades = []

    new_grade = click.prompt("Enter a grade")
    while new_grade is not "":
        grades.append(int(new_grade))
        click.echo(f"Power Score: {powerlaw(grades)}")
        new_grade = click.prompt("Enter a grade", default="", show_default=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
