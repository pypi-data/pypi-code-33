"""
limix boostrap theme
====================

A flexible and fast generalised mixed model toolbox.
"""

from ._testit import test

__version__ = "0.0.4"


def get_html_theme_path():
    """ Return list of HTML theme paths. """
    import os

    cur_dir = os.path.abspath(os.path.dirname(__file__))
    return [cur_dir]


def setup(app):
    import os

    app.add_html_theme(
        "bootstrap-limix",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "bootstrap-limix")),
    )


__all__ = ["__version__", "setup", "get_html_theme_path", "test"]
