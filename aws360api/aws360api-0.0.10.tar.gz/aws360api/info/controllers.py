#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import flask dependencies
from flask import Blueprint, request, jsonify, current_app as app

from aws360api import include_server_info

# Define a blueprint
info = Blueprint('info', __name__, url_prefix='/info')

# http://<hostname>/info endpoint
@info.route('', methods=['GET'])
def get_app_info():
    app.logger.debug("INFO")

    server_info = include_server_info()
    return jsonify(server_name=server_info['get_server_name'](),
                   git_revision=server_info['get_git_revision'](),
                   git_tag=server_info['get_git_tag']())
