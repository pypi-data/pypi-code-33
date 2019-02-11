from unittest.mock import patch
from datetime import datetime
from io import StringIO

from django.test import TestCase
from django.core.management import call_command

from dbcron.management.commands.crond import Command
from dbcron.tests.factories import JobFactory


class CrondRunJobTest(TestCase):
    def setUp(self):
        self.command = Command()

    @patch('crontab.CronTab.next', return_value=42)
    def test_not_now(self, mock):
        job = JobFactory.create()
        result = self.command.run_job(job)
        self.assertIsNone(result)

    @patch('crontab.CronTab.next', return_value=0)
    def test_run(self, mock):
        job = JobFactory.create()
        result = self.command.run_job(job)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, datetime)

    @patch('crontab.CronTab.next', side_effect=Exception)
    def test_run_with_error(self, mock):
        job = JobFactory.create()
        with self.assertRaises(Exception):
            self.command.run_job(job)


class CrondCommandTest(TestCase):
    def setUp(self):
        self.stdout = StringIO()

    @patch('dbcron.management.commands.crond.time.sleep')
    @patch('dbcron.management.commands.crond.Command.stop', side_effect=(False, True))
    def test_run(self, mock, mock_sleep):
        call_command('crond', stdout=self.stdout)
        self.assertEqual(mock.call_count, 2)
        self.stdout.seek(0)
        self.assertIn('Started', self.stdout.read())

    @patch('dbcron.management.commands.crond.time.sleep')
    @patch('dbcron.management.commands.crond.Command.run_job', return_value=True)
    @patch('dbcron.management.commands.crond.Command.stop', return_value=True)
    def test_filter_tag(self, mock_stop, mock_run_job, mock_sleep):
        JobFactory.create(tag='foo', is_active=True)
        call_command('crond', '--tags', 'foo', stdout=self.stdout)
        self.assertEqual(mock_run_job.call_count, 1)

    @patch('dbcron.management.commands.crond.time.sleep')
    @patch('dbcron.management.commands.crond.Command.run_job', return_value=True)
    @patch('dbcron.management.commands.crond.Command.stop', return_value=True)
    def test_filter_tag_has_no_job(self, mock_stop, mock_run_job, mock_sleep):
        JobFactory.create(tag='foo', is_active=True)
        call_command('crond', '--tags', 'bar', stdout=self.stdout)
        self.assertEqual(mock_run_job.call_count, 0)

    @patch('dbcron.management.commands.crond.time.sleep')
    @patch('dbcron.management.commands.crond.Command.run_job', return_value=True)
    @patch('dbcron.management.commands.crond.Command.stop', return_value=True)
    def test_filter_tags(self, mock_stop, mock_run_job, mock_sleep):
        JobFactory.create(tag='foo', is_active=True)
        JobFactory.create(tag='bar', is_active=True)
        JobFactory.create(tag='ham', is_active=True)
        call_command('crond', '--tags', 'foo', 'bar', stdout=self.stdout)
        self.assertEqual(mock_run_job.call_count, 2)

    @patch('dbcron.management.commands.crond.time.sleep')
    @patch('dbcron.management.commands.crond.Command.stop', return_value=True)
    def test_quiet(self, mock_stop, mock_sleep):
        call_command('crond', '--quiet', stdout=self.stdout)
        self.stdout.seek(0)
        self.assertFalse(self.stdout.read())

    @patch('dbcron.management.commands.crond.Command.main', side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt(self, mock_main):
        call_command('crond', stdout=self.stdout)
        self.stdout.seek(0)
        self.assertIn('Stopped', self.stdout.read())
