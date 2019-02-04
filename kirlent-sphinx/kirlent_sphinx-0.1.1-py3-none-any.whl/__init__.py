# Copyright (C) 2019 H. Turgut Uyar <uyar@tekir.org>

from pathlib import Path

from . import slides, tables


__version__ = "0.1.1"


_template_path = Path(__file__).parent.joinpath("templates")


def get_path():
    """Get the base path for templates.

    :sig: () -> str
    :return: Base path for the templates of this extension.
    """
    return str(_template_path)


def setup(app):
    """Register this extension with Sphinx.

    This will add the directives and themes of this extension to Sphinx.

    :sig: (sphinx.application.Sphinx) -> Dict[str, str]
    :param app: Sphinx application to register this extension with.
    :return: Information about this extension.
    """
    tables.setup(app)
    slides.setup(app)
    app.add_html_theme("kirlent", str(Path(_template_path, "kirlent")))
    return {"version": __version__}
