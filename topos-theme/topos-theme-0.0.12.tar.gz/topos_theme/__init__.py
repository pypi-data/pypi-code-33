from os import path


__version__ = "0.0.12"


def update_context(app, pagename, templatename, context, doctree):
    context["topos_theme_version"] = __version__


def setup(app):

    if hasattr(app, "add_html_theme"):
        app.add_html_theme("topos-theme", path.abspath(path.dirname(__file__)))

    app.connect("html-page-context", update_context)

    return {"version": __version__, "parallel_read_safe": True}
