# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from flask import Flask, abort, jsonify, \
    Response
from logging import getLogger, ERROR

class DMOTD(Flask):
    def __init__(self, path="/etc/motd"):
        super().__init__("dmotd_daemon")

        self.dmotd_path = path

        log = getLogger('werkzeug')
        log.disabled = True
        
        self.dmotd_routes()
    
    def dmotd_routes(self):
        @self.route("/raw", methods=["GET"])
        def raw():
            try:
                with open(self.dmotd_path, "r") as f:
                    contents = f.read()
            except FileNotFoundError:
                return Response("Error: not found.", mimetype="text/plain")

            return Response(contents, mimetype="text/plain")

        @self.route("/json", methods=["GET"])
        def json():
            try:
                with open(self.dmotd_path, "r") as f:
                    contents = f.read()
            except FileNotFoundError:
                return jsonify({
                    "ok": False,
                    "error-code": 404,
                    "error-desc": "Not Found."
                })

            return jsonify({
                "ok": True,
                "lines": contents
            })
