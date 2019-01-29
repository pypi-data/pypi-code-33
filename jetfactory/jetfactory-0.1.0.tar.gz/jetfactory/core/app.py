# -*- coding: utf-8 -*-

from logging import getLogger
from sanic import Sanic

from jetfactory.log import LOGGING_CONFIG_DEFAULTS

from .settings import ApplicationSettings
from .error import JetErrorHandler
from .manager import jetmgr


class Application(Sanic):
    def __init__(self, **kwargs):
        self.packages = kwargs.pop('packages', [])

        try:
            overrides = dict(kwargs.pop('settings', {}))
        except ValueError:
            raise Exception('Application `settings` must be a collection')

        for name, logger in LOGGING_CONFIG_DEFAULTS['loggers'].items():
            logger['level'] = 'DEBUG' if overrides.get('DEBUG') else 'INFO'

        super(Application, self).__init__(
            kwargs.pop('name', 'jetfactory'),
            log_config=kwargs.pop('log_config', LOGGING_CONFIG_DEFAULTS),
            **kwargs
        )

        # Application root logger
        self.log = getLogger('root')

        # Apply known settings from ENV or provided `settings`
        self.config.update(ApplicationSettings(overrides).merged)

        self.error_handler = JetErrorHandler()

        # Listeners
        self.register_listener(jetmgr.attach, 'after_server_start')
        self.register_listener(jetmgr.detach, 'after_server_stop')

    def run(self, **kwargs):
        """Starts the server using settings validated in `ApplicationSettings`, or kwargs.

        :param kwargs:
            - :param host: Listen host, defaults to 127.0.0.1
            - :param port: Listen port, defaults to 8080
            - :param workers: Number of workers, defaults to get_one per core.
            - :param debug: Debug mode, default false
            - :param access_log: Enable/Disable access logging
        """

        debug = kwargs.pop('debug', self.config['DEBUG'])
        sql_log = kwargs.pop('sql_log', None)
        access_log = kwargs.pop('access_log', None)
        workers = kwargs.pop('workers', self.config['WORKERS'])

        # Enable access and sql log by default in debug mode, otherwise disable if it wasn't explicitly enabled.
        if debug:
            self.log.warning('Debug mode enabled')
            sql_log = sql_log is None or sql_log
            access_log = access_log is None or access_log

            if int(workers) > 1:
                self.log.warning('Automatic reload DISABLED due to multiple workers')

        # Configure SQL statement logging
        getLogger('peewee').setLevel('DEBUG' if sql_log else 'INFO')

        cfg = dict(
            host=kwargs.pop('host', self.config['LISTEN_HOST']),
            port=kwargs.pop('port', self.config['LISTEN_PORT']),
            workers=workers,
            debug=debug,
            access_log=access_log,
            **kwargs
        )

        self.log.info(f"Starting {cfg['workers']} worker(s) on address: {cfg['host']}:{cfg['port']}")

        super(Application, self).run(**cfg)
