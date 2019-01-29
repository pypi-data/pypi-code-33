from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from samtal.core.questions import Question
from samtal.core.team_members import TeamMember


class Sender(Enum):
    BluePill = auto()
    Other = auto()


@dataclass(frozen=True)
class Message:
    text: str
    sender: Sender = Sender.BluePill

    @staticmethod
    def make_from_question(question: Question) -> 'Message':
        return Message(text=f'{question.text} ("Yes", "Somehow" or "No")')

    @property
    def is_from_bluepill(self):
        return self.sender == Sender.BluePill


class Conversation(ABC):
    def __init__(self, to: TeamMember):
        self.to = to

    @abstractmethod
    def read_last_messages(self) -> List[Message]:
        pass

    @property
    def last_question(self) -> Question:
        return self.__last_question

    def send_question(self, question: Question):
        self.send_message(Message.make_from_question(question))
        self.__last_question = question

    @abstractmethod
    def send_message(self, message: Message):
        pass

