import sys
import click


def error(message, exit=True):
    click.secho("ERROR: " + message, fg="red")
    if exit:
        sys.exit(1)


def success(message):
    click.secho("SUCCESS: " + message, fg="green")


def info(message):
    click.secho("INFO: " + message, fg="blue")
