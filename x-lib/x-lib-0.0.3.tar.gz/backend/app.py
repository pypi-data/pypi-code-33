import codecs
import json
import os

from flask import Flask, g
from flask import request
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

from .consul import Consulate
from .exception import ValidationException, CoreException
from .logger import logging
from .response import JsonResponse

log = logging.getLogger(__name__)

DEFAULT_CONFIG = 'application'

# if not os.path.exists(DEFAULT_CONFIG):
# 	raise RuntimeError('please create config.json file in your project root folder')

db = SQLAlchemy()
consul = Consulate()
cache = Cache()
app = Flask(__name__)


def create_app(configure=None):
    if configure is None:
        configure = {'TEST': True}
    try:
        if os.getenv('flask_profiles_active', ''):
            print('Profile active is : ', os.getenv('flask_profiles_active', ''))
            json_file = open(DEFAULT_CONFIG + '_' + os.getenv('flask_profiles_active', '') + '.json', 'rb')
            reader = codecs.getreader('utf-8')
            config = json.load(reader(json_file))
            app.config.update(configure)
            json_file.close()
        else:
            print('Profile active is : ', os.getenv('flask_profiles_active', ''))
            json_file = open(DEFAULT_CONFIG + '.json', 'rb')
            reader = codecs.getreader('utf-8')
            config = json.load(reader(json_file))
            app.config.update(configure)
            json_file.close()
        print(config)
        consul.init_app(app)
        consul.load_config(namespace=config['namespace'])
        config.pop('namespace')
        consul.register(**config)
        print(app.config)
        cache.init_app(app, app.config)
        app.response_class = JsonResponse

        @app.errorhandler(Exception)
        def handle_error(error):
            log.error(error, exc_info=True)
            try:
                log.info('rollbacking transaction')
                db.session.rollback()
            except Exception as e:
                log.error(e, exc_info=True)

            msg = {'status': 'FAIL'}
            if type(error) is TypeError:
                msg['message'] = 'type.error'
            elif type(error) is ValidationException:
                msg['message'] = error.message
                if error.key is not None:
                    msg['key'] = error.key
                    pass
            elif type(error) is CoreException:
                msg['message'] = error.message
            else:
                message = [str(x) for x in error.args]
                msg['message'] = message
            return msg

        # @app.before_request
        # def return_cached():
        # 	if request.method == 'GET':
        # 		response = cache.get(cached_key())
        # 		if response:
        # 			log.info("Using cache for %s", request.path)
        # 			return response

        @app.after_request
        def session_commit(response):
            if request.method == 'GET' and type(response) == JsonResponse:
                try:
                    return response
                except Exception:
                    raise
            if app.config['TEST']:
                g.db.session.rollback()
            else:
                try:
                    g.db.session.commit()
                except Exception:
                    g.db.session.rollback()
                    raise
            return response
    except:
        log.info("Consulate is not running")
        pass
    return app

# def cached_key():
# 	path = request.path
# 	args = dict(request.args)
# 	if args:
# 		if 'access_token' in args:
# 			args.pop('access_token')
# 		return path + '?' + urlencode(args, encoding='utf-8', doseq=True)
# 	return path


# def run(**kwargs):
# 	if 'SERVER_PORT' in app.config:
# 		kwargs.update({'port': app.config['SERVER_PORT']})
# 	if 'SERVER_HOST' in app.config:
# 		kwargs.update({'host': app.config['SERVER_HOST']})
# 	else:
# 		kwargs.update({'host': '0.0.0.0'})
# 	app.run(**kwargs)
