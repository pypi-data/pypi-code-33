import uuid
from logging import getLogger
from threading import Thread
from flask import Flask, request, jsonify, Response

from cone.server.ConeCore import ConeCore


def _create_app(cone_core):
    app = Flask("cone")
    app.logger.disabled = True
    getLogger("werkzeug").disabled = True

    @app.route("/")
    def index():
        return "cone server is running..."

    @app.route("/task", methods=["GET"])
    def task():
        return jsonify(cone_core.get_next_task())

    @app.route("/results/<string:id>", methods=["POST"])
    def result(id):
        result_data = request.get_json()
        cone_core.add_result(id, result_data)
        return Response(status=201)

    return app


class Server(ConeCore):

    def __init__(self, port=5000, host="0.0.0.0"):
        ConeCore.__init__(self)
        self.app = _create_app(self)
        self.port = port
        self.host = host

    def start(self):
        server_thread = Thread(target=self.app.run, kwargs={
            "host": self.host,
            "port": self.port,
            "debug": False
        })
        server_thread.daemon = True
        print("Starting cone server on {}:{}...".format(self.host, self.port))
        server_thread.start()
