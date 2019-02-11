import uuid
import pytest
from unittest.mock import call

from pronet_worker.worker import Worker, _runner


class DummyTask(object):
    def __init__(self, id=None):
        self._id = id

    def error(self, message):
        pass

    def run(self, message):
        raise Exception('an exception!')

    def set_update_queue(self, message):
        pass


class DummyQueue(object):
    def put(self, data):
        pass

    def get(self):
        pass

    def task_done(self):
        pass


class DummyPool(object):
    def terminate(self):
        pass

    def join(self):
        pass


def dummy_runner(tasks, results, updates, single_task=False):
    pass


class TestRunner(object):
    """
    Test cases for pronet_worker.worker._runner
    """

    def test_runner(self, mocker):
        task = DummyTask()
        set_update_mock = mocker.patch.object(task, 'set_update_queue')
        run_mock = mocker.patch.object(task, 'run')

        tasks = DummyQueue()
        tasks.get = mocker.MagicMock(return_value=task)
        done_mock = mocker.patch.object(tasks, 'task_done')

        update = DummyQueue()

        result = DummyQueue()
        result_mock = mocker.patch.object(result, 'put')

        _runner(tasks, result, update, single_task=True)

        # check set_update_queue
        calls = [call(update), call(None)]
        set_update_mock.assert_has_calls(calls)
        result_mock.assert_called_once_with(task)

        # assert run was called
        run_mock.assert_called_once()

        # assert tasks.task_done was called
        done_mock.assert_called_once()

        # check that task was added to the result queue
        result_mock.assert_called_once_with(task)

    def test_runner_error(self, mocker):
        task = DummyTask()
        error_mock = mocker.patch.object(task, 'error')

        tasks = DummyQueue()
        tasks.get = mocker.MagicMock(return_value=task)
        done_mock = mocker.patch.object(tasks, 'task_done')

        update = DummyQueue()

        result = DummyQueue()
        result_mock = mocker.patch.object(result, 'put')

        _runner(tasks, result, update, single_task=True)

        # assert run was called
        error_mock.assert_called_once_with('Exception occurred!')

        # assert tasks.task_done was called
        done_mock.assert_called_once()

        # check that task was added to the result queue
        result_mock.assert_called_once_with(task)


class TestWorker(object):
    """
    Test cases for pronet_worker.worker.Worker.
    """

    def _prepare_worker(self):
        p = DummyPool()
        w = Worker(runner=dummy_runner, pool=p)
        return w, p

    def test_init(self):
        # use real worker and process pool
        w = Worker()
        assert w._run is True
        w.join()

    def test_run(self, mocker):
        w, _ = self._prepare_worker()
        mock = mocker.patch.object(w._queue, 'put')
        task = DummyTask()
        w.run(task)
        mock.assert_called_once_with(task)

    def test_add(self, mocker):
        w, _ = self._prepare_worker()
        mock = mocker.patch.object(w._queue, 'put')
        task1 = DummyTask()
        task2 = DummyTask()
        tasks = [task1, task2]
        w.add(tasks)
        calls = [call(task1), call(task2)]
        mock.assert_has_calls(calls)

    def test_results(self, mocker):
        w, _ = self._prepare_worker()
        task = DummyTask('my_id')
        w._results.put(task)
        # object is copied by multiprocessing queue,
        # == compare does not work
        assert len(w.results()) == 1
        assert w.results()[0]._id == 'my_id'

    def test_next(self):
        w, _ = self._prepare_worker()
        w._run = False
        task = DummyTask('my_id')
        w._results.put(task)
        for r in w.next():
            assert r._id == 'my_id'

    def test_updates(self):
        w, _ = self._prepare_worker()
        w._run = False
        w._updates.put('update')
        for u in w.updates():
            assert u == 'update'
