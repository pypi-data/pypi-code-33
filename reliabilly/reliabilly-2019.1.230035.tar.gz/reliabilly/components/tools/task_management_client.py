from jira import JIRA, JIRAError
from reliabilly.settings import Constants

PROJECT_NAME = 'reliabilly'


def get_default_task_client(user, token, baseurl=Constants.TASK_MANAGEMENT_URL_DEFAULT):
    client = None
    try:
        client = JIRA(baseurl, basic_auth=(user, token))
    except JIRAError as ex:
        print(ex)
        exit(False)

    return client


class TaskManagementClient:
    def __init__(self, user, token, url=Constants.TASK_MANAGEMENT_URL_DEFAULT, client=None):
        self.client = client
        if not self.client:
            self.client = get_default_task_client(user, token, url)

    def close_ticket(self, ticket_number):
        try:
            self.client.transition_issue(ticket_number, "121")
            return True
        except JIRAError:
            return False

    def set_awaiting_review(self, ticket_number):
        try:
            self.client.transition_issue(ticket_number, "101")
            return True
        except JIRAError:
            return False

    @staticmethod
    def get_task_summary(issue):
        summary = issue.fields.summary
        return summary

    @staticmethod
    def get_task_description(issue):
        description = issue.fields.description
        return description

    def comment_issue(self, issue, message):
        try:
            self.client.add_comment(issue, message)
            return True
        except JIRAError:
            return False

    def get_issues_by_user(self, user):
        jira_query = 'project={} and sprint in openSprints() '.format(PROJECT_NAME)
        jira_query += 'and status in ("In Progress")'
        jira_query += 'and assignee in ("' + user + '") '
        return self.client.search_issues(jira_query)
