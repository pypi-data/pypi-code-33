import logging
from abc import ABCMeta, abstractmethod

import pytest
from webtest import TestApp

LOGGING_LEVEL = logging.getLevelName(logging.INFO)
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'loggers': {
        'ingredients_http': {
            'level': LOGGING_LEVEL,
            'handlers': ['console']
        },
        'cherrypy.access': {
            'level': 'INFO',
            'handlers': ['console']
        },
        'cherrypy.error': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
}


class APITestCase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def app_cls(self):
        raise NotImplementedError

    @abstractmethod
    def setup_mounts(self, app):
        pass

    @pytest.yield_fixture()
    def app(self):
        app = self.app_cls()(logging_config=LOGGING_CONFIG)
        self.setup_mounts(app)

        app.setup()

        yield app

    @pytest.yield_fixture()
    def wsgi(self, app):
        yield TestApp(app.wsgi_application)
