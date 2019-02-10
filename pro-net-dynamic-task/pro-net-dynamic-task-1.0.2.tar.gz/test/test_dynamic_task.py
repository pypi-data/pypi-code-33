import uuid

from pronet_dynamic_task.dynamic_task import DynamicTask


class TestDynamicTask(object):
    """
    Test cases for pronet_dynamic_task.dynamic_task.DynamicTask
    """

    def _prepare_task(self, lib='maximum_algorithm'):
        id = uuid.uuid4()
        d = [5, 6, 7]
        t = DynamicTask(id, algorithm=lib, input=d)
        return t

    def test_task_run(self):
        t = self._prepare_task()
        t.run()
        assert t.result() == 7

    def test_task_run_lib_unknown(self):
        t = self._prepare_task(lib='unknown')
        t.run()
        assert t.result() == 'Algorithm unknown not found!'

    def test_task_run_lib_error(self):
        t = self._prepare_task(lib='main')
        t.run()
        assert t.result() == 'Algorithm main not valid!'
