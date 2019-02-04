import inspect
import os
from random import randint
from uuid import uuid4

import pytest

from pyqalx.config import BotConfig
from pyqalx.core import QalxNoGUIDError
from pyqalx.core.entity import QalxEntity
from pyqalx.core.errors import QalxError, QalxAPIResponseError, QalxEntityNotFound, QalxMultipleEntityReturned, \
    QalxNoQueueFoundByName
from pyqalx.core.group import Group
from pyqalx.core.item import Item
from pyqalx.core.qalx import entity_by_string
from pyqalx.core.queue import Queue
from pyqalx.core.set import Set


@pytest.mark.parametrize("request_type", ['get', 'post', 'patch', 'delete'])
@pytest.mark.parametrize("endpoint", ['item', 'set', 'group', 'queue'])
def test_process_api_request(qalx, mocker, request_type, endpoint):
    mock_transport_function = mocker.patch("pyqalx.core.qalx.PyQalxAPI." + request_type)
    mock_transport_function.return_value = (True, {"guid": uuid4()})
    qalx._process_api_request(request_type, endpoint, thing="stuff")
    mock_transport_function.assert_called_once_with(endpoint, json={"meta": {},
                                                                    "thing": "stuff"})
    pass


def test_process_api_request_error(qalx):
    with pytest.raises(Exception):
        qalx._process_api_request("foo", "here", thing="stuff")


@pytest.mark.parametrize("request_type", ['get', 'post', 'patch', 'delete'])
@pytest.mark.parametrize("endpoint", ['item', 'set', 'group', 'queue'])
def test_process_api_request_non_json_error(qalx, mocker, request_type, endpoint):
    mock_transport_function = mocker.patch("pyqalx.core.qalx.PyQalxAPI." + request_type)
    mock_transport_function.return_value = (True, {"guid": uuid4()})
    with pytest.raises(QalxError):
        qalx._process_api_request(request_type, endpoint, thing=uuid4())


@pytest.mark.parametrize("request_type", ['get', 'post', 'patch', 'delete'])
@pytest.mark.parametrize("endpoint", ['item', 'set', 'group', 'queue'])
def test_process_api_request_http_error(qalx, mocker, request_type, endpoint):
    mock_transport_function = mocker.patch("pyqalx.core.qalx.PyQalxAPI." + request_type)
    mock_transport_function.return_value = (False, {"I'm a": "complete HTTP failure"})
    with pytest.raises(QalxAPIResponseError) as e:
        qalx._process_api_request(request_type, endpoint, thing="stuff")
        assert "I'm a: complete HTTP failure" in str(e)


def test_entity_by_string(mocker):
    class EntityA(QalxEntity):
        entity_type = "A"

    class EntityB(QalxEntity):
        entity_type = "B"

    class EntityCButNamedB(QalxEntity):
        entity_type = "B"

    mock_function = mocker.patch('pyqalx.core.qalx.getmembers')
    mock_function.return_value = [("EntityA", EntityA)]
    assert entity_by_string("A") == EntityA

    mock_function.return_value = []
    with pytest.raises(QalxEntityNotFound):
        entity_by_string("B")

    mock_function.return_value = [('EntityB', EntityB), ("EntityCButNamedB", EntityCButNamedB)]
    with pytest.raises(QalxMultipleEntityReturned):
        entity_by_string("B")


@pytest.mark.parametrize("endpoint", ['item', 'set', 'group', 'queue'])
def test_entities(endpoint):
    assert QalxEntity in inspect.getmro(entity_by_string(endpoint))


@pytest.mark.parametrize("entity_type", ['item', 'set', 'group', 'queue'])
def test_get_entity_by_guid(qalx, mocker, entity_type):
    guid = uuid4().hex
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    mocked_process_api_request.return_value = {"guid": guid}
    mocked_entity_by_string = mocker.patch("pyqalx.core.qalx.entity_by_string")
    mocked_entity_by_string.return_value = QalxEntity
    entity = qalx.get_entity_by_guid(entity_type, guid)
    assert entity['guid'] == guid
    endpoint = f"{entity_type}/{guid}"
    mocked_process_api_request.assert_called_with('get', endpoint)


