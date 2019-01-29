import json
import unittest

import pytest

from oc_wrapper.model.RoleBinding import RoleRef, Subject


class TestRoleRef(unittest.TestCase):
    def test_role_ref(self):
        d = json.loads("""
{
     "roleRef": {
                "name": "admin"
            }
}""")

        rf = RoleRef(d.get("roleRef"))
        assert rf.name == 'admin'


class TestSubject(unittest.TestCase):
    def test_subject(self):
        d = json.loads("""
{
    "kind": "Group",
    "name": "Developers"
}""")

        s = Subject(d)
        assert s.kind == 'Group'
        assert s.name == 'Developers'

    def test_from_list(self):
        d = json.loads("""
{
    "subjects": [
                {
                    "kind": "Group",
                    "name": "Developers"
                }
            ]
}""")

        subjects = Subject.from_dist_list(d.get("subjects"))
        assert len(subjects) == 1
        assert subjects[0].kind == 'Group'
        assert subjects[0].name == 'Developers'


if __name__ == '__main__':
    pytest.main()
