# pylint: disable=invalid-name
import unittest
from unittest import skipUnless
from unittest.mock import MagicMock
from jira import JIRAError

from reliabilly.components.tools.task_management_client import TaskManagementClient
from reliabilly.settings import Constants, Settings


class TaskManagementClientTests(unittest.TestCase):

    def test_close_ticket(self):
        mock = MagicMock()
        client = TaskManagementClient(mock, mock, mock, mock)
        ticket_number = 'dummy'
        client.close_ticket(ticket_number)
        self.assertTrue(mock.transition_issue.called)

    def test_close_ticket_failure(self):
        mock = MagicMock()
        mock.transition_issue.side_effect = JIRAError
        client = TaskManagementClient(mock, mock, mock, mock)
        ticket_number = 'dummy'
        self.assertFalse(client.close_ticket(ticket_number))

    def test_set_awaiting_review(self):
        mock = MagicMock()
        client = TaskManagementClient(mock, mock, mock, mock)
        ticket_number = 'dummy'
        client.set_awaiting_review(ticket_number)
        self.assertTrue(mock.transition_issue.called)

    def test_set_awaiting_review_failure(self):
        mock = MagicMock()
        mock.transition_issue.side_effect = JIRAError
        client = TaskManagementClient(mock, mock, mock, mock)
        ticket_number = 'dummy'
        self.assertFalse(client.set_awaiting_review(ticket_number))

    def test_comment_issue(self):
        mock = MagicMock()
        client = TaskManagementClient(mock, mock, mock, mock)
        ticket_number = 'dummy'
        client.comment_issue(ticket_number, 'test message')
        self.assertTrue(mock.add_comment.called)

    def test_comment_issue_failure(self):
        mock = MagicMock()
        mock.add_comment.side_effect = JIRAError
        client = TaskManagementClient(mock, mock, mock, mock)
        ticket_number = 'dummy'
        self.assertFalse(client.comment_issue(ticket_number, 'test message'))

    def test_get_jira_summary(self):
        mock = MagicMock()
        mock.fields = mock
        mock.summary = 'a test summary'
        summary = TaskManagementClient.get_task_summary(mock)
        self.assertEqual(summary, 'a test summary')

    def test_get_jira_description(self):
        mock = MagicMock()
        mock.fields = mock
        mock.description = 'a test description'
        description = TaskManagementClient.get_task_description(mock)
        self.assertEqual(description, 'a test description')

    def test_get_issues_by_user(self):
        mock = MagicMock()
        mock.search_issues.return_value = [1, 2]
        client = TaskManagementClient(mock, mock, mock, mock)
        issues = client.get_issues_by_user('test_user')
        self.assertEqual(len(issues), 2)

    @skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
    def test_real_get_summary(self):
        client = TaskManagementClient('USERNAME', 'PASSWORD', Constants.TASK_MANAGEMENT_URL_DEFAULT)
        issues = client.get_issues_by_user('russell.tyrone.jones')
        self.assertEqual(len(issues), 1)
        client.comment_issue(issues[0], 'this is a test comment')
        self.assertEqual(client.get_task_summary(issues[0]), 'Put remaining functions in jenkinsfile into inv')
        client.set_awaiting_review('1470')
        client.close_ticket('1470')
