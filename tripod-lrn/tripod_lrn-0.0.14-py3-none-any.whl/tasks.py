# -*- coding: utf-8 -*-
"""
module tasks.py
--------------------
Provides the Tripod command line functions.
"""
import sys
from invoke import task


@task(default=True)
def run(context):
    """
    Start the Server with Gunicorn
    """
    # lazy load app
    from tripod import app
    # call app.run
    app.run()


@task
def test(context, path=None, cov=None, ):
    """
    Application tests execution task.
    """

    params = ['-x', '-s', '-vv', '--cov-report=term-missing',
              '--cov-report=html:static/coverage', '--ignore=env']
    if cov:
        params.append('--cov={}'.format(cov))

    if path is not None:
        params = [path] + params

    import pytest
    sys.exit(pytest.main(params))