@pytest.mark.parametrize("entity_type", ['item', 'set', 'group', 'queue'])
def test_archive_entity_by_guid(qalx, mocker, entity_type):
    guid = uuid4().hex
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    mocked_process_api_request.return_value = {"guid": guid, "info": {"archived": True}}
    mocked_entity_by_string = mocker.patch("pyqalx.core.qalx.entity_by_string")
    mocked_entity_by_string.return_value = QalxEntity
    entity = qalx.archive_entity_by_guid(entity_type, guid)
    assert entity['guid'] == guid
    endpoint = f"{entity_type}/{guid}/archive"
    mocked_process_api_request.assert_called_with('patch', endpoint)


@pytest.mark.parametrize("entity_type", ['item', 'set', 'group', 'queue'])
def test_save_entity(qalx, mocker, entity_type):
    Entity = entity_by_string(entity_type)
    guid = uuid4()
    entity_structure = {"guid": guid, "info": {"archived": False}, "data": {"thing": "stuff"}}
    entity = Entity({})
    with pytest.raises(QalxNoGUIDError):
        qalx.save_entity(entity)
    entity = Entity(entity_structure)
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    endpoint = f"{entity_type}/{guid}"
    mocked_process_api_request.return_value(entity_structure)
    qalx.save_entity(entity)
    mocked_process_api_request.assert_called_with('patch', endpoint, data=entity_structure['data'])


def test_add_item_data(qalx, mocker):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    guid = uuid4()
    item_structure = {"guid": guid, "info": {"archived": False}, "data": {"thing": "stuff"}}
    mocked_process_api_request.return_value = item_structure
    item1 = qalx.add_item_data(data=item_structure['data'])
    mocked_process_api_request.assert_called_with('post', 'item', data=item_structure['data'], meta=None)
    assert isinstance(item1, Item)
    meta = {"some": "meta data"}
    item2 = qalx.add_item_data(data=item_structure['data'], meta=meta)
    mocked_process_api_request.assert_called_with('post', 'item', data=item_structure['data'], meta=meta)
    assert isinstance(item2, Item)
    with pytest.raises(QalxError):
        qalx.add_item_data(data='data', meta=meta)


def test_add_item_file(qalx, mocker):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    guid = uuid4()
    item_structure = {"guid": guid, "info": {"archived": False}, "file": {"url": "s3://thefile"}}
    mocked_process_api_request.return_value = item_structure
    file_path = "/path/to/a/file"
    item1 = qalx.add_item_file(file_path=file_path)
    mocked_process_api_request.assert_called_with('post', 'item', file_path=file_path, data={}, meta=None)
    assert isinstance(item1, Item)


def test_get_item_file(qalx, mocker):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    guid = uuid4().hex
    item_structure = {"guid": guid, "info": {"archived": False},
                      "file": {"url": "s3://thefile", "filename": "some_file.extension"}}
    mocked_process_api_request.return_value = item_structure
    item1 = qalx.get_entity_by_guid('item', guid)
    mocked_process_api_request.assert_called_with('get', 'item/'+ guid)
    mocked_requests = mocker.patch('pyqalx.core.item.requests')
    assert isinstance(item1, Item)

    some_bytes = b'some bytes'
    mock_response = mocker.MagicMock()
    mocked_requests.get.return_value = mock_response
    mock_response.content = some_bytes
    mock_response.ok = True
    file_bytes = item1.read_file()
    mocked_requests.get.assert_called_with(url=item_structure['file']['url'])
    assert file_bytes == some_bytes
    fake_path = "/a/path/"
    mocked_open = mocker.mock_open()
    m = mocker.patch('pyqalx.core.item.open',mocked_open, create=True)
    item1.save_file(fake_path)
    full_fake_path = os.path.join(fake_path, item_structure['file']['filename'])
    mocked_open.assert_called_with(full_fake_path, 'wb')


def test_add_set(qalx, mocker):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    guid1 = uuid4().hex
    guid2 = uuid4().hex
    item1_structure = {"guid": guid1, "info": {"archived": False}, "data": {"thing": "stuff"}}
    item2_structure = {"guid": guid2, "info": {"archived": False}, "data": {"thing": "stuff"}}
    mocked_process_api_request.return_value = {"guid": uuid4(), "info": {"some": "info"}, "item_guids": [guid1, guid2]}
    set = qalx.add_set(items=[Item(item1_structure), Item(item2_structure)])
    mocked_process_api_request.assert_called_with('post', 'set', item_guids=[guid1, guid2], meta=None)
    assert isinstance(set, Set)


