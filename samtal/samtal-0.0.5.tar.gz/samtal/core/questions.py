import random
from abc import abstractmethod, ABC
from dataclasses import dataclass

from yaml import load


@dataclass(frozen=True)
class Question:
    topic: str
    subtopic: str
    thematic: str
    text: str


class Questions:

    def __init__(self, questions_list):
        self._questions = questions_list

    def find(self, question_text: str) -> Question:
        solutions = filter(lambda q: q.text == question_text, self._questions)
        return next(solutions)

    def __len__(self):
        return len(self._questions)

    def pick(self, get_index=None) -> Question:
        def get_random_question_index():
            return random.randint(0, len(self._questions) - 1)

        get_index = get_index or get_random_question_index
        index = get_index()
        return sorted(self._questions, key=lambda q: q.text)[index]


class QuestionsRepository(ABC):
    @abstractmethod
    def load(self) -> Questions:
        pass


class YmlParser(QuestionsRepository):
    def __init__(self, yaml: str):
        self.__yaml = yaml

    def load(self) -> Questions:
        content = load(self.__yaml)
        questions_list = YmlParser.parse(content)
        return Questions(questions_list)

    @staticmethod
    def parse(level_content, levels=None):
        levels = levels or []
        parse_content = []
        parse_sub_level = YmlParser._get_sub_level_parser(levels)
        for sub_level, sub_level_content in level_content.items():
            parse_content += parse_sub_level(sub_level_content, levels + [sub_level])
        return parse_content

    @staticmethod
    def _get_sub_level_parser(levels):
        if len(levels) < 2:
            parse_sub_level = YmlParser.parse
        else:
            parse_sub_level = YmlParser._extract_questions
        return parse_sub_level

    @staticmethod
    def _extract_questions(questions, levels):
        (topic, subtopic, thematic) = levels
        return [Question(topic, subtopic, thematic, question) for question in questions]
