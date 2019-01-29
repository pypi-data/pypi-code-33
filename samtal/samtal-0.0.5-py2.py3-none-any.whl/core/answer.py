from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

from samtal.core.questions import Question
from samtal.core.team_members import Team


class Answer(Enum):
    Yes = 'Yes'
    No = 'No'
    NoAnswer = auto()


@dataclass(frozen=True)
class LogLine:
    question: Question
    answer: Answer
    team: Team


class AnswerRepository(ABC):

    @abstractmethod
    def lastlog(self) -> LogLine:
        pass

    @abstractmethod
    def log(self, question: Question, answer: Answer, team: Team):
        pass
