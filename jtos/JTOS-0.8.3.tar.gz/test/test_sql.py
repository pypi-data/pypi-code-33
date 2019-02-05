import pytest
from jtos import jtos


class TestJTOS:

    s_obj = {
        "select": {"tables": ["users"], "fields": ["email", "id", "password"]}
    }

    w_obj = {
        "where": [
            {"field": "email", "op": "l", "val": "t@test.com"},
            {"field": "name", "op": "e", "val": "test", "join": "a"},
            {"field": "id", "op": "e", "val": 3, "join": "o"}
        ]
    }

    sw_obj = {**s_obj, **w_obj}

    so_obj = {
        "select": {
            "tables": ["users"],
            "fields": ["email", "id", "password"],
            "orderBy": {"email": "ASC", "id": "desc"},
        }
    }

    jo_obj = {
        'join': {
            'type': 'left',
            'conditions': {
                'from': {
                    'table': 'activities',
                    'field': 'id'
                },
                'to': {
                    'table': 'users',
                    'field': 'id'
                }
            }
        }
    }

    de_obj = {
        "delete": {
            "table": "users",
        }
    }

    in_obj = {
        "insert": {
            "table": "users",
            "values": {
                "name": "test",
                "email": "address"
            }
        }
    }

    def test_creation(self):
        j = jtos.JTOS()
        assert j is not None

    def test_select_where(self):
        j = jtos.JTOS()
        stmt = j.parse_object(TestJTOS.sw_obj)
        print(stmt)
        assert (
            stmt
            == "SELECT email,id,password FROM users WHERE email LIKE 't@test.com' AND name = 'test' OR id = 3;"
        )

    def test_select_order(self):
        j = jtos.JTOS()
        stmt = j.parse_object(TestJTOS.so_obj)
        assert (
            stmt == "SELECT email,id,password FROM users ORDER BY email ASC, id DESC;"
        )
    
    def test_select_order_group(self):
        j = jtos.JTOS()
        sg = TestJTOS.so_obj
        sg['select']['groupBy'] = ['email', 'id']
        stmt = j.parse_object(sg)
        assert (
            stmt == "SELECT email,id,password FROM users GROUP BY email, id ORDER BY email ASC, id DESC;"
        )

    def test_insert(self):
        j = jtos.JTOS()
        stmt = j.build_insert(TestJTOS.in_obj['insert'])
        assert(stmt == "INSERT INTO users(name,email) VALUES('test','address')")

    def test_delete(self):
        j = jtos.JTOS()
        stmt = j.build_delete(TestJTOS.de_obj['delete'])
        assert(stmt == "DELETE FROM users")
        del_where = TestJTOS.de_obj
        del_where['where'] = TestJTOS.sw_obj['where']
        stmt = j.parse_object(del_where)
        assert stmt == "DELETE FROM users WHERE email LIKE 't@test.com' AND name = 'test' OR id = 3;"

    def test_join(self):
        j = jtos.JTOS()
        stmt = j.build_join(TestJTOS.jo_obj['join'])
        assert stmt == " left JOIN activities ON activities.id = users.id"

    def test_select(self):
        j = jtos.JTOS()
        stmt = j.parse_object(TestJTOS.s_obj)
        print(stmt)
        assert stmt == "SELECT email,id,password FROM users;"
