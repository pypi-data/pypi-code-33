from slackclient import SlackClient as SlackApi
from reliabilly.components.logger import _get_logger
from reliabilly.settings import Settings, Constants
from reliabilly.components.web.http_requestor import HttpRequestor


class SlackClient:
    def __init__(self, slack_client=SlackApi(Settings.SLACK_API_TOKEN), web_client=HttpRequestor()):
        self.client = slack_client
        self.web_client = web_client

    # pylint: disable=inconsistent-return-statements
    def get_user_id(self, email):
        email_search = Constants.USERS_EMAIL_QUERY + email
        headers = {Constants.AUTHORIZATION_HEADER: Constants.SHARED_AUTH_TOKEN}
        response = self.web_client.get(email_search, headers=headers)
        data = response.json()
        if data['total'] == 1:
            slack_account = data['users'][0]['slack']
            if slack_account:
                return slack_account['id']

    # pylint: disable=dangerous-default-value
    def send_message(self, channel, message, attachments=dict()):
        result = self.client.api_call(
            Constants.SLACK_POST_MESSAGE_TYPE, channel=channel, text=message, attachments=attachments)
        _get_logger(__name__).debug(result)
        return result.get('ts', result.get('error'))

    # pylint: disable=dangerous-default-value
    def update_message(self, channel, message, timestamp, attachments=dict()):
        result = self.client.api_call(
            Constants.SLACK_UPDATE_MESSAGE_TYPE, channel=channel, text=message, ts=timestamp, attachments=attachments)
        _get_logger(__name__).debug(result)
        return result.get('ts', result.get('error'))

    def send_ephemeral_message(self, channel, message, user):
        result = self.client.api_call(Constants.SLACK_EPHEMERAL_MESSAGE_TYPE, channel=channel, text=message, user=user)
        _get_logger(__name__).debug(result)
        return result.get('ts', result.get('error'))

    def add_reaction(self, channel, name, timestamp):
        result = self.client.api_call(
            Constants.SLACK_ADD_REACTION_TYPE, channel=channel, name=name, timestamp=timestamp)
        _get_logger(__name__).debug(result)
        return result.get('ok')

    # pylint: disable=dangerous-default-value
    def send_dm(self, email, message, attachments=dict()):
        user_id = self.get_user_id(email)
        return self.send_message(user_id, message, attachments)
