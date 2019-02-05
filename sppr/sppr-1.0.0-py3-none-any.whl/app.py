from flask import Flask, send_from_directory
import os
import requests

PACKAGE_DIR = os.environ.get('PACKAGE_DIR', '/packages')

def start():
    app = Flask(__name__)

    def a(path, dirname=''):
        full_path = os.path.join(dirname, path)
        return '<a href="/{1:}">{0:}</a>'.format(path, full_path)

    @app.route('/')
    def index():
        return '\n'.join([a(p.name) for p in os.scandir(PACKAGE_DIR)])

    @app.route('/<package>/')
    def package_versions(package):
        path = os.path.join(PACKAGE_DIR, os.path.basename(package))
        if not os.path.isdir(path):
            return requests.get('https://pypi.org/simple/{}/'.format(package)).content

        return '\n'.join([a(p.name, os.path.join(PACKAGE_DIR, package)) for p in os.scandir(path)])

    @app.route('/packages/<path:path>')
    def get_package(path):
        return send_from_directory(PACKAGE_DIR, path)

    return app
