import random

from samtal.core.questions import Question
from samtal.core.test_helpers import sample_questions, question_review


def test_i_can_read_all_questions():
    assert len(sample_questions()) == 5


def test_i_can_find_a_question():
    questions = sample_questions()
    found = questions.find("All team members (dev + ops) attend workshops (kata...)")
    expected = Question("devops", "Team work", "Workshop", "All team members (dev + ops) attend workshops (kata...)")
    assert found == expected


def test_i_can_find_a_other_question():
    questions = sample_questions()
    found = questions.find("Team review all code changes")
    expected = question_review()
    assert found == expected


def test_i_pick_a_random_question():
    questions = sample_questions()
    expected = questions.find("New joiner are validated directly by the team")
    assert questions.pick(get_index=lambda: 1) == expected


def test_i_pick_a_random_question_with_a_fixed_random_seed():
    random.seed(5)
    questions = sample_questions()
    random_question = questions.pick()
    assert random_question is not None
    other_question = questions.pick()
    assert random_question != other_question


