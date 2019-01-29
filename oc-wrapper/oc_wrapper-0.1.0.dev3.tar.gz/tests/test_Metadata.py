import json
import unittest
from datetime import datetime

import pytest
import pytz

from oc_wrapper.model.Metadata import Metadata


class TestMetadata(unittest.TestCase):
    def test_metadata(self):
        d = json.loads("""
{
    "metadata": {
        "creationTimestamp": "2018-11-30T12:49:14Z",
        "name": "system:foo",
        "namespace": "foo-namespace",
        "resourceVersion": "64981186",
        "selfLink": "/apis/authorization.openshift.io/v1/namespaces/foo-namespace/rolebindings/system%3Afoo",
        "uid": "573b02b3-f49e-11e8-a146-066f131be090"
    }
}
""")

        m = Metadata(d.get("metadata"))
        assert m.creation_timestamp == datetime(2018, 11, 30, 12, 49, 14, 0, tzinfo=pytz.utc)
        assert m.name == 'system:foo'
        assert m.namespace == 'foo-namespace'
        assert m.resource_version == '64981186'
        assert m.self_link == '/apis/authorization.openshift.io/v1/namespaces/foo-namespace/rolebindings/system%3Afoo'
        assert m.uid == '573b02b3-f49e-11e8-a146-066f131be090'


if __name__ == '__main__':
    pytest.main()
