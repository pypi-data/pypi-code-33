#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module: FoxyProxyREST - RESTful API with Flask
***

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs Ltd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Smart Arcs <support@smartarchitects.co.uk>, May 2018
"""
import datetime

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

import logging
import os
import string
import threading
import json
import random
import traceback
import eventlet
from eventlet import wsgi
from flask import Flask, jsonify, request, abort
from flask_sslify import SSLify
from flask_socketio import SocketIO, emit as ws_emit
from functools import wraps

from foxyproxy.client_thread import ClientThread

eventlet.monkey_patch(socket=True)

logger = logging.getLogger(__name__)

PAYLOAD_ENC_TYPE = 'AES-256-GCM-SHA256'


class AugmentedRequest(object):
    """
    Augmented request object with metadata
    """

    def __init__(self, req=None):
        self.req = req
        self.s = None  # session
        self.api_key = None
        self.ip = None
        self.last_results = None


class FoxyProxyREST(object):
    """
    Main server object
    """
    HTTP_PORT = 4443
    API_HEADER = 'X-Auth-API'

    def __init__(self, signer, downstream_port=0, key_folder=None):
        self.running = True
        self.run_thread = None
        self.stop_event = threading.Event()
        self.local_data = threading.local()

        self.use_websockets = True
        self.use_sse = True

        self.debug = False
        self.server = None
        self.config = None
        self.db = None

        self.flask = Flask(__name__)
        self.flask.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        self.socket_io = None

        if downstream_port == 0:
            self.port = FoxyProxyREST.HTTP_PORT
        else:
            self.port = downstream_port
        self.key_folder = key_folder
        self.signer = signer

    #
    # Management
    #
    def shutdown_server(self):
        """
        Shutdown flask server
        :return:
        """
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def terminating(self):
        """
        Set state to terminating
        :return:
        """
        self.running = False
        self.stop_event.set()

    def wsgi_options(self):
        """
        Returns kwargs for wsgi server
        :return:
        """
        kwargs = dict()
        return kwargs

    def init_server(self):
        """
        Initialize server
        :return:
        """
        self.flask.config['SECRET_KEY'] = FoxyProxyREST.random_alphanum(16)

        if self.use_websockets:
            self.socket_io = SocketIO(self.flask, async_mode='eventlet', policy_server=False,
                                      allow_upgrades=True, **self.wsgi_options())

            logger.info('SocketIO wrapper %s for Flask: %s' % (self.socket_io, self.flask))

    def work(self):
        """
        Main work method for the server - accepting incoming connections.
        :return:
        """
        logger.info('REST thread started %s %s %s dbg: %s'
                    % (os.getpid(), os.getppid(), threading.current_thread(), self.debug))
        try:
            self.init_server()
            self.init_rest()
            logging.info('RESTful API of FoxyProxy is up and running, listening on port %d' % self.port)

            if self.use_websockets:
                self.serve_websockets()
            elif self.debug:
                self.serve_werkzeug()
            else:
                self.serve_eventlet()

            logger.info('Terminating flask: %s' % self.flask)

        except Exception as e:
            logger.error('Exception: %s' % e)
            logger.error(traceback.format_exc())

        self.terminating()
        logger.info('Work loop terminated')

    def serve_werkzeug(self):
        """
        Developer local server, not for production use
        :return:
        """
        r = self.flask.run(debug=self.debug, port=self.HTTP_PORT, threaded=True)
        logger.info('Started werkzeug server: %s' % r)

    def serve_eventlet(self):
        """
        Eventlet server, fast async, for production use
        :return:
        """
        listener = eventlet.listen(('0.0.0.0', self.HTTP_PORT))
        logger.info('Starting Eventlet listener %s for Flask %s' % (listener, self.flask))
        wsgi.server(listener, self.flask, **self.wsgi_options())

    def serve_websockets(self):
        """
        Classical Flask application + websocket support, using eventlet
        :return:
        """
        logger.info('Starting socket_io')
        self.socket_io.run(app=self.flask, host='0.0.0.0', port=self.HTTP_PORT, **self.wsgi_options())

    def start(self):
        """
        Starts serving thread
        :return:
        """

        if self.key_folder:
            self.flask.run(
                os.path.join(self.key_folder, 'fullchain.pem'),
                os.path.join(self.key_folder, 'privkey.pem')
            )
            sslify = SSLify(self.flask)

        self.run_thread = threading.Thread(target=self.work, args=())
        self.run_thread.setDaemon(True)
        self.run_thread.start()

    #
    # REST interface
    #

    def init_rest(self):
        """
        Initializes rest server
        TODO: auth for dump, up, down - encrypt time token.
        :return:
        """

        @self.flask.route('/', methods=['GET'])
        def info():
            result = {
                'endpoints': [
                    '/api/v1.0/command (POST)',
                    '/api/v1.0/hello (POST, GET)',
                    '/api/v1.0/select (POST, GET)'
                    '/ws - web socket server'
                ]
            }
            return jsonify(result)

        @self.flask.route('/api/v1.0/command', methods=['POST'])
        def command():
            """
            EP handler for command
            :return:
            """
            request_in = FoxyProxyREST._process_payload(request, self.config)
            new_thread = ClientThread('rest', request_in, self.signer)
            new_thread.run()
            result = new_thread.get_response()  # use without threading
            return jsonify(result)

        @self.flask.route('/api/v1.0/select', methods=['GET'])
        def terminal():
            """
            The parameter is just one 'name' ...v1.0/terminal?name=xxxx . It returns a JSON with an ordered
            list of terminals
            :return:
            """
            terminal_name = None
            try:
                terminal_name = request.args.get('name')
            except:
                pass

            if (terminal_name is not None) and len(terminal_name) > 0:
                new_list = self.signer.prioritize(terminal_name)
                return jsonify(new_list)
            else:
                abort("Request has a missing parameter 'terminal'")

            # TODO add a list of selected readers for enumeration

        @self.flask.route('/api/v1.0/select', methods=['POST'])
        def terminal2():
            """
            Parameters of the post are: 'name'. It returns a JSON with an ordered
            list of terminals.
            :return:
            """
            request_in = FoxyProxyREST._process_payload(request, self.config)
            if ("terminal" in request_in) and (len(request_in['terminal']) > 0):
                new_list = self.signer.prioritize(request_in['terminal'])
                return jsonify(new_list)
            else:
                abort("Request has a missing parameter 'terminal'")

        @self.flask.route('/api/v1.0/hello', methods=['GET'])
        def hello():
            """
            Hello EP implementation
            :return:
            """
            return self.on_keep_alive()

        @self.flask.route('/api/v1.0/hello', methods=['POST'])
        def hello_post():
            """
             Hello POST EP implementation
            :return:
            """
            return self.on_keep_alive()

        @self.flask.errorhandler(400)
        def bad_request(e):
            """
             400 hander
            :param e:
            :return:
            """
            return jsonify(error=400, text=str(e)), 400

        @self.flask.errorhandler(405)
        def method_not_allowed(e):
            """
            405 handler
            :param e:
            :return:
            """
            return jsonify(error=405, text=str(e)), 405

        @self.flask.errorhandler(500)
        def internal_server_error(e):
            """
            500 handler
            :param e:
            :return:
            """
            return jsonify(error=500, text=str(e)), 500

        @self.flask.errorhandler(404)
        def url_not_found(e):
            """
            404 handler
            :param e:
            :return:
            """
            return jsonify(error=404, text=str(e)), 404

        @self.socket_io.on('message', namespace='/ws')
        def handle_message(message):
            """
            WS message handler
            :param message:
            :return:
            """
            logging.info('received ws message: ' + message)
            request_in = FoxyProxyREST._process_payload(message, self.config)
            thread_object = ClientThread(request_in)
            thread_object.run()  # use without threading
            result = thread_object.get_response()
            ws_emit('foxyproxy', jsonify(result))

        @self.socket_io.on('connect', namespace='/ws')
        def test_connect():
            """
            WS connect handler
            :return:
            """
            logger.info('WS client connected')

    def wrap_requests(*args0, **kwargs0):
        """
        Function decorator for requests call, wrapping in try-catch, catching exceptions
        :return:
        """

        def wrap_requests_decorator(*args):
            f = args[0]

            @wraps(f)
            def wrapper(*args, **kwds):
                # noinspection PyBroadException
                self = args[0]
                r = None
                try:
                    r = self._auth_request(kwds.get('request', None))
                    args = list(args)[1:]
                    res = f(self, r, *args, **kwds)
                    return res

                except Exception as e:
                    logger.error('Uncaught exception: %s' % e)
                    self.trace_logger.log(e)

                finally:
                    if r is not None:
                        FoxyProxyREST.silent_close(r.s)

                # fail
                abort(500)

            return wrapper

        return wrap_requests_decorator

    @staticmethod
    def silent_close(c, quiet=True):
        # noinspection PyBroadException
        """

        :param c:
        :param quiet:
        :return:
        """
        try:
            if c is not None:
                c.close()
        except Exception as e:
            if not quiet:
                logger.error('Close exception: %s' % e)
        pass

    @staticmethod
    def _process_payload(_request, config):
        """
        Decrypts payload, fails request in case of a problem
        :param _request:
        :return:
        """
        if not _request or not _request.json or 'data' not in _request.json:
            logger.warning('Invalid request')
            abort(400)

        data = _request.json['data']
        js = FoxyProxyREST.unprotect_payload(data, config)

        return js

    #
    # Handlers
    #
    @staticmethod
    def on_keep_alive(request=None):
        """
        Simple keepalive
        :param request:
        :return:
        """
        return jsonify({'result': True})

    @staticmethod
    def jsonify(obj):
        """
        Transforms object for transmission
        :param obj:
        :return:
        """
        if obj is None:
            return obj
        elif isinstance(obj, list):
            return [jsonify(x) for x in obj]
        elif isinstance(obj, dict):
            return {str(k): jsonify(obj[k]) for k in obj}
        elif isinstance(obj, datetime.datetime):
            return FoxyProxyREST.unix_time(obj)
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        else:
            return obj

    @staticmethod
    def unix_time(dt):
        """
        Get a unix_time regardless of the timezone
        :param dt:
        :return:
        """
        if dt is None:
            return None
        cur = datetime.datetime.utcfromtimestamp(0)
        if dt.tzinfo is not None:
            cur.replace(tzinfo=dt.tzinfo)
        else:
            cur.replace(tzinfo=None)
        # noinspection PyBroadException
        try:
            return (dt - cur).total_seconds()
        except Exception:
            pass

    @staticmethod
    def random_alphanum(length):
        """
        Generates a random password which consists of digits, lowercase and uppercase characters
        :param length:
        :return:
        """
        return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))

    @staticmethod
    def unprotect_payload(payload, config):
        """
        Processes protected request payload
        :param payload:
        :param config:
        :return:
        """
        if payload is None:
            raise ValueError('payload is None')
        if ('enctype' in payload) and (config is None):
            raise ValueError('encryption config is None')

        if 'enctype' in payload:
            if payload['enctype'] != PAYLOAD_ENC_TYPE:
                raise ValueError('Unknown payload protection: %s' % payload['enctype'])
            else:
                plaintext = ""
                # TODO encryption - probably not needed
                # key = make_key(config.vpnauth_enc_password)
                # iv = base64.b64decode(payload['iv'])
                # tag = base64.b64decode(payload['tag'])
                # ciphertext = base64.b64decode(payload['payload'])
                # plaintext = decrypt(key=key, iv=iv, ciphertext=ciphertext, tag=tag)
                js = json.loads(plaintext)
        else:
            js = payload

        return js
