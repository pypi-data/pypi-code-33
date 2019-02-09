"""Factory for creating a service app"""

import json
import logging
import logging.config
import os
import time
import traceback
import uuid
from http import HTTPStatus

import yaml
from flask import Flask, g, jsonify, request

logger = logging.getLogger(__name__)


def create_app(env, config_module, logging_config_file=None):
    """
    Creates a Flask app to be used as a datasource service.

    Args:
        env (str): the deployment environment; 'env' determines
            the config class name to be loaded from
            'config_module'. E.g., if 'env' is passed as 'local',
            config class ConfigLocal will be loaded.
        config_module (module): a module in which to find config
            classes
        logging_config_file (str, optional): logging config file
            in YAML format; if None no logging will be setup

    Raises:
        ValueError: when config class for 'env' cannot be loaded

    Returns:
        Flask: the flask app
    """

    assert env
    assert config_module

    config_class_name = f'Config{env.capitalize()}'
    logger.info('Loading config from class %s in module %s',
                config_class_name, config_module)
    config_obj = getattr(config_module, config_class_name)
    if not config_obj:
        raise ValueError(f'Unable to load config class {config_class_name} from {config_module}')

    app = Flask(config_obj.APP_NAME)

    if logging_config_file:
        app.logger.disabled = True
        with open(logging_config_file, 'r') as f:
            logging_cfg = yaml.load(f)
            logging.config.dictConfig(logging_cfg)

    app.config.from_object(config_obj)
    app.secret_key = os.urandom(24)

    def body_str(entity):
        if entity.json: # pylint: disable=no-else-return
            return json.dumps(entity.json, ensure_ascii=False, indent=True)
        elif entity.data:
            try:
                return entity.data.decode('utf-8').replace('\n', ' ')
            except: # pylint: disable=bare-except
                return str(entity.data)
        else:
            return ''

    @app.before_request
    def before_request():   # pylint: disable=unused-variable
        """
        Log and start timing request. Extract or generate trace id.
        """

        if request.method not in ['GET', 'POST', 'PUT']:
            return

        if 'TraceId' in request.headers:
            g.trace_id = request.headers['TraceId']
        else:
            g.trace_id = str(uuid.uuid1())
        g.start = time.time()
        logger.info('Request started, %s, %s',
                    request.full_path, body_str(request))

    @app.after_request
    def after_request(response):    # pylint: disable=unused-variable
        """
        Time and log response.
        """

        if request.method not in ['GET', 'POST', 'PUT']:
            return response

        if response.status_code >= 400:
            log_method = logger.error
        else:
            log_method = logger.info
        log_method('Request ended, took %d ms', int((time.time() - g.start) * 1000))
        logger.debug('Response body:\n%s', body_str(response))
        return response

    @app.errorhandler(Exception)
    def error_handler(ex):  # pylint: disable=unused-variable
        """
        Log and generate response for all unhandled exceptions.
        """

        exp_tb = traceback.format_exception(ex.__class__, ex, ex.__traceback__)
        msg = ' '.join(exp_tb).replace('\n', ' ')
        logger.error('Exception occurred: %s\n%s', ex, "".join(exp_tb))
        return (jsonify({'message': 'An unexpected error occurred', 'diagnostics': msg}),
                HTTPStatus.BAD_REQUEST)

    return app
