# -*- coding: utf-8 -*-
"""
flask loader module -  defines classes and methods that builds flask applications and blueprints.
"""
from ..events.app_hooks import AppHooks
from ..application.blueprint import AppBlueprint
from ..application.flask import FlaskApp
from ..utils import import_module


def find_blueprints(app):
    """
    Auto-discover INSTALLED_APPS modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """
    # recover app.config installed plugins
    BLUEPRINTS = app.config.get('BLUE_PRINTS', [])
    mods = []
    for blueprint in BLUEPRINTS:
        # Attempt to import the app's module.
        try:
            mod = import_module(blueprint)
            mods.append(mod)
        except:
            pass

    return mods


def register_blueprints(app):
    """
    Auto-discover INSTALLED BLUEPRINT APPS modules and register them to the app received as parameters.
    :param app: Already configured Flask app instance.
    :return: All registered BLUEPRINTS.
    """
    modules = find_blueprints(app)

    for mod in modules:
        hooks = AppHooks(mod.__name__)
        hooks.before_app_init.send(app)
        AppBlueprint(mod, app, hooks, app.config)


def build_flask_app(config):
    app_hooks = AppHooks()
    # runs the before app initialization hook
    app_hooks.before_app_init.send()
    app = FlaskApp(app_hooks, config)
    with app.app_context():
        register_blueprints(app)
    return app


def build_app(dev, instance):
    if dev:  # runs app in development mode
        app = build_flask_app(instance.app_config)
    else:
        from tripod.application.gunicorn import GunicornApp
        app = GunicornApp(instance.app_config)
        print(">>>>>", app)

    return app
