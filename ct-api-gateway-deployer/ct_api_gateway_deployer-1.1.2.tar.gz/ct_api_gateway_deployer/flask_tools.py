# -*- coding: utf-8 -*-
import importlib
import json

from flask import Blueprint, Flask
from flask_restful import Api as FlaskApi

from ct_api_gateway_deployer.src.common.utils import Utils


class FlaskTools:

    @staticmethod
    def add_resources(application: Flask, router_file_path: str) -> None:

        with open(router_file_path, 'r') as routes_file:
            data = json.load(routes_file)

        api_bp = Blueprint(data['blueprint']['name'], application.import_name)
        api = FlaskApi(api_bp)

        for resource in data['blueprint']['resources']:
            urls = []
            # Construct URLs
            for method in resource['methods']:
                urls.append(Utils.mount_flask_uri(method))

            # Create resource for URLS
            api.add_resource(
                getattr(importlib.import_module(
                    resource['flask']['resourceModule']),
                    resource['flask']['resourceClass']
                ),
                *urls,
                strict_slashes=resource['flask']['strictSlashes']
            )

        application.register_blueprint(api_bp, url_prefix=data['blueprint']['url_prefix'])
