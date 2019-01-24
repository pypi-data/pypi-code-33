import requests
import datetime
from flask import jsonify


timeFormat = "%Y-%m-%dT%H:%M:%S"


def parse_time(block_time):
    # convert backend time into timestamp
    return datetime.datetime.strptime(block_time, timeFormat)


def format_time(datim):
    return datim.strftime(timeFormat)


def fetch_data(url):
    try:
        req = requests.post(
            url,
            json={
                "method": "call",
                "params": ["database", "get_objects", [["2.1.0"]]],
                "jsonrpc": "2.0",
                "id": 1,
            },
            timeout=2,
        )
    except Exception as e:
        raise Exception("Node timed out: {}".format(str(e)))

    if req.status_code != 200:
        raise Exception("Node returns an error core {}".format(req.status_code))

    try:
        data = req.json()
    except Exception as e:
        raise Exception("Invalid JSON format returned")

    if "result" not in data:
        raise Exception("Node does not return a result but {}".format(data))

    return data.get("result")[0]


def get_headblocknum(endpoint):
    try:
        data = fetch_data(endpoint)
        return int(data.get("head_block_number"))
    except:
        return 0


def run_backend_tests(data):
    tests = dict()

    # Test the current blockchain time
    time = parse_time(data["time"])
    tests[
        "current_headblock_in_sync"
    ] = time < datetime.datetime.utcnow() + datetime.timedelta(seconds=30)

    maintenance = parse_time(data["next_maintenance_time"])
    # Test the next maintenance interval
    tests[
        "next_maintenance_in_the_future"
    ] = maintenance > datetime.datetime.utcnow() - datetime.timedelta(seconds=10)

    return tests


def appendadditionadata(ret, data):
    ret["server_time"] = format_time(datetime.datetime.utcnow())
    ret["head_block_time"] = data.get("time")
    ret["deltatime"] = abs(
        parse_time(ret["head_block_time"]) - parse_time(ret["server_time"])
    ).total_seconds()
    return ret


def api_error(msg, data=None, tests=None):
    return (
        jsonify(
            appendadditionadata(dict(tests=tests, status="error", error=str(msg)), data)
        ),
        406,
    )


def api_success(data, tests):
    return (
        jsonify(appendadditionadata(dict(tests=tests, status="success"), data)),
        200,
    )
