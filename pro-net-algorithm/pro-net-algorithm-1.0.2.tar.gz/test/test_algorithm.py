import uuid
from unittest.mock import ANY

from pronet_algorithm.algorithm import Algorithm


class TestAlgorithm(object):
    """
    Test cases for pronet_algorithm.algorithm.AlgorithmTask
    """

    def _prepare_task_mock(self):
        class DummyTask(object):
            def error(self, message):
                pass

            def done(self, result):
                pass

            def update(self, message, progress, step):
                pass

        return DummyTask()

    def _prepare_algorithm(self, task=None):
        id = uuid.uuid4()
        d = {'numbers': [5, 6, 7], 'fast': True}
        a = Algorithm(d, task)
        return a

    def test_algorithm_init(self):
        a = self._prepare_algorithm()
        assert a._data == {'numbers': [5, 6, 7], 'fast': True}

    def test_algorithm_init_task(self):
        t = self._prepare_task_mock()
        a = self._prepare_algorithm(task=t)
        assert a._task == t

    def test_algorithm_error(self):
        a = self._prepare_algorithm()
        a.error('an error occurred')
        assert a.result() == 'an error occurred'

    def test_algorithm_error_task(self, mocker):
        t = self._prepare_task_mock()
        mock = mocker.patch.object(t, 'error')
        a = self._prepare_algorithm(task=t)
        a.error('an error occurred')
        mock.assert_called_once_with('an error occurred')

    def test_algorithm_done(self):
        a = self._prepare_algorithm()
        a.done({'foo': 'bar'})
        assert a.result() == {'foo': 'bar'}

    def test_algorithm_done_task(self, mocker):
        t = self._prepare_task_mock()
        mock = mocker.patch.object(t, 'done')
        a = self._prepare_algorithm(task=t)
        a.done({'foo': 'bar'})
        mock.assert_called_once_with({'foo': 'bar'})

    def test_algorithm_is_success(self):
        a = self._prepare_algorithm()
        a.done({'foo': 'bar'})
        assert a.is_success() is True

    def test_algorithm_is_success_error(self):
        a = self._prepare_algorithm()
        a.error('an error occurred')
        assert a.is_success() is False

    def test_algorithm_is_done(self):
        a = self._prepare_algorithm()
        a.done({'foo': 'bar'})
        assert a.is_done() is True

    def test_algorithm_is_done_error(self):
        a = self._prepare_algorithm()
        a.error('an error occurred')
        assert a.is_done() is True

    def test_algorithm_log(self, mocker):
        a = self._prepare_algorithm()
        mock = mocker.patch.object(a._logger, 'debug')
        a.log('a message')
        mock.assert_called_once_with('a message')

    def test_algorithm_log_task(self, mocker):
        t = self._prepare_task_mock()
        mock = mocker.patch.object(t, 'update')
        a = self._prepare_algorithm(task=t)
        a.log('a message')
        mock.assert_called_once_with('a message', ANY, ANY)

    def test_algorithm_step(self, mocker):
        a = self._prepare_algorithm()
        mock = mocker.patch.object(a._logger, 'info')
        a.step({'a': 'Step'})
        mock.assert_called_once_with("Step: {'a': 'Step'}")

    def test_algorithm_step_task(self, mocker):
        t = self._prepare_task_mock()
        mock = mocker.patch.object(t, 'update')
        a = self._prepare_algorithm(task=t)
        a.step({'a': 'Step'})
        mock.assert_called_once_with(ANY, ANY, {'a': 'Step'})

    def test_algorithm_progress(self, mocker):
        a = self._prepare_algorithm()
        mock = mocker.patch.object(a._logger, 'info')
        a.progress(1, 10)
        mock.assert_called_once_with("Progress: 1 of 10")

    def test_algorithm_progress_task(self, mocker):
        t = self._prepare_task_mock()
        mock = mocker.patch.object(t, 'update')
        a = self._prepare_algorithm(task=t)
        a.progress(1, 10)
        mock.assert_called_once_with(ANY, (1, 10), ANY)

    def test_algorithm_calc_max_progress(self):
        a = self._prepare_algorithm()
        a.calc_max_progress()
        assert a._current_progress == 0
        assert a._max_progress == 6

    def test_algorithm_do_progress(self):
        a = self._prepare_algorithm()
        a.calc_max_progress()
        a.do_progress()
        assert a._current_progress == 1
        a.do_progress()
        assert a._current_progress == 2

    def test_algorithm_process(self):
        a = self._prepare_algorithm()
        res = a.process()
        assert res == (5, 18)
