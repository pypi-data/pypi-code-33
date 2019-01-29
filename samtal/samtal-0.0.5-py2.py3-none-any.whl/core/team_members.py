import random
from typing import List, Dict

from attr import dataclass
from yaml import load


@dataclass(frozen=True)
class Team:
    name: str


@dataclass(frozen=True)
class TeamMember:
    name: str
    team: Team
    mail: str
    mattermost: str

    @staticmethod
    def build(team: Team, name: str, member: Dict[str, str]) -> "TeamMember":
        mail = member['mail'] if member else ""
        mattermost = member['mattermost'] if member else ""
        return TeamMember(name=name, team=team, mail=mail, mattermost=mattermost)


class MembersRepository():
    pass


class Members:
    def __init__(self, members: List[TeamMember]):
        self.__members = members

    def __len__(self):
        return len(self.__members)

    def find_by_name(self, name: str) -> List[TeamMember]:
        found = []
        for team_member in self.__members:
            if team_member.name == name:
                found.append(team_member)
        return found

    def without(self, members: 'Members') -> 'Members':
        return Members(list(set(self.__members) - set(members.__members)))

    def pick(self, get_index=None):
        def get_random_question_index():
            return random.randint(0, len(self.__members) - 1)

        get_index = get_index or get_random_question_index
        index = get_index()

        return sorted(self.__members, key=lambda p: p.name)[index]


class YmlParser(MembersRepository):
    def __init__(self, yaml: str):
        self.__yaml = yaml

    def load(self) -> Members:
        content = load(self.__yaml)
        members_list = YmlParser.parse(content)
        return Members(members_list)

    @staticmethod
    def parse(content) -> List[TeamMember]:
        members: List[TeamMember] = []
        for team_name, team_members in content.items():
            members += YmlParser.extract_members(Team(team_name), team_members)
        return members

    @staticmethod
    def extract_members(team: Team, team_members: Dict[str, Dict[str, str]]) -> List[TeamMember]:
        return [TeamMember.build(team, name, member) for name, member in team_members.items()]
