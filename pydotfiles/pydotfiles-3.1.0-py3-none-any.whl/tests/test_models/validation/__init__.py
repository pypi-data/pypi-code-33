import json
import yaml
from pkg_resources import resource_stream


"""
Utility helpers
"""


def load_test_data(version, file_name):
    if file_name.endswith(".json"):
        return json.load(resource_stream(f"tests.resources.validator.{version}", file_name))
    elif file_name.endswith(".yaml") or file_name.endswith(".yml"):
        return yaml.load(resource_stream(f"tests.resources.validator.{version}", file_name))
