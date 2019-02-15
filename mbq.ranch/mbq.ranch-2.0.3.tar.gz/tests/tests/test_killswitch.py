from unittest.mock import Mock

from django.test import TestCase

from celery import Celery
from mbq import ranch


class TaskManagementTests(TestCase):
    def test_killswitch_on(self):
        celery_app = Celery(
            "ranch_test", task_cls=ranch.killswitch.create_task_class(lambda x, y: True)
        )
        mock_task_func = Mock()

        @celery_app.task()
        def test_task():
            mock_task_func()

        test_task()
        mock_task_func.assert_not_called()

    def test_killswitch_off(self):
        celery_app = Celery(
            "ranch_test",
            task_cls=ranch.killswitch.create_task_class(lambda x, y: False),
        )
        mock_task_func = Mock()

        @celery_app.task()
        def test_task():
            mock_task_func()

        test_task()
        mock_task_func.assert_called_once_with()

    def test_killswitch_name(self):
        celery_app = Celery(
            "ranch_test",
            task_cls=ranch.killswitch.create_task_class(lambda x, y: False),
        )

        @celery_app.task()
        def test_task():
            pass

        self.assertEqual(
            test_task.killswitch_name(),
            "task-killswitch-test-service-tests-tests-test-killswitch-test-task",
        )
