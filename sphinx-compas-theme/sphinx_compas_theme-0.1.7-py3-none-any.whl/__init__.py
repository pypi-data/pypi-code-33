import os


__version__ = '0.1.7'


def get_html_theme_path():
    theme_path = os.path.abspath(os.path.dirname(__file__))
    return [theme_path]


def setup(app):
    if hasattr(app, 'add_html_theme'):
        theme_path = get_html_theme_path()[0]

        app.add_html_theme('compas', os.path.join(theme_path, 'compas'))
        app.add_html_theme('compaspkg', os.path.join(theme_path, 'compaspkg'))
