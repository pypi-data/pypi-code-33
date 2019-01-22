import morpfw
from morpcc.app import App as BaseApp


class App(BaseApp):
    pass


@App.template_directory()
def get_template_directory():
    return 'templates'
