"""Tests for rule.py"""
from .context import rpg
from rpg import enzyme
from rpg import rule


def test_rule():
    """Test class 'Rule'"""
    # Simple rule0
    index = 0
    letter = "D"
    cut = True
    pos = 0
    rule0 = rule.Rule(index, letter, cut, pos)

    # Test function '__repr__()'
    print_res = rule0.__repr__()
    assert print_res == "index=0\nletter=D\ncut=True\npos=0\n"

    # Simple rule1
    index = 2
    letter = "Q"
    cut = False
    pos = 1
    rule1 = rule.Rule(index, letter, cut, pos)
    print_res = rule1.__repr__()
    assert print_res == "index=2\nletter=Q\ncut=False\npos=1\n"

    # Simple rule2 identical to 1
    index = 0
    letter = "D"
    cut = True
    pos = 0
    rule2 = rule.Rule(index, letter, cut, pos)
    # Test function '__eq__()'
    assert rule0 == rule2

    # Complexe rule2
    rule2.rules.append(rule1)

    # Test __repr__
    print_res = rule2.__repr__()
    assert print_res == "index=0\nletter=D\ncut=True\npos=0\n\tindex=2"\
                        "\n\tletter=Q\n\tcut=False\n\tpos=1\n"

    # Test function '__ne__()'
    assert rule0 != rule2
    assert rule0 != False

    # Test function 'equ(other)'
    assert rule0.equ(rule2)  # primary rule identical

    # Test function 'contains(other)'
    assert rule2.contains(rule1)
    assert rule2.contains(rule0) == None

    # Test function 'contains(other)'
    assert rule2.contains_any_level(rule1)
    assert rule2.contains_any_level(rule0) == False

    # Test function 'get_header()'
    res = rule2.get_header()
    assert res == 'rule.Rule(0, "D", True, 0)'

    # Test function 'get_all_headers()'
    res = rule2.get_all_headers()
    assert res == ['rule.Rule(0, "D", True, 0)',
                   ['rule.Rule(2, "Q", False, 1)']]

    prev_name = ""
    prev_com = " # "
    # Test function 'format_a_rule(prev_name, prev_com)'
    res = rule2.format_a_rule(prev_name, prev_com)
    assert res == ['D_0', ' # Always cleaves before D, except...',
                   'D_0 = rule.Rule(0, "D", True, 0) # Always cleaves before D, '
                   'except...']
    res = rule1.format_a_rule(prev_name, prev_com)
    assert res == ['1Q2', ' # Never cleaves after Q, except...',
                   '1Q2 = rule.Rule(2, "Q", False, 1) # Never cleaves after Q, '
                   'except...']

    # Test function 'format_rule()'
    res = rule2.format_rule()
    assert res == 'D_0 = rule.Rule(0, "D", True, 0) # Always cleaves before D, ex'\
                  'cept...\nD_0Q2 = rule.Rule(2, "Q", False, 1) # Never cleaves b'\
                  'efore D, followed by Q, except...\nD_0.rules.append(D_0Q2)'\
                  '\nENZ.append(D_0)\n\n'

