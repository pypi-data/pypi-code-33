from dataclasses import dataclass
from typing import List, Type

from samtal.core.conversation import Conversation, Message
from samtal.core.team_members import TeamMember


@dataclass(frozen=True)
class WebContext():
    protocol: str
    domain: str


class WebConversation(Conversation):
    def __init__(self, to: TeamMember, uuid_generator, web_context: WebContext,
                 conversation_sender: Type[Conversation]):
        super().__init__(to)
        self.__conversation_sender = conversation_sender(to=to)
        self.__domain = web_context.domain
        self.__protocol = web_context.protocol
        self.__uuid_generator = uuid_generator

    def send_message(self, message: Message):
        new_message = Message(f"{message.text}\nTo reply, please click here {self.build_answering_url()}")
        self.__conversation_sender.send_message(new_message)

    def read_last_messages(self) -> List[Message]:
        pass

    def build_answering_url(self):
        return f"{self.__protocol}://{self.__domain}/conversation/{self.__uuid_generator()}"

    @property
    def conversation_sender(self):
        return self.__conversation_sender

    def answer(self, message: Message):
        pass
