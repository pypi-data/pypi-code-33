import os
from flask import Flask, jsonify, g
from urllib import unquote
import OpenOPC
from mylogger import setup_logging
import logging

# local import
import config



def create_app():
    # setup logging
    logger = logging.getLogger('opc_app.' + __name__)
    
    # Get the environment so we know what config to load
    env = os.environ.get('ENVIRONMENT')
    logger.debug('Using %s environment' % env)

    # Create the app
    app = Flask(__name__)

    # Load the config
    app.config.from_object(config.lookup[env])

    def get_opc_conn():
        """gets a new opc client if there isn't one yet. Otherwise gets it from 'g'.
        """
        if not hasattr(g, 'opc'):
            # create the opc client in DCOM mode (windows only)
            g.opc = OpenOPC.client()
            logger.info('Created opc client')
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
