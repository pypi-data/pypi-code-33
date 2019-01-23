from reliabilly.components.chat.slack_client import SlackClient


class ChatClient:
    """ This class is intended to abstract away our chat tool. """
    def __init__(self, chat_client=SlackClient()):
        self.client = chat_client

    # pylint: disable=dangerous-default-value
    def send_room_message(self, room, message, attachments=dict()):
        return self.client.send_message(room, message, attachments=attachments)

    def send_user_message(self, email, message, attachments=dict()):
        return self.client.send_dm(email, message, attachments)

    # pylint: disable=dangerous-default-value
    def send_ephemeral_message(self, room, message, user):
        return self.client.send_ephemeral_message(room, message, user)

    # pylint: disable=dangerous-default-value
    def update_message(self, room, message, timestamp, attachments=dict()):
        return self.client.update_message(room, message, timestamp, attachments)

    def add_reaction(self, room, name, timestamp):
        return self.client.add_reaction(room, name, timestamp)
