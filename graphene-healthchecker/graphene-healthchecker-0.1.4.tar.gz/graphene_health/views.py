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
    fetch_connected_node_count,
)

app.config.update(dict(config))


def get_headblock():
    return get_headblocknum(app.config["witness_url"])


def get_connected_count():
    return fetch_connected_node_count(app.config["witness_url"])


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


clean_endpoint = app.config["witness_url"].split("@")[-1]
# Add prometheus wsgi middleware to route /metrics requests
BACKEND_HEADBLOCK_NUM = Gauge(
    "backend_headblock_number", "Backend Head Block Number", ["endpoint"]
)
BACKEND_CONNECTIONS_NUM = Gauge(
    "backend_num_connections", "Backend Connections in P2P network", ["endpoint"]
)
BACKEND_HEADBLOCK_NUM.labels(clean_endpoint).set_function(get_headblock)
BACKEND_CONNECTIONS_NUM.labels(clean_endpoint).set_function(get_connected_count)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
