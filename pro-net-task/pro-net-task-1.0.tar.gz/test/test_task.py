import uuid
import pytest

from pronet_task.task import Task, State


class MyQueue(object):
    def put(self, data):
        pass


class TestTask(object):
    """
    Test cases for pronet_task.Task
    """

    def _prepare_task(self, mocker=None):
        class Algorithm():
            def execute(self, data, task=None):
                pass
        a = Algorithm()
        id = uuid.uuid4()
        d = [5, 6, 7]
        t = Task(id, algorithm=a, input=d)
        return t, a

    def test_task_id(self):
        id = uuid.uuid4()
        t = Task(id)
        assert t.id() == id

    def test_task_state(self):
        id = uuid.uuid4()
        t = Task(id, state=State.RUNNING)
        _, _, s = t.state()
        assert s == State.RUNNING

    def test_task_update(self):
        t, _ = self._prepare_task()
        t.update('a message', (1, 10), {
            'title': 'A step',
            'description': 'Doing something.'
            })
        message, progress, _ = t.state()
        assert message == 'a message'
        assert progress == (1, 10)
        assert len(t.steps()) == 1
        assert t.steps()[0] == {
            'title': 'A step',
            'description': 'Doing something.'
            }

    def test_task_steps(self):
        t, _ = self._prepare_task()
        step_a = {'title': 'Step 1'}
        step_b = {'title': 'Step 2'}
        t.update(step=step_a)
        t.update(step=step_b)
        # update with same step is ignored
        t.update(step=step_b)
        assert t.steps() == [step_a, step_b]

    def test_task_result(self):
        t, _ = self._prepare_task()
        assert t.result() is None
        t.done([1, 2])
        assert t.result() == [1, 2]

    def test_task_running(self):
        t, _ = self._prepare_task()
        assert t.running() is True
        t.run()
        assert t.running() is True
        t.done()
        assert t.running() is False

    def test_task_running_error(self):
        t, _ = self._prepare_task()
        assert t.running() is True
        t.error()
        assert t.running() is False

    def test_task_run(self, mocker):
        t, a = self._prepare_task()
        mock = mocker.patch.object(a, 'execute')
        t.run()
        mock.assert_called_once_with([5, 6, 7], t)

    def test_task_done(self):
        t, _ = self._prepare_task()
        t.done([1, 2])
        _, _, s = t.state()
        assert s == State.DONE
        assert t.result() == [1, 2]

    def test_task_error(self):
        t, _ = self._prepare_task()
        t.error('something failed')
        _, _, s = t.state()
        assert s == State.ERROR
        assert t.result() == 'something failed'

    def test_task_set_update_queue(self, mocker):
        t, _ = self._prepare_task()
        q = MyQueue()
        mock = mocker.patch.object(q, 'put', autospec=True)
        t.set_update_queue(q)
        assert t._update_queue == q
        t.update(message='a message')
        mock.assert_called_once_with((
            t.id(),
            'a message',
            None,
            None))
