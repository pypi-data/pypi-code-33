from samtal.core.answer import Answer, LogLine
from samtal.adapters.answer_sqlite import SqlAnswerRepository
from samtal.core.test_helpers import system_team, question_review


def create_test_repository():
    return SqlAnswerRepository("sqlite", filename=":memory:")


def test_should_write_one_log_line_per_answer():
    answer_repository = create_test_repository()
    question = question_review()
    answer = Answer.Yes
    team = system_team()
    answer_repository.log(question, answer, team)

    assert LogLine(question, answer, team) == answer_repository.lastlog()


def test_should_read_last_log_line():
    answer_repository = create_test_repository()
    question = question_review()
    team = system_team()

    answer_repository.log(question, Answer.Yes, team)
    answer_repository.log(question, Answer.No, team)

    assert LogLine(question, Answer.No, team) == answer_repository.lastlog()
