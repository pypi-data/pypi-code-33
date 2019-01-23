"""GraphQL client for IOExplorer API.

"""
import re
import os
import json

from functools import partial

import pkg_resources
import snug
import quiz

_ = quiz.SELECTOR

URL = os.environ.get("IOEXPLORER_GRAPHQL_URL", "")
_SCHEMA_PATH = pkg_resources.resource_filename("ioapi", "schema.json")


def auth_factory(auth):
    """
    Create a credential object to authenticate user of the API.

    """
    if isinstance(auth, str):
        return snug.header_adder({"Authorization": "bearer {auth}"})
    assert isinstance(auth, tuple)
    return auth


class SequelizeJSON(quiz.Scalar):  # pylint: disable=too-few-public-methods
    """A JSON string"""

    def __init__(self, data):
        super().__init__()
        self.data = data

    def __gql_dump__(self):
        return re.sub(r'("([^\"]+?)")\s*:', r"\2:", json.dumps(self.data))

    @classmethod
    def __gql_load__(cls, data):
        return data


def execute(obj, auth=(), url=URL, **kwargs):
    "Execute a query."
    return quiz.execute(obj, auth=auth_factory(auth), url=url, **kwargs)


# pylint: disable=invalid-name
schema = quiz.Schema.from_path(_SCHEMA_PATH, module=__name__, scalars=[SequelizeJSON])
schema.populate_module()
query = schema.query
executor = partial(partial, execute)
# pylint: enable=invalid-name
