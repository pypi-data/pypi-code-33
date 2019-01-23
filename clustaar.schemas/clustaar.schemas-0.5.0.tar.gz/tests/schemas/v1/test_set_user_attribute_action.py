from clustaar.schemas.v1 import SET_USER_ATTRIBUTE_ACTION
from clustaar.schemas.models import SetUserAttributeAction
import pytest


@pytest.fixture
def action():
    return SetUserAttributeAction(key="var1", value="val1")


@pytest.fixture
def data():
    return {
        "type": "set_user_attribute_action",
        "key": "var1",
        "value": "val1"
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = SET_USER_ATTRIBUTE_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SET_USER_ATTRIBUTE_ACTION)
        assert isinstance(action, SetUserAttributeAction)
        assert action.key == "var1"
        assert action.value == "val1"
