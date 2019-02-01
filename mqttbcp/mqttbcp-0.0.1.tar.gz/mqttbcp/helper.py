from functools import wraps
from typing import Set

from mqttbcp import Client


def extract_data(args):
    if not len(args) > 0:
        return
    data = args[-1]
    if not isinstance(data, dict):
        return
    return data


def extract_client_inst(args):
    if not len(args) > 0:
        return
    cl = args[0]
    if not isinstance(cl, Client):
        return
    return cl


def requires_keys(keys: Set[str]):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            data = extract_data(args)
            if not keys <= data.keys():
                return
            return f(*args, **kwargs)

        return wrapped

    return wrapper


def targets(clid: str):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            data = extract_data(args)
            if not {"id"} <= data.keys():
                return
            cl = extract_client_inst(args)
            cl_id = clid if clid else cl.client_id
            if not cl_id == data.get("id"):
                return
            return f(*args, **kwargs)

        return wrapped

    return wrapper


def register(cmd_id: str):
    def wrapper(f):
        Client.commands[cmd_id] = f

        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, *kwargs)

        return wrapped

    return wrapper
