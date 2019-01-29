from samtal.core.questions import YmlParser, Question
from samtal.core.team_members import TeamMember, Team


def thomas_dupond():
    return TeamMember(name="Thomas Dupond",
                      team=system_team(),
                      mail="thomas.dupond@exemple.com",
                      mattermost="https://matermost.com/users/id-thomas")


def system_team():
    return Team("system team")


def sample_questions():
    yam_file = """
---
devops:
    code health:
        code review:
            - Team does pair programming
            - Team review all code changes
        Refactoring:
            - Team does refactoring
    Team work:
        Workshop:
            - All team members (dev + ops) attend workshops (kata...)
Agility:
    Organization:
        New joiner:
            - New joiner are validated directly by the team
"""
    questions = YmlParser(yam_file).load()
    return questions


def question_review():
    return Question("devops", "code health", "code review", "Team review all code changes")


def question_pairing():
    return Question("devops", "code health", "code review", "Team does pair programming")


def alexis():
    return TeamMember(name="Alexis Benoist",
                      team=Team("empty"),
                      mattermost="https://framateam.org/api/v4/users/g576161drfdujpcbahhsgezcky",
                      mail='')


def no_spam():
    return TeamMember(name="No Spam",
                      team=Team("empty"),
                      mattermost='',
                      mail='nospam@yopmail.com')


def thomas():
    return TeamMember(name="Thomas Clavier",
                      team=Team("Azaé"),
                      mattermost="",
                      mail='tclavier@azae.net')
