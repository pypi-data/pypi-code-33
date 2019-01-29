import functools
import os

import vcr

from samtal.adapters import conversation_mattermost
from samtal.adapters.conversation_mattermost import MattermostConversation, MattermostConversationProvider
from samtal.core.conversation import Message, Sender
from samtal.core.team_members import TeamMember, Team
from samtal.core.test_helpers import question_review, alexis, no_spam


def use_full_cassette(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            path = os.path.dirname(conversation_mattermost.__file__)
            with vcr.use_cassette(f'{path}/vcr_cassettes/{name}.yaml') as cass:
                func(*args, **kwargs)
                if not cass.rewound:
                    return
                assert cass.all_played

        return wrapper_repeat

    return decorator


@use_full_cassette('create_channel')
def test_should_create_a_channel():
    mattermost_conversation = get_mattermost_conversation()
    mattermost_conversation._login()
    channel_id = mattermost_conversation._create_channel()
    channel_id_expected = '93om3e6jf7bnfbr6qaetfyanke'
    assert channel_id_expected == channel_id
    assert channel_id_expected == mattermost_conversation._create_channel()


@use_full_cassette('create_channel_from_email')
def test_should_create_a_channel_from_email():
    mattermost_conversation = get_mattermost_conversation(to=no_spam())
    mattermost_conversation._login()
    channel_id = mattermost_conversation._create_channel()
    channel_id_expected = 'byc3bphgqfdtxbf3z67cqid7ec'
    assert channel_id_expected == channel_id
    assert channel_id_expected == mattermost_conversation._create_channel()


@use_full_cassette('send_message')
def test_should_send_a_message_on_an_existing_channel():
    mattermost_conversation = get_mattermost_conversation()
    mattermost_conversation.send_question(question_review())
    assert question_review() == mattermost_conversation.last_question


@use_full_cassette('read_messages')
def test_should_read_last_messages_on_an_existing_channel():
    mattermost_conversation = get_mattermost_conversation()
    other_message_expected = send_message_to_bluepill('Bonjour')
    messages_expected = [
        Message('Avant Avant dernier message'),
        Message('Avant dernier message'),
        Message('Dernier message'),
    ]
    for message_expected in messages_expected[::-1]:
        mattermost_conversation.send_message(message_expected)
    messages = mattermost_conversation.read_last_messages()
    assert messages_expected == messages[:3]
    assert other_message_expected == messages[3]


def send_message_to_bluepill(text: str) -> Message:
    mattermost_conversation_other = get_mattermost_conversation_other()
    mattermost_conversation_other.send_message(Message(text))
    return Message(text, Sender.Other)


@use_full_cassette('read_message')
def test_should_read_the_last_message_on_an_existing_channel():
    mattermost_conversation = get_mattermost_conversation()
    mattermost_conversation.send_message(Message('Dernier message'))
    message = mattermost_conversation.read_last_message()
    assert Message("Dernier message", Sender.BluePill) == message


@use_full_cassette('login')
def test_should_login():
    mattermost_conversation = get_mattermost_conversation()
    mattermost_conversation._login()
    assert mattermost_conversation.token is not None


@use_full_cassette('from_email')
def test_should_convert_email_to_mattermost_id():
    mattermost_conversation = get_mattermost_conversation(to=no_spam())
    mattermost_conversation._login()
    assert "1quctx9kij81dxu7fs4y8zrgfa" == mattermost_conversation.get_member_user_id_from_email()


def test_provider_should_create_mattermost_conversation():
    provider = MattermostConversationProvider(host="hostname", login="user", password="password")
    conversation = provider.open(alexis())
    assert isinstance(conversation, MattermostConversation)
    assert "hostname" == conversation.host
    assert "user" == conversation.login
    assert "password" == conversation.password


def get_mattermost_conversation(to=None):
    to_ = to or alexis()
    return MattermostConversation(to=to_, host="framateam.org", login="bluepill",
                                  password="jeeS8ohF0beixeiraire")


def get_mattermost_conversation_other():
    password = "4E92F557-A0D6-4077-A91C-695947D4DAEE"
    bluepill = TeamMember(name="bluepill",
                          team=Team("empty"),
                          mattermost="https://framateam.org/api/v4/users/zh9teaxhwjge8csqebpbbks1so",
                          mail='')
    return MattermostConversation(to=bluepill, host="framateam.org", login="alexis.benoist",
                                  password=password)
