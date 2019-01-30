# -*- coding: utf-8 -*-
"""
Module flask.py
----------------------
A flask application wrapper to be used by tripod.
It basically overrides the Flask Config object and adds some application event events
to the Flask application object.
"""
from flask import Flask
import os
import atexit
from tripod import utils


class FlaskApp(Flask):
    """The flask object implements a WSGI application and acts as the central
        object.  It is passed the name of the module or package of the
        application.  Once it is created it will act as a central registry for
        the view functions, the URL rules, template configuration and much more.

        The name of the package is used to resolve resources from inside the
        package or the folder the module is contained in depending on if the
        package parameter resolves to an actual python package (a folder with
        an :file:`__init__.py` file inside) or a standard module (just a ``.py`` file).

        For more information about resource loading, see :func:`open_resource`.

        Usually you create a :class:`Flask` instance in your main module or
        in the :file:`__init__.py` file of your package like this::

            from flask import Flask
            app = Flask(__name__)

        .. admonition:: About the First Parameter

            The idea of the first parameter is to give Flask an idea of what
            belongs to your application.  This name is used to find resources
            on the filesystem, can be used by extensions to improve debugging
            information and a lot more.

            So it's important what you provide there.  If you are using a single
            module, `__name__` is always the correct value.  If you however are
            using a package, it's usually recommended to hardcode the name of
            your package there.

            For example if your application is defined in :file:`yourapplication/app.py`
            you should create it with one of the two versions below::

                app = Flask('yourapplication')
                app = Flask(__name__.split('.')[0])

            Why is that?  The application will work even with `__name__`, thanks
            to how resources are looked up.  However it will make debugging more
            painful.  Certain extensions can make assumptions based on the
            import name of your application.  For example the Flask-SQLAlchemy
            extension will look for the code in your application that triggered
            an SQL query in debug mode.  If the import name is not properly set
            up, that debugging information is lost.  (For example it would only
            pick up SQL queries in `yourapplication.app` and not
            `yourapplication.views.frontend`) 
    """

    def __init__(self, app_hooks, config):
        """
        Flask app function initialization;
        :param import_name: the name of the application package
        :param static_url_path: can be used to specify a different path for the
                                static files on the web.  Defaults to the name
                                of the `static_folder` folder.
        :param static_folder: the folder with static files that should be served
                              at `static_url_path`.  Defaults to the ``'static'``
                              folder in the root path of the application.
        :param template_folder: the folder that contains the templates that should
                                be used by the application.  Defaults to
                                ``'templates'`` folder in the root path of the
                                application.
        :param instance_path: An alternative instance path for the application.
                              By default the folder ``'instance'`` next to the
                              package or module is assumed to be the instance
                              path.
        :param instance_relative_config: if set to ``True`` relative filenames
                                         for loading the config are assumed to
                                         be relative to the instance path instead
                                         of the application root.
        :param root_path: Flask by default will automatically calculate the path
                          to the root of the application.  In certain situations
                          this cannot be achieved (for instance if the package
                          is a Python 3 namespace package) and needs to be
                          manually defined.
        """
        super().__init__(
            import_name=config.get("flask.app_name", "app"),
            static_url_path=config.get("flask.static_url_path", None),
            static_folder=config.get("flask.static_folder", 'static'),
            static_host=config.get("flask.static_path", None),
            host_matching=bool(config.get("flask.host_matching", False)),
            subdomain_matching=bool(config.get("flask.subdomain_matching", False)),
            template_folder=config.get("flask.template_folder", 'templates'),
            instance_path=config.get("flask.instance_path", os.getcwd()),
            instance_relative_config=bool(config.get("flask.instance_relative_config", False)),
            root_path=config.get("flask.root_path", None)
        )
        # update our custom config with the flask.config dict
        for key, value in self.config.items():
            if key not in config:
                config[key] = value
        # overrides flask.config with our custom config
        self.config = config
        # application events
        self.events = app_hooks
        # register at_exit function to be called when any terminate signal is captured
        atexit.register(self.at_exit)

        self.events.on_app_init.send(self)

    def at_exit(self):
        self.events.on_app_exit.send(self)

    def load_urls(self):
        """
        Loads urls.py file ensuring compatibility with older versions that uses urls.py file
        """
        if utils.check_module_existence('urls'):

            app_dotted_path = 'urls.register_urls'

            loader_func = utils.import_string(app_dotted_path)
            if not callable(loader_func):
                raise TypeError(
                    "'register_urls' must be a callable object."
                    "'register_urls' also must have the following signature:"
                    "'register_urls(app)'"
                )

            loader_func(self)

    def run(self, host=None, port=None, debug=None,
            load_dotenv=True, **options):
        """Runs the application on a local development server.

        Do not use ``run()`` in a production setting. It is not intended to
        meet security and performance requirements for a production server.
        Instead, see :ref:`deployment` for WSGI server recommendations.

        If the :attr:`debug` flag is set the server will automatically reload
        for code changes and show a debugger in case an exception happened.

        If you want to run the application in debug mode, but disable the
        code execution on the interactive debugger, you can pass
        ``use_evalex=False`` as parameter.  This will keep the debugger's
        traceback screen active, but disable code execution.

        It is not recommended to use this function for development with
        automatic reloading as this is badly supported.  Instead you should
        be using the :command:`flask` command line script's ``run`` support.

        .. admonition:: Keep in Mind

           Flask will suppress any server error with a generic error page
           unless it is in debug mode.  As such to enable just the
           interactive debugger without the code reloading, you have to
           invoke :meth:`run` with ``debug=True`` and ``use_reloader=False``.
           Setting ``use_debugger`` to ``True`` without being in debug mode
           won't catch any exceptions because there won't be any to
           catch.

        :param host: the hostname to listen on. Set this to ``'0.0.0.0'`` to
            have the server available externally as well. Defaults to
            ``'127.0.0.1'`` or the host in the ``SERVER_NAME`` config variable
            if present.
        :param port: the port of the webserver. Defaults to ``5000`` or the
            port defined in the ``SERVER_NAME`` config variable if present.
        :param debug: if given, enable or disable debug mode. See
            :attr:`debug`.
        :param load_dotenv: Load the nearest :file:`.env` and :file:`.flaskenv`
            files to set environment variables. Will also change the working
            directory to the directory containing the first file found.
        :param options: the options to be forwarded to the underlying Werkzeug
            server. See :func:`werkzeug.serving.run_simple` for more
            information.
        """
        host = self.config.get("flask.host", None)
        port = self.config.get("flask.port", None)
        debug = self.config.get("flask.debug", None)
        load_dotenv = self.config.get("flask.load_dotenv", None)
        super().run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)
