from datetime import datetime, timedelta
from typing import List

from samtal.core.answer import Answer, AnswerRepository, LogLine
from samtal.core.bot import Bot, BotAction, SEND_QUESTION_TIMEDELTA, ConversationProvider
from samtal.core.conversation import Conversation, Message, Sender
from samtal.core.questions import Question
from samtal.core.team_members import Team, TeamMember
from samtal.core.test_helpers import thomas_dupond, sample_questions, question_review, question_pairing
from samtal.core.test_team_members import sample_members

TICKER_TIMEDELTA = timedelta(seconds=30)


class ConversationMock(Conversation):
    def read_last_messages(self):
        try:
            return [self.__last_message]
        except AttributeError:
            return []

    def send_message(self, message: Message):
        self.__last_message = message


class AnswerRepositoryMock(AnswerRepository):
    def __init__(self):
        self.__last_line = None

    def log(self, question, answer, team):
        log_line = LogLine(question, answer, team)
        self.__last_line = log_line

    def lastlog(self):
        return self.__last_line


class ConversationProviderMock(ConversationProvider):
    def open(self, team_member: TeamMember) -> Conversation:
        return ConversationMock(team_member)


class AnsweringConversationMock(Conversation):
    def __init__(self, to: TeamMember, answer_text: str):
        self.called = False
        self.answer_text = answer_text
        super().__init__(to)
        self.__last_messages: List[Message] = []

    def send_question(self, question: Question):
        if self.called:
            raise AssertionError('Too many questions sent')
        self.called = True
        super().send_question(question)
        self.send_message(Message(self.answer_text, Sender.Other))

    def read_last_messages(self) -> List[Message]:
        return self.__last_messages

    def send_message(self, message: Message):
        self.__last_messages.append(message)


class AnsweringConversationProviderMock(ConversationProvider):
    def __init__(self, answers=None):
        self.answers = answers or [Answer.Yes]
        self.call_nb = 0

    def open(self, team_member: TeamMember) -> Conversation:
        if self.call_nb >= len(self.answers):
            raise AssertionError('Too many conversations opened!')
        self.call_nb += 1
        answer_text = self.answers[self.call_nb - 1].value
        return AnsweringConversationMock(team_member, answer_text)


def test_i_should_answer():
    question = Question("devops", "code health", "code review", "Team review all code changes")

    repository, bot = bot_factory()

    bot.answer(question, Answer.Yes, Team("Teapot"))

    lastlog = repository.lastlog()
    assert lastlog.question == question
    assert lastlog.answer == Answer.Yes
    assert lastlog.team == Team("Teapot")


def test_should_ask_a_question():
    question = question_review()
    team_member = thomas_dupond()
    conversation_provider = ConversationProviderMock()
    bot = Bot(AnswerRepositoryMock(), conversation_provider, None, None)
    conversation = bot.ask(team_member, question)
    [message] = conversation.read_last_messages()
    assert message.text.startswith('Team review all code changes')
    assert message.text.endswith('("Yes", "Somehow" or "No")')
    assert conversation.to == team_member


def test_should_read_an_answer():
    question = question_review()
    answer_repository, bot = bot_factory()
    conversation = conversation_with_one_answer(question, answer="Yes")
    bot._add_conversation(conversation)
    bot.pull_answers()
    assert answer_repository.lastlog().answer == Answer.Yes
    assert answer_repository.lastlog().question == question
    assert answer_repository.lastlog().team == conversation.to.team
    assert not bot.is_speaking_to(conversation.to)


def bot_factory():
    answer_repository = AnswerRepositoryMock()
    return (answer_repository, Bot(answer_repository, None, None, None))


def test_should_read_another_answer():
    question = question_pairing()
    answer_repository, bot = bot_factory()
    conversation = conversation_with_one_answer(question, answer="No")
    bot._add_conversation(conversation)
    bot.pull_answers()
    assert answer_repository.lastlog().answer == Answer.No
    assert answer_repository.lastlog().question == question
    assert answer_repository.lastlog().team == conversation.to.team
    assert not bot.is_speaking_to(conversation.to)


def test_should_wait_an_answer():
    question = question_pairing()
    answer_repository, bot = bot_factory()
    conversation = conversation_without_answer(question)
    bot._add_conversation(conversation)
    bot.pull_answers()
    assert answer_repository.lastlog() is None
    assert bot.is_speaking_to(conversation.to)


def test_answer_ignore_case():
    messages = [
        Message.make_from_question(question_review()),
        Message("no", sender=Sender.Other)
    ]
    assert Answer.No == Bot._get_answer_from_messages(messages)


def test_answer_does_not_take_old_answer():
    messages = [
        Message.make_from_question(question_review()),
        Message("no", sender=Sender.Other),
        Message.make_from_question(question_pairing())
    ]
    assert Answer.NoAnswer == Bot._get_answer_from_messages(messages)


def test_should_find_answer_in_sentence():
    messages = [
        Message.make_from_question(question_review()),
        Message("no, it's stupid!", sender=Sender.Other)
    ]
    assert Answer.No == Bot._get_answer_from_messages(messages)


def test_should_run_the_bot_for_one_iteration():
    repository = AnswerRepositoryMock()
    bot = Bot(repository, AnsweringConversationProviderMock(), members=sample_members(), questions=sample_questions())
    bot.run(mock_ticker_factory(TICKER_TIMEDELTA / 2))
    assert repository.lastlog().answer == Answer.Yes
    assert bot.conversation_count() == 0


def test_should_run_the_bot_longer():
    repository = AnswerRepositoryMock()
    bot = Bot(repository, AnsweringConversationProviderMock(), members=sample_members(), questions=sample_questions())
    bot.run(mock_ticker_factory(SEND_QUESTION_TIMEDELTA - TICKER_TIMEDELTA / 2))
    assert repository.lastlog().answer == Answer.Yes
    assert bot.conversation_count() == 0


def test_should_run_the_bot_for_two_questions():
    repository = AnswerRepositoryMock()
    bot = Bot(repository, AnsweringConversationProviderMock([Answer.Yes, Answer.No]), members=sample_members(),
              questions=sample_questions())
    bot.run(mock_ticker_factory(SEND_QUESTION_TIMEDELTA + TICKER_TIMEDELTA))
    assert repository.lastlog().answer == Answer.No
    assert bot.conversation_count() == 0


def test_command_should_say_read_every_120_tick_otherwise_write():
    expected = [BotAction.ReadAndSend] + [BotAction.Read] * 119 + [BotAction.ReadAndSend]
    assert expected == list(Bot.get_actions(mock_ticker_factory(SEND_QUESTION_TIMEDELTA + TICKER_TIMEDELTA)()))


def conversation_with_one_answer(question: Question, answer: str) -> Conversation:
    conversation = conversation_without_answer(question)
    conversation.send_message(Message(answer, sender=Sender.Other))
    return conversation


def conversation_without_answer(question):
    conversation = ConversationMock(thomas_dupond())
    conversation.send_question(question)
    return conversation


def mock_ticker_factory(run_time: timedelta):
    def ticker():
        start = datetime.now()
        tick_time = start
        while True:
            yield tick_time
            tick_time += TICKER_TIMEDELTA
            if tick_time - start >= run_time:
                return

    return ticker
