from datetime import datetime

from pony.orm import Database, Required, PrimaryKey, commit, db_session, desc

from samtal.core.answer import AnswerRepository, LogLine, Answer
from samtal.core.questions import Question
from samtal.core.team_members import Team


class SqlAnswerRepository(AnswerRepository):
    def init_db(self):
        self.db = Database()

        class LogLineEntity(self.db.Entity):
            id = PrimaryKey(int, auto=True)
            created_at = Required(datetime, default=datetime.now)
            question_text = Required(str)
            question_topic = Required(str)
            question_subtopic = Required(str)
            question_thematic = Required(str)
            team_name = Required(str)
            answer = Required(str)

            def parse_team(self) -> Team:
                return Team(self.team_name)

            def parse_question(self) -> Question:
                return Question(self.question_topic, self.question_subtopic,
                                self.question_thematic, self.question_text)

            def parse_answer(self) -> Answer:
                return Answer(self.answer)

            def parse_log_line(self) -> LogLine:
                question = self.parse_question()
                team = self.parse_team()
                answer = self.parse_answer()
                return LogLine(question, answer, team)

        self.LogLineEntity = LogLineEntity

    def __init__(self, provider: str, **kwargs):
        self.init_db()
        args_dict = {'create_db': True, **kwargs}
        self.db.bind(provider, **args_dict)
        self.db.generate_mapping(create_tables=True)

    def log(self, question, answer, team):
        with db_session:
            self.LogLineEntity(question_text=question.text, question_topic=question.topic,
                               question_subtopic=question.subtopic, question_thematic=question.thematic,
                               answer=answer.value,
                               team_name=team.name)
            commit()

    def lastlog(self) -> LogLine:
        with db_session:
            last_log_line = self.LogLineEntity.select().order_by(desc(self.LogLineEntity.created_at)).first()
            return last_log_line.parse_log_line()
