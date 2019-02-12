import uuid
import pytest
import queue

from pronet_registry.registry import (
    get_registry,
    _get_updates,
    _get_results,
    Registry)


class TestGetRegistry(object):
    """
    Test cases for pronet_registry.registry.get_registry
    """

    def test_get_registry(self):
        assert get_registry().__class__.__name__ is 'Registry'

    def test_get_registry(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 == r2


class DummyQueue(object):
    def put(self, data):
        pass

    def get(self, block=None, timeout=None):
        pass


class DummyWorker(object):
    def __init__(self, updates=[], next=[]):
        self._updates = updates
        self._next = next

    def updates(self):
        return self._updates

    def next(self):
        return self._next

    def run(self, task):
        pass


class DummyRegistry(object):
    _worker = DummyWorker()
    _tasks = {}
    _updates = {}


class DummyTask(object):
    def __init__(self, id=1):
        self._id = id
        self._running = True

    def update(self):
        pass

    def result(self):
        pass

    def state(self):
        pass

    def running(self):
        return self._running


class TestGetUpdates(object):
    """
    Test cases for pronet_registry.registry._get_updates
    """

    def _prepare_registry(self):
        reg = DummyRegistry()
        reg._worker = DummyWorker(updates=[(
            1,
            'This is an update!',
            None,
            None)])
        reg._tasks[1] = DummyTask()
        reg._updates[1] = DummyQueue()
        return reg

    def test_get_updates(self, mocker):
        reg = self._prepare_registry()
        mock_tasks = mocker.patch.object(reg._tasks[1], 'update')
        mock_updates = mocker.patch.object(reg._updates[1], 'put')
        _get_updates(reg)
        mock_tasks.assert_called_once_with(
            message='This is an update!',
            progress=None,
            step=None)
        mock_updates.assert_called_once_with((
            'This is an update!',
            None,
            None))


class TestGetResults(object):
    """
    Test cases for pronet_registry.registry._get_results
    """

    def _prepare_registry(self):
        reg = DummyRegistry()
        reg._worker = DummyWorker(next=[DummyTask(2)])
        # Add task with wrong id to be able to check if the
        # task was changed.
        reg._tasks[2] = DummyTask(1)
        return reg

    def test_get_updates(self, mocker):
        reg = self._prepare_registry()
        assert reg._tasks[2]._id == 1
        _get_results(reg)
        assert reg._tasks[2]._id == 2


class DummyAlgorithm(object):
    def execute(data, task):
        pass


class TestGetResults(object):
    """
    Test cases for pronet_registry.registry.Registry
    """

    def _prepare_registry(self):
        registry = Registry(worker=DummyWorker(), updates=False, results=False)
        return registry

    def test_create_static(self, mocker):
        registry = self._prepare_registry()
        mock = mocker.patch.object(registry._worker, 'run')
        id = registry.create_static(DummyAlgorithm(), data=None)
        assert id is not None
        assert id in registry._tasks
        assert id in registry._updates
        mock.assert_called_once_with(registry._tasks[id])

    def test_create(self, mocker):
        registry = self._prepare_registry()
        mock = mocker.patch.object(registry._worker, 'run')
        id = registry.create('algorithm_a', data=None)
        assert id is not None
        assert id in registry._tasks
        assert id in registry._updates
        mock.assert_called_once_with(registry._tasks[id])

    def test_result(self, mocker):
        registry = self._prepare_registry()
        # create a new task
        id = registry.create('algorithm_a', data=None)
        # and mock the result value of the new task
        registry._tasks[id].result = mocker.MagicMock(
            return_value='My task result.'
        )
        assert registry.result(id) == 'My task result.'

    def test_result_unknown_id(self):
        registry = self._prepare_registry()
        with pytest.raises(AttributeError):
            registry.result('unknown')

    def test_state(self, mocker):
        registry = self._prepare_registry()
        # create a new task
        id = registry.create('algorithm_a', data=None)
        # and mock the result value of the new task
        registry._tasks[id].state = mocker.MagicMock(
            return_value=('a', 'b', 'c')
        )
        assert registry.state(id) == ('a', 'b', 'c')

    def test_state_unknown_id(self):
        registry = self._prepare_registry()
        with pytest.raises(AttributeError):
            registry.state('unknown')

    def test_delete(self):
        registry = self._prepare_registry()
        id = registry.create('algorithm_a', data=None)
        registry.delete(id)
        assert id not in registry._tasks
        assert id not in registry._updates
        with pytest.raises(AttributeError):
            registry.state(id)
        with pytest.raises(AttributeError):
            registry.result(id)

    def test_watch(self, mocker):
        registry = Registry()
        id = registry.create('algorithm_a', data=[4, 5, 6])
        updates = [u for u in registry.watch(id, timeout=0.1)]
        assert len(updates) == 1
        assert updates[0] == ('Sum is 15', None, None)

    def test_watch_single(self, mocker):
        registry = Registry()
        id = registry.create('algorithm_a', data=[4, 5, 6])
        update = next(registry.watch(id, timeout=0.1))
        assert update == ('Sum is 15', None, None)
