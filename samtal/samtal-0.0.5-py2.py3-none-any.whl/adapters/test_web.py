from samtal.adapters.conversation_web import WebConversation, WebContext
from samtal.core.conversation import Message, Sender
from samtal.core.test_bot import ConversationMock
from samtal.core.test_helpers import alexis, thomas


def test_should_compute_uniq_url_to_collect_answer():
    web_conversation = sample_web_conversation()
    answer_url = web_conversation.build_answering_url()
    assert sample_url() == answer_url


def test_send_message_should_use_conversation_sender():
    web_conversation = sample_web_conversation()
    web_conversation.send_message(Message("Un message."))
    expected_message = Message(f"Un message.\nTo reply, please click here {sample_url()}")
    assert [expected_message] == web_conversation.conversation_sender.read_last_messages()


def test_should_add_answer():
    conversation_id = "CONVERSATION_TO_THOMAS"
    web_conversation = sample_web_conversation(to=thomas())
    web_conversation.answer(Message("Yes", Sender.Other))


def samtal_azae_net():
    return WebContext(domain="samtal.azae.net", protocol="https")


def sample_web_conversation(to=alexis()):
    return WebConversation(to=to,
                           uuid_generator=static_uuid_generator,
                           web_context=samtal_azae_net(),
                           conversation_sender=ConversationMock)


def static_uuid_generator():
    return "CONVERSATION-TO-ALEXIS-UUID"


def sample_url():
    return "https://samtal.azae.net/conversation/CONVERSATION-TO-ALEXIS-UUID"
