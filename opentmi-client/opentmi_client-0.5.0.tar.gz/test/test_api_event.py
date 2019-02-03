import unittest
from opentmi_client.api import Event


class TestEvent(unittest.TestCase):
    def test_construct(self):
        event = Event()
        self.assertIsInstance(event, Event)
        self.assertEqual(event.data, {})

    def test_str(self):
        event = Event()
        event.eid = "iid"
        self.assertEqual(str(event), "iid")

    def test_properties(self):
        event = Event()
        event.msgid = 'ALLOCATED'
        self.assertEqual(event.msgid, 'ALLOCATED')
        event.traceid = "asd"
        self.assertEqual(event.traceid, "asd")
        event.msg = "abc"
        self.assertEqual(event.msg, "abc")
        event.tag = "taag"
        self.assertEqual(event.tag, "taag")
        event.duration = 123.0
        self.assertEqual(event.duration, 123.0)
        event.eid = "aid"
        self.assertEqual(event.eid, "aid")
        spare = {"a": 123}
        event.spare = spare
        self.assertEqual(event.spare, spare)
        self.assertDictEqual(event.data, {
            "msgid": "ALLOCATED",
            "traceid": "asd",
            "msg": "abc",
            "tag": "taag",
            "duration": 123.0,
            "id": "aid",
            "spare": spare,
        })

    def test_priority(self):
        event = Event()
        event.priority.facility = "testcase"
        self.assertEqual(event.priority.facility, "testcase")
        event.priority.level = "warning"
        self.assertEqual(event.priority.level, "warning")
        self.assertDictEqual(event.data, {
            "priority": {
                "facility": "testcase",
                "level": "warning"
            }
        })

    def test_ref(self):
        event = Event()
        event.ref.resource = "123"
        self.assertEqual(event.ref.resource, "123")
        event.ref.testcase = "tcs"
        self.assertEqual(event.ref.testcase, "tcs")
        event.ref.result = "res"
        self.assertEqual(event.ref.result, "res")
        self.assertDictEqual(event.data, {
            "ref": {
                "resource": "123",
                "testcase": "tcs",
                "result": "res"
            }
        })
