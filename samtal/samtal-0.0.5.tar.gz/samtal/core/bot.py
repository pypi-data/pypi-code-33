import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Set, cast

from textblob import TextBlob

from samtal.core.answer import Answer, AnswerRepository
from samtal.core.conversation import Conversation, Message
from samtal.core.questions import Question, Questions
from samtal.core.team_members import Team, TeamMember, Members


class BotAction(Enum):
    Read = auto()
    ReadAndSend = auto()


SEND_QUESTION_TIMEDELTA = timedelta(hours=1)


class ConversationProvider(ABC):
    @abstractmethod
    def open(self, team_member: TeamMember) -> Conversation:
        pass


def infinite_ticker():
    while True:
        yield datetime.now()
        wait_time = SEND_QUESTION_TIMEDELTA / 4
        time.sleep(wait_time.seconds)


class Bot:
    def __init__(self, repository: AnswerRepository,
                 conversation_provider: ConversationProvider,
                 members: Members,
                 questions: Questions):
        self.__questions = questions
        self.__members = members
        self.__conversation_provider = cast(ConversationProvider, conversation_provider)
        self.__repository = repository
        self.__conversations: Set[Conversation] = set()

    def answer(self, question: Question, answer: Answer, team: Team):
        self.__repository.log(question, answer, team)

    def ask(self, team_member: TeamMember, question: Question) -> Conversation:
        conversation = self.__conversation_provider.open(team_member)
        conversation.send_question(question)
        self._add_conversation(conversation)
        return conversation

    def is_speaking_to(self, to: TeamMember):
        return any(to == member for member in self.members_conversing_with)

    def _add_conversation(self, conversation: Conversation):
        self.__conversations.add(conversation)

    def pull_answers(self):
        for conversation in self.__conversations:
            messages = conversation.read_last_messages()
            question = conversation.last_question
            answer = Bot._get_answer_from_messages(messages)
            if answer == Answer.NoAnswer:
                continue
            self.answer(question, answer, conversation.to.team)
            self.__conversations = self.__conversations - {conversation}

    @staticmethod
    def _get_answer_from_messages(messages: List[Message]) -> Answer:
        for message in reversed(messages):
            if message.is_from_bluepill:
                return Answer.NoAnswer
            for word in TextBlob(message.text).words:
                if word.lower() == 'yes':
                    return Answer.Yes
                if word.lower() == 'no':
                    return Answer.No
        return Answer.NoAnswer

    @staticmethod
    def get_actions(ticker):
        last_message_time = datetime.now() - timedelta(days=1)
        for tick in ticker:
            if tick - SEND_QUESTION_TIMEDELTA >= last_message_time:
                yield BotAction.ReadAndSend
                last_message_time = tick
            else:
                yield BotAction.Read

    def run(self, ticker):
        for action in Bot.get_actions(ticker()):
            if action == BotAction.ReadAndSend:
                member = self.get_member_with_no_conversation()
                question = self.__questions.pick()
                self.ask(member, question)
            self.pull_answers()

    @property
    def members_conversing_with(self):
        return [c.to for c in self.__conversations]

    def get_member_with_no_conversation(self):
        members = Members(self.members_conversing_with)
        no_speaking_to_members = self.__members.without(members)
        return no_speaking_to_members.pick()

    def conversation_count(self):
        return len(self.__conversations)
