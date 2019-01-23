import pytest
from clustaar.schemas.models import Video, Message
from tests.utils import MAPPER


@pytest.fixture
def video():
    return Video(url="http://example.com/")


@pytest.fixture
def message(video):
    return Message(text="hello",
                   attachments=[video])


@pytest.fixture
def data():
    return {
        "type": "message",
        "text": "hello",
        "attachments": [
            {
                "type": "video",
                "url": "http://example.com/"
            }
        ]
    }


class TestDump(object):
    def test_returns_a_dict(self, data, message):
        result = MAPPER.dump(message)
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "incoming_message")
        assert isinstance(result, Message)
        assert result.text == "hello"
        assert isinstance(result.attachments[0], Video)
