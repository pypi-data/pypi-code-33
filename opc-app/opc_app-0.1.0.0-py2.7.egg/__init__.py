import os
from flask import Flask, jsonify, g
from urllib import unquote
import OpenOPC
from mylogger import setup_logging
import logging

# local import
from instance.config import app_config


def create_app():
    env = os.environ.get('ENVIRONMENT')
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=os.path.join(
        app.instance_path, 'flaskr.sqlite'))

    app.config.from_object(app_config[env])
    app.config.from_pyfile('config.py')

    # setup python logging
    setup_logging(app.config['LOG_DIR'])

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def get_opc_conn():
        """gets a new opc client if there isn't one yet. Otherwise gets it from 'g'.
        """
        logger = logging.getLogger(__name__)
        if not hasattr(g, 'opc'):
            # create the opc client in DCOM mode (windows only)
            g.opc = OpenOPC.client()
            logger.info('created opc client')
        return g.opc

    @app.teardown_appcontext
    def close_opc_conn(error):
        """Closes the database again at the end of the request."""
        if hasattr(g, 'opc'):
            g.opc.close()

    @app.route('/', methods=['GET'])
    @app.route('/api', methods=['GET'])
    def api():
        """just say hello to the api.
        """
        response = jsonify({
            'message': 'opc http endpoint is alive'
        })
        response.status_code = 200
        return response

    @app.route('/api/sensor/<string:name>', methods=['GET'])
    def sensor(name):
        """fetch the values for the sensor.
        """
        opc = get_opc_conn()

        # connect to the server
        res = opc.connect(app.config['OPC_SERVER_NAME'])
        if not res:
            response = jsonify({
                'message': 'opc connection to server failed'
            })
            response.status_code = 500
            return response

        # read the requested value
        value, quality, time = opc.read(name)

        response = jsonify({
            'value': value,
            'quality': quality,
            'time': time
        })

        response.status_code = 200
        return response

    @app.route('/api/servers')
    def servers():
        """fetch the list of available servers to connect to.
        """
        opc = get_opc_conn()

        server_list = opc.servers()

        response = jsonify({
            'servers': server_list
        })
        response.status_code = 200

        return response

    @app.route('/api/nodes/<string:node>', methods=['GET'])
    def nodes(node):
        """fetch the values for the sensor.
        """
        # create the opc client in DCOM mode (windows only)
        opc = get_opc_conn()

        # connect to the server
        res = opc.connect(app.config['OPC_SERVER_NAME'])
        if not res:
            response = jsonify({
                'message': 'opc connection to server failed'
            })
            response.status_code = 500
            return response

        if node == 'all':
            node_list = opc.list()
        else:
            node_list = opc.list(node)

        response = jsonify({
            'nodes': node_list,
        })

        response.status_code = 200
        return response

    return app
