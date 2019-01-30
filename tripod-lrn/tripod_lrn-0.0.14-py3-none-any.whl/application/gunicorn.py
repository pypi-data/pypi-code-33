# -*- coding: utf-8 -*-
"""
application application module -
    defines a simple and generic application application class used to run flask applications 
    from the flask_manager package.
                               
"""
from gunicorn.app.base import Application
from tripod.application.app_factory.flask_factory import create_flask_app


class GunicornApp(Application):
    """
    Gunicorn application class.
    """

    def __init__(self, config):
        self.config = config
        self.application = create_flask_app(self.config)
        super(GunicornApp, self).__init__()

    def load_config(self):
        # def init(self, parser, opts, args):
        path = self.config.get("GUNICORN.CONFIG_PATH", "settings/config.py")
        self.load_config_from_module_name_or_filename(path)

    def load(self):
        flask_app = create_flask_app(self.config)
        return flask_app