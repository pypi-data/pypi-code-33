# -*- coding: utf-8 -*-
"""
Module blueprint.py
----------------------
A flask bluprint application wrapper to be used by tripod.
It basically overrides the Flask Config object and adds some application event events
to the Flask application object.
"""
from flask import Blueprint
import atexit
from tripod import utils


class AppBlueprint(Blueprint):
    """Represents a blueprint.  A blueprint is an object that records
    functions that will be called with the
    :class:`~flask.blueprints.BlueprintSetupState` later to register functions
    or other things on the main application.  See :ref:`blueprints` for more
    information.
    """
    def __init__(self, mod, app, hooks, config):
        super().__init__(
            name=mod.__name__.split('.')[-1],
            import_name=mod.__name__,
            static_folder=config.get("static_folder", 'static'),
            static_url_path=config.get("static_url_path", ''),
            template_folder=config.get("template_folder", 'templates'),
            url_prefix=config.get("url_prefix", None),
            subdomain=config.get("subdomain", None),
            url_defaults=config.get("url_defaults", None),
            root_path=config.get("root_path", None)
        )

        for key, value in config.items():
            app.config["bl_{}_{}".format(mod.__name__, key)] = value

        self.events = hooks
        # register at_exit function to be called when any terminate signal is captured
        atexit.register(self.at_exit)
        self.events.on_app_init.send(self)

        self.load_urls(mod.__name__)

        app.register_blueprint(self, url_prefix="/" + self.name)

    def at_exit(self):
        self.events.on_app_exit.send(self)

    def load_urls(self, name):
        """
        Loads urls.py file ensuring compatibility with older versions that uses urls.py file
        """
        if utils.check_module_existence('{}.urls'.format(name)):

            app_dotted_path = 'urls.register_urls'

            loader_func = utils.import_string(app_dotted_path)
            if not callable(loader_func):
                raise TypeError(
                    "'register_urls' must be a callable object."
                    "'register_urls' also must have the following signature:"
                    "'register_urls(app)'"
                )

            loader_func(self)