def test_check_rule():
    """Test function 'check_rule(exprule)'."""
    # Good
    expr = "(,A or B,)"
    res = rule.check_rule(expr)
    assert res == expr

    # No amino acid
    expr = "()"
    res = rule.check_rule(expr)
    assert res == ""
    expr = "(,)"
    res = rule.check_rule(expr)
    assert res == ""
    expr = "(,,)"
    res = rule.check_rule(expr)
    assert res == ""

    # Bad character
    not_allowed = ["!", "\"", "#", "$", "%", "&", "'", "*", "+", "-", "_", ".",
                   "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "^",
                   "`", "{", "|", "}", "~", "0", "1", "2", "3", "4", "5", "6",
                   "7", "8", "9"]
    for i in not_allowed:
        expr = "(,A or B" + i + ")"
        res = rule.check_rule(expr)
        assert res == ""

    # Space in expr
    expr = "(A,) "
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(,A )"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(, A)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "( ,A)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = " (A,)"
    res = rule.check_rule(expr)
    assert res == ""
    # OK
    expr = "(,A or B)"
    res = rule.check_rule(expr)
    assert res == expr

    # No UPPER letter after a letter
    expr = "(AB,)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(,aB)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(,A or Ba)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(,BA or B)"
    res = rule.check_rule(expr)
    assert res == ""
    # OK
    expr = "(,A or B)"
    res = rule.check_rule(expr)
    assert res == expr

    # Bracket verif
    expr = "B"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(B"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "B)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(A)(B"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(A(B)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(A))(B)"
    res = rule.check_rule(expr)
    assert res == ""
    # OK
    expr = "(A)(B,)(C)"
    res = rule.check_rule(expr)
    assert res == expr

    # Comma verif
    expr = "(A)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(,A,,)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(,A or ,B)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(,A)(,B)"
    res = rule.check_rule(expr)
    assert res == ""

    expr = "(,A)(B,)"
    res = rule.check_rule(expr)
    assert res == ""
    # OK
    expr = "(,A,)(B)"
    res = rule.check_rule(expr)
    assert res == expr

def test_split_complex_rule():
    """Test function 'split_complex_rule(rule)'."""
    # No 'or'
    a_rule = "(,A)"
    res = rule.split_complex_rule(a_rule)
    assert res == ["(,A)"]

    # One 'or'
    a_rule = "(A or B,)"
    res = rule.split_complex_rule(a_rule)
    assert res == ["(A,)", "(B,)"]

    # Several 'or'
    a_rule = "(,A or B or C or D,)"
    res = rule.split_complex_rule(a_rule)
    assert res == ["(,A,)", "(,B,)", "(,C,)", "(,D,)"]

def test_add_rule():
    """Test function 'add_rule(rules_list, rule)'."""
    rules_list = []
    # Add a basic rule that cut before 'A'
    rule1 = rule.Rule(0, "A", True, 0)
    rule.add_rule(rules_list, rule1)
    assert rules_list[0].index == 0
    assert rules_list[0].letter == "A"
    assert rules_list[0].cut is True
    assert rules_list[0].pos is 0
    assert len(rules_list) == 1
    assert rules_list[0] == rule1

    # Add a similar rule, it shouldn't be added
    rule2 = rule.Rule(0, "A", True, 0)
    rule.add_rule(rules_list, rule2)
    assert len(rules_list) == 1
    assert rules_list[0] == rule1

    # Add a similar rule, it shouldn't be added, but sub-rules yes
    rule3 = rule.Rule(0, "A", True, 0)
    rule3.rules.append(rule.Rule(2, "Z", False, 1))
    rule.add_rule(rules_list, rule3)
    assert len(rules_list) == 1

    # Add a rule that cut after 'B' and a sub-rule (except if Y after)
    rule4 = rule.Rule(0, "B", True, 1)
    rule4.rules.append(rule.Rule(2, "Y", False, 1))
    rule.add_rule(rules_list, rule4)
    assert len(rules_list) == 2
    assert rules_list[0] == rule1
    assert rules_list[1] == rule4
    assert len(rule4.rules) == 1
    # It doesn't change rule4.cut
    assert rule4.cut is True
    assert rules_list[1].rules[0].index == 2
    assert rules_list[1].rules[0].letter == "Y"
    assert rules_list[1].rules[0].cut is False
    assert rules_list[1].rules[0].pos == 1

    # Add a rule that DOESN'T cut after 'C'
    rule5 = rule.Rule(0, "C", False, True)
    # Add a sub-rule in rule5 that is cutting before 'A' (same as rule1)
    rule5.rules.append(rule.Rule(0, "A", True, 0))
    rule.add_rule(rules_list, rule5)
    # It is NOT recorded as the rule already exist
    assert len(rules_list) == 2
    # But it modify rule5.cut
    assert rule5.cut is True
    # And rule5 is added to rule1 sub-rules
    assert rules_list[0].rules[1].letter == "C"

    # create a complex rule containing B
    rule6 = rule.Rule(0, "D", True, 1)
    rule6.rules.append(rule.Rule(0, "E", True, 0))
    rule6.rules.append(rule.Rule(0, "F", False, 0))
    rule6.rules.append(rule.Rule(0, "B", True, 1))  # Existing rule
    rule6.rules.append(rule.Rule(0, "G", True, 0))
    rule.add_rule(rules_list, rule6)
    # It is NOT added
    assert len(rules_list) == 2
    # rule6.cut should have change
    assert rule6.cut is False
    # rule6 should have only 3 sub-rules, 'E', 'F' and 'G'
    assert len(rule6.rules) == 3
    # Those have been added to rule4
    assert rule4.rules[1].rules[0].letter == "E"
    assert rule4.rules[1].rules[1].letter == "F"
    assert rules_list[1].rules[1].rules[2].letter == "G" # Same as rule4

def test_create_rules():
    """Test function 'create_rules(all_rules)'."""
    all_rules = {}
    # Simplest rule
    # Cut before A

    rule1 = "(,A)"
    all_rules[rule1] = True
    # Truth for this rule
    truth1 = rule.Rule(0, "A", True, 0)
    res = rule.create_rules(all_rules)
    assert truth1 in res

    # More complex rule
    # Cut after B or C
    rule2 = "(B or C,)"
    all_rules[rule2] = True
    # Truth for rule2
    truth2_1 = rule.Rule(0, "B", True, 1)
    truth2_2 = rule.Rule(0, "C", True, 1)
    res = rule.create_rules(all_rules)
    assert truth1 in res
    assert truth2_1 in res
    assert truth2_2 in res
    assert len(res) == 3

    # Other complexe rule
    # Don't cleaves after E if there is a D before
    # But cleaves after E otherwise
    rule3 = "(E,)"
    all_rules[rule3] = True
    exc3 = "(D)(E,)"
    all_rules[exc3] = False
    # Truth for rule3
    truth3_1 = rule.Rule(-1, "D", False, -1)
    truth3 = rule.Rule(0, "E", True, 1)  # cleaves after E
    truth3.rules.append(truth3_1)
    res = rule.create_rules(all_rules)
    assert truth1 in res
    assert truth2_1 in res
    assert truth2_2 in res
    assert truth3 in res
    assert len(res) == 4

    # Similar complexe rule
    # Cleaves after G if there is a F before
    # But don't cleaves after G otherwise
    rule4 = "(F)(G,)"
    all_rules[rule4] = True
    # Truth for rule4
    truth4_1 = rule.Rule(-1, "F", True, -1)
    truth4 = rule.Rule(0, "G", False, 1)  # Don't cleaves after G
    truth4.rules.append(truth4_1)
    res = rule.create_rules(all_rules)
    assert truth1 in res
    assert truth2_1 in res
    assert truth2_2 in res
    assert truth3 in res
    assert truth4 in res
    assert len(res) == 5

    # Double comma
    rule5 = "(,H,)"
    all_rules[rule5] = True
    # Truth for rule5
    truth5_1 = rule.Rule(0, "H", True, 0)
    truth5_2 = rule.Rule(0, "H", True, 1)
    res = rule.create_rules(all_rules)
    assert truth5_1 in res
    assert truth5_2 in res
    assert len(res) == 7

    # Double comma and 'or'
    # Cleaves after I or J, except if a K is after, but cleaves if a L is before
    all_rules = {}
    rule6 = "(,I or J,)"
    all_rules[rule6] = True
    rule6_1 = "(,I or J,)(K)"
    all_rules[rule6_1] = False
    rule6_2 = "(L)(,I or J,)(K)"
    all_rules[rule6_2] = True
    # Truth for rule6
    truth6_1 = rule.Rule(0, "I", True, 0)
    truth6_2 = rule.Rule(0, "I", True, 1)
    truth6_3 = rule.Rule(0, "J", True, 0)
    truth6_4 = rule.Rule(0, "J", True, 1)
    truth6_5 = rule.Rule(1, "K", False, -1)
    truth6_6 = rule.Rule(-1, "L", True, -1)
    truth6_5.rules.append(truth6_6)
    truth6_4.rules.append(truth6_5)
    truth6_3.rules.append(truth6_5)
    truth6_2.rules.append(truth6_5)
    truth6_1.rules.append(truth6_5)
    res = rule.create_rules(all_rules)
    assert truth6_1 in res
    assert truth6_2 in res
    assert truth6_3 in res
    assert truth6_4 in res
    assert len(res) == 4

def test_handle_rule():
    """Test function 'handle_rule(seq, pos, a_rule, cut)'"""

    # We cut after E preceeded by D
    a_rule = {}
    rule_txt = "(D)(E,)"
    a_rule[rule_txt] = True
    all_rules = rule.create_rules(a_rule)
    seq = "ABCDEF"
    pos = 4
    cut = None  # Not needed here
    res = rule.handle_rule(seq, pos, all_rules[0], cut)
    assert res is True
    # We cut after E preceeded by D
    a_rule = {}
    rule_txt = "(D)(E,)"
    a_rule[rule_txt] = True
    all_rules = rule.create_rules(a_rule)
    seq = "ABCXEF"
    pos = 4
    cut = None  # Not needed here
    res = rule.handle_rule(seq, pos, all_rules[0], cut)
    assert res is None
    # We cut after E preceeded by D
    a_rule = {}
    rule_txt = "(D)(E,)"
    a_rule[rule_txt] = True
    all_rules = rule.create_rules(a_rule)
    seq = "ABCDEF"
    pos = 3  # Not E
    cut = None  # Not needed here
    res = rule.handle_rule(seq, pos, all_rules[0], cut)
    assert res is None

    # We cut after E NOT preceeded by D
    a_rule = {}
    rule_txt = "(E,)"
    a_rule[rule_txt] = True
    exc_txt = "(D)(E,)"
    a_rule[exc_txt] = False
    all_rules = rule.create_rules(a_rule)
    seq = "ABCXEF"
    pos = 4
    cut = None  # Not needed here
    res = rule.handle_rule(seq, pos, all_rules[0], cut)
    assert res is True

    # We cut after E NOT preceeded by D
    a_rule = {}
    rule_txt = "(E,)"
    a_rule[rule_txt] = True
    exc_txt = "(D)(E,)"
    a_rule[exc_txt] = False
    all_rules = rule.create_rules(a_rule)
    seq = "ABCDEF"
    pos = 4
    cut = None  # Not needed here
    res = rule.handle_rule(seq, pos, all_rules[0], cut)
    assert res is False