def test_add_group(qalx, mocker):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    guid1 = uuid4().hex
    guid2 = uuid4().hex
    set1_structure = {"guid": guid1, "info": {"archived": False}, "item_guids": ["item1", "item2"]}
    set2_structure = {"guid": guid2, "info": {"archived": False}, "item_guids": ["item3", "item4"]}
    mocked_process_api_request.return_value = {"guid": uuid4(), "info": {"some": "info"}, "set_guids": [guid1, guid2]}
    group = qalx.add_group(sets=[Set(set1_structure), Set(set2_structure)])
    mocked_process_api_request.assert_called_with('post', 'group', set_guids=[guid1, guid2], meta=None)
    assert isinstance(group, Group)


def test_add_queue(qalx, mocker):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    queue = qalx.add_queue("unittest queue", meta={"some": "stuff"})
    mocked_process_api_request.assert_called_with('post', 'queue', parameters=qalx._queue_params,
                                                  meta={"some": "stuff", "queue_name": "unittest queue"})
    assert isinstance(queue, Queue)
    queue = qalx.add_queue("unittest queue")
    mocked_process_api_request.assert_called_with('post', 'queue', parameters=qalx._queue_params,
                                                  meta={"queue_name": "unittest queue"})
    assert isinstance(queue, Queue)


@pytest.mark.parametrize("entity_type", ['item', 'set', 'group', 'queue'])
def test_list_entities(qalx, mocker, entity_type):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    params = dict(sort=None, skip=randint(0, 100), limit=randint(1, 500))
    entities = qalx.list_entities(entity_type, **params)
    mocked_process_api_request.assert_called_with("get", entity_type, **params)


def test_get_queue_messages(qalx, mocker):
    mock_queue = mocker.MagicMock()
    with pytest.raises(QalxError):
        qalx.get_queue_messages(mock_queue)


def test_get_queue_by_name(qalx, mocker):
    list_method = mocker.patch.object(qalx, 'list_entities')
    mock_queues = [mocker.MagicMock(), mocker.MagicMock()]
    list_method.return_value = mock_queues
    with pytest.raises(QalxMultipleEntityReturned):
        qalx.get_queue_by_name("unittest queue")

    queue = Queue({"guid": uuid4()})
    list_method.return_value = [queue]
    get_by_guid_method = mocker.patch.object(qalx, 'get_entity_by_guid')
    q = qalx.get_queue_by_name("unittest queue")
    get_by_guid_method.assert_called_with('queue', queue['guid'])


def test_get_or_create_queue(qalx, mocker):
    get_by_name_method = mocker.patch.object(qalx, 'get_queue_by_name')
    get_by_name_method.return_value = Queue({"meta": {"name": "unittest queue"}})
    q = qalx.get_or_create_queue("unittest queue")
    get_by_name_method.assert_called_with("unittest queue")
    assert isinstance(q, Queue)
    get_by_name_method = mocker.patch.object(qalx, 'get_queue_by_name')
    get_by_name_method.side_effect = QalxNoQueueFoundByName
    create_queue_method = mocker.patch.object(qalx, 'add_queue')
    q = qalx.get_or_create_queue("unittest new queue", meta={"some": "meta"})
    create_queue_method.assert_called_with("unittest new queue", {"some": "meta"})


def test_add_bot(qalx, mocker):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    conf = {"Some": "config"}
    bot_config = BotConfig(conf)
    bot = qalx.add_bot(bot_config)
    mocked_process_api_request.assert_called_with('post', 'bot', config=conf, host=qalx._host_info, meta=None)


def test_update_bot_status(qalx, mocker):
    mocked_process_api_request = mocker.patch('pyqalx.core.qalx.Qalx._process_api_request')
    bot = qalx.update_bot_status("1234", "unittest")
    mocked_process_api_request.assert_called_with('patch', 'bot/1234', status="unittest")
