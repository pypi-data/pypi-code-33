"""
state store for the click application
"""
import click
import json


class State:
    """state object for click"""

    def __init__(self):
        """constructor"""
        self.verbose = False


def get_state():
    """gets the current state of the click app"""
    return click.get_current_context().ensure_object(State)


def debug(text):
    """only prints if verbose mode is on"""
    state = get_state()
    if state.verbose:
        if isinstance(text, dict):
            text = json.dumps(text, indent=2, sort_keys=True)
        click.echo(click.style(text, fg="green"), err=True)
