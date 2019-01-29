from mattermostdriver import Driver

from samtal.core.bot import ConversationProvider
from samtal.core.conversation import Conversation, Message, Sender
from samtal.core.team_members import TeamMember


class MattermostConversation(Conversation):
    def __init__(self, to: TeamMember, host: str, login: str, password: str):
        super().__init__(to)
        self.driver = Driver({
            'url': host,
            'port': 443,
            'login_id': login,
            'password': password,
        })
        self.user_id = None

    def get_bot_id(self):
        self._login()
        return self.user_id

    def get_teammember_id(self):
        url = self.to.mattermost
        if url != '':
            return url.split('/')[-1]
        email = self.to.mail
        if email != '':
            return self.get_member_user_id_from_email()
        raise NotImplemented()

    def _create_channel(self):
        rv = self.driver.channels.create_direct_message_channel([self.get_bot_id(), self.get_teammember_id()])
        return rv['id']

    def send_message(self, message):
        self._login()
        channel_id = self._create_channel()
        self.driver.posts.create_post({'message': message.text, 'channel_id': channel_id})

    def _login(self):
        if self.user_id:
            return
        rv = self.driver.login()
        self.user_id = rv['id']

    @property
    def token(self):
        return self.driver.client.token

    def read_last_message(self):
        messages = self.read_last_messages()
        return messages[0]

    def read_last_messages(self):
        self._login()
        channel_id = self._create_channel()
        order, posts = self.get_posts_for_channel(channel_id)
        return [self.make_message(posts[id_]) for id_ in order]

    def make_message(self, post: dict) -> Message:
        is_bluepill = post['user_id'] == self.get_bot_id()
        sender = Sender.BluePill if is_bluepill else Sender.Other
        return Message(post['message'], sender)

    def get_posts_for_channel(self, channel_id):
        payload = self.driver.posts.get_posts_for_channel(channel_id)
        order = payload['order']
        posts = payload['posts']
        return order, posts

    @property
    def host(self):
        return self.driver.options['url']

    @property
    def login(self):
        return self.driver.options['login_id']

    @property
    def password(self):
        return self.driver.options['password']

    def get_member_user_id_from_email(self):
        self._login()
        user = self.driver.users.get_user_by_email(self.to.mail)
        return user['id']


class MattermostConversationProvider(ConversationProvider):
    def __init__(self, host: str, login: str, password: str):
        self.__host = host
        self.__login = login
        self.__password = password

    def open(self, team_member: TeamMember) -> Conversation:
        return MattermostConversation(team_member, host=self.__host, login=self.__login, password=self.__password)
