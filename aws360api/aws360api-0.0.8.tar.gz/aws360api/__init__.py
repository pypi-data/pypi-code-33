#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import logging
import git

from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)

################################################################################
### Override with specific settings based on the FLASK_ENV env var
################################################################################

if "FLASK_ENV" in os.environ:
    if os.environ["FLASK_ENV"] == 'prod':
        app.config.from_object('aws360api.config.prod.ProductionConfig')
    else:
        app.config.from_object('aws360api.config.config.DevelopmentConfig')
else:
    app.config.from_object('aws360api.config.config.DevelopmentConfig')

################################################################################
### Extra Jinja Filters
################################################################################


# ################################################################################
# ### Code revision
# ################################################################################

git_repo = None
git_sha = None
git_ref = None

try:
    git_repo = git.Repo(search_parent_directories=True)
    git_sha = git_repo.head.object.hexsha[:7]
    git_ref = str(git_repo.head.reference) if git_repo.head else '-'
except Exception:
    pass

app.config['GIT_REVISION'] = git_sha
app.config['GIT_TAG'] = git_ref

################################################################################
### Backend Setup
################################################################################


################################################################################
# http://stackoverflow.com/questions/13809890/flask-context-processors-functions
################################################################################


@app.context_processor
def include_server_info():
    server_name, git_revision, git_tag = request.host.split(':')[0], app.config['GIT_REVISION'], app.config['GIT_TAG']

    def get_server_name():
        return server_name

    def get_git_revision():
        return git_revision

    def get_git_tag():
        return git_tag

    return dict(get_server_name=get_server_name,
                get_git_revision=get_git_revision,
                get_git_tag=get_git_tag)


################################################################################
# Blueprints registration
################################################################################

from aws360api.scrapper.controllers import scrapper
from aws360api.badger.controllers import badger
from aws360api.heartbeat.controllers import heartbeat
from aws360api.info.controllers import info

app.register_blueprint(badger)
app.register_blueprint(scrapper)
app.register_blueprint(heartbeat)
app.register_blueprint(info)


@app.route('/', methods=['GET'])
def index(error=None):
    return redirect(url_for('badger.index'))


################################################################################
# Global errors handling
################################################################################


if not app.config['DEBUG']:
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('error.html', error=str(error), code=500, ), 500

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error.html', error=str(error), code=404), 404

    @app.errorhandler(Exception)
    def exception_handler(error):
        return render_template('error.html', error=error)
