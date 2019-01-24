from . import app
from flask import jsonify, request

from prometheus_client import Gauge
from prometheus_client import make_wsgi_app
from werkzeug.wsgi import DispatcherMiddleware

from .config import config
from .utils import (
    parse_time,
    format_time,
    fetch_data,
    run_backend_tests,
    appendadditionadata,
    api_error,
    api_success,
    get_headblocknum,
)

app.config.update(dict(config))


def get_headblock():
    return get_headblocknum(app.config["witness_url"])


@app.route("/")
def status():
    tests = None
    try:
        data = fetch_data(app.config["witness_url"])
    except Exception as e:
        return api_error(e)
    try:
        tests = run_backend_tests(data)
    except Exception as e:
        return api_error(e, data)

    if not all(tests.values()):
        return api_error("At least one test failed!", data, tests)

    return api_success(data, tests)


# Add prometheus wsgi middleware to route /metrics requests
BACKEND_HEADBLOCK_NUM = Gauge(
    "backend_headblock_number", "Backend Head Block Number", ["endpoint"]
)
BACKEND_HEADBLOCK_NUM.labels(app.config["witness_url"]).set_function(get_headblock)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
