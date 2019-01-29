import random

from samtal.core.team_members import YmlParser, TeamMember, Team
from samtal.core.test_helpers import thomas_dupond


def test_should_pick_a_team_member_to_send_question():
    members = sample_members()
    found = members.find_by_name("thibault")
    expected = TeamMember(name="thibault",
                          team=Team("cc open"),
                          mail="",
                          mattermost="")
    assert found[0] == expected


def test_should_pick_an_other_team_member_to_send_question():
    members = sample_members()
    found = members.find_by_name("Thomas Dupond")
    expected = thomas_dupond()
    assert found[0] == expected


def test_should_read_all_members():
    assert len(sample_members()) == 5


def test_i_pick_a_random_team_member():
    members = sample_members()
    expected = TeamMember(name="Pierre", team=Team("other team"), mail="", mattermost="")
    assert members.pick(get_index=lambda: 1) == expected


def test_i_pick_a_random_team_member_with_a_fixed_random_seed():
    random.seed(5)
    members = sample_members()
    random_team_member = members.pick()
    assert random_team_member is not None
    other_team_member = members.pick()
    assert random_team_member != other_team_member


def sample_members():
    yml_file = """
---
cc open:
    thibault:
        
system team:
    Thomas Dupond:
        mail: thomas.dupond@exemple.com
        mattermost: https://matermost.com/users/id-thomas

other team:
    Jean:
        mail: jean@exemple.com
        mattermost: https://framateam.org/api/v4/users/id-jean
    Pierre:
    Simon:
"""
    yml_parser = YmlParser(yml_file)
    peoples = yml_parser.load()
    return peoples
