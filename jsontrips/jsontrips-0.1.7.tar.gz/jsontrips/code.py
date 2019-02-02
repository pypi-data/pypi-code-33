import os
import pkg_resources
import json

def get_file(name):
    return json.loads(pkg_resources.resource_string(__name__, os.path.join("data", name)).decode('utf-8'))
