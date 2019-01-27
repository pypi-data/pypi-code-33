#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import flask dependencies
from flask import Blueprint, request, jsonify, current_app as app

from datetime import datetime

# Define a blueprint
heartbeat = Blueprint('heatbeat', __name__, url_prefix='/heartbeat')

# http://<hostname>/heartbeat endpoint
@heartbeat.route('', methods=['GET'])
def check_heartbeat():
    app.logger.debug("HEARTBEAT")
    return jsonify(status="success",
                   msg="I am an healthy flask app",
                   time=str(datetime.now()))
