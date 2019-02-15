import json
import uuid
from unittest.mock import Mock, patch

from django.db.models import signals
from django.test import TestCase

from mbq.ranch.constants import TaskStatus
from mbq.ranch.controllers import persist_task, rerun_logged_task
from mbq.ranch.exceptions import TaskNotFound
from mbq.ranch.models import LoggedTask


class TaskManagementTests(TestCase):
    def setUp(self):
        signals.post_save.disconnect(sender=LoggedTask, dispatch_uid="logged_task_save")
        signals.post_delete.disconnect(
            sender=LoggedTask, dispatch_uid="logged_task_delete"
        )

    def test_persist_failed_task(self):
        LoggedTask.objects.all().delete()

        persist_task(
            "task_id",
            "queue_name",
            "task_name",
            [1, 2, 3],
            {"foo": 1, "bar": 2},
            "stacktrace",
            TaskStatus.FAILURE,
            uuid.uuid4(),
        )

        logged_task = LoggedTask.objects.filter(
            id="task_id",
            task_name="task_name",
            stacktrace="stacktrace",
            status=TaskStatus.FAILURE,
        ).first()

        self.assertIsNotNone(logged_task)
        self.assertEqual(json.loads(logged_task.args), [1, 2, 3])
        self.assertEqual(json.loads(logged_task.kwargs), {"foo": 1, "bar": 2})

    @patch("mbq.ranch.controllers.import_module")
    def test_rerun_task_with_params(self, module_import_mock):
        module_mock = Mock()
        module_import_mock.return_value = module_mock

        logged_task = persist_task(
            "task_id",
            "queue_name",
            "some.module.lookup.and.thefunction",
            ["a", "b"],
            {"fizz": "buzz"},
            "stacktrace",
            TaskStatus.FAILURE,
            uuid.uuid4(),
        )
        rerun_logged_task(logged_task)

        module_import_mock.assert_called_once_with("some.module.lookup.and")
        module_mock.thefunction.delay.assert_called_once_with("a", "b", fizz="buzz")
        self.assertFalse(LoggedTask.objects.filter(pk=logged_task.pk).exists())

    @patch("mbq.ranch.controllers.import_module")
    def test_rerun_task_with_no_params(self, module_import_mock):
        module_mock = Mock()
        module_import_mock.return_value = module_mock

        logged_task = persist_task(
            "task_id",
            "queue_name",
            "some.module.lookup.and.thefunction",
            [],
            {},
            "stacktrace",
            TaskStatus.FAILURE,
            uuid.uuid4(),
        )
        rerun_logged_task(logged_task)

        module_import_mock.assert_called_once_with("some.module.lookup.and")
        module_mock.thefunction.delay.assert_called_once_with()

        self.assertFalse(LoggedTask.objects.filter(pk=logged_task.pk).exists())

    @patch("mbq.ranch.controllers.import_module")
    def test_rerun_task_not_found(self, module_import_mock):
        module_mock = Mock()
        module_import_mock.return_value = module_mock

        del module_mock.somefunction

        logged_task = persist_task(
            "task_id",
            "queue_name",
            "somemodule.somefunction",
            ["a", "b"],
            {"fizz": "buzz"},
            "stacktrace",
            TaskStatus.FAILURE,
            uuid.uuid4(),
        )

        with self.assertRaises(TaskNotFound):
            rerun_logged_task(logged_task)
